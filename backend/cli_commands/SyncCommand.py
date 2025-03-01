import os
import logging
from django.core.files.storage import DefaultStorage
from restapi.serializer import TagSerializer
from .Command import Command
from .GenerateVideoCommand import generate_videos
from .AddFolderCommand import add_mission_from_folder
from .DeleteFolderCommand import delete_mission_from_folder
from restapi.models import Mission, Tag, File, Topic
import json
from mcap.reader import make_reader
from pathlib import Path
from django.core.files.base import ContentFile


# Create a custom logging handler to track if any log message was emitted
class LogTracker(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_occurred = False

    def emit(self, record):
        self.log_occurred = True


class SyncCommand(Command):
    name = "sync"

    def parser_setup(self, subparser):
        _ = subparser.add_parser(self.name, help="synchronize filesystem and database")

    def command(self, args):
        sync_folder()


storage = DefaultStorage()


def sync_files(mission_path, mission):
    """
    Syncs .mcap and metadata files:
    - Adds new files if they appear in the filesystem.
    - Removes files from the database if they are missing.
    """
    BASE_DIR = Path(__file__).resolve().parent.parent
    BASE_DIR = Path.joinpath(BASE_DIR, "media")
    existing_files = {file.file.name for file in File.objects.filter(mission=mission)}
    current_files = set()
    logging.info(f"Syncing files for mission {mission.name}.")
    # Find all .mcap and metadata files from the mission in the filesystem
    for folder in storage.listdir(mission_path)[0]:
        folder_path = os.path.join(mission_path, folder)
        typ = os.path.basename(folder_path)

        for subfolder in storage.listdir(folder_path)[0]:
            subfolder_path = os.path.join(folder_path, subfolder)
            mcap_path = None

            for item in storage.listdir(subfolder_path)[1]:
                item_path = os.path.join(subfolder_path, item)
                if item_path.endswith(".mcap"):
                    mcap_path = item_path
                    generate_videos(mcap_path)

            if mcap_path:
                current_files.add(mcap_path)  # Track found files
                metadata = extract_topics_from_mcap(mcap_path)
                # Add new found files to the database
                if mcap_path not in existing_files:
                    try:
                        size = storage.size(mcap_path)

                        duration = get_duration_from_mcap(mcap_path)
                        file = File(
                            robot=None,
                            duration=duration,
                            size=size,
                            file=mcap_path,
                            mission_id=mission.id,
                            type=typ,
                        )
                        file.save()
                        logging.info(
                            f"Added new file {mcap_path} for mission {mission.name}."
                        )
                    except Exception as e:
                        logging.error(f"Error processing {mcap_path}: {e}")
                else:
                    file = File.objects.get(file=mcap_path)
                # Get all video files in this folder
                videos_in_folder = {
                    video: os.path.join(subfolder_path, video)
                    for video in storage.listdir(subfolder_path)[1]
                    if video.endswith(".mp4")
                }
                logging.info(
                    f"Found {len(videos_in_folder)} video files in folder {subfolder_path}"
                )
                # Process each topic in the metadata
                for topic_name, topic_data in metadata.items():
                    # Try to find a corresponding video file
                    matching_video = videos_in_folder.get(
                        topic_name.replace("/", "-") + ".mp4", None
                    )

                    try:
                        # Create and save Topic **before** adding video
                        topic = Topic(
                            file=file,
                            name=topic_data["name"],
                            type=topic_data["type"],
                            message_count=topic_data["message_count"],
                            frequency=topic_data["frequency"],
                        )
                        topic.full_clean()
                        topic.save()
                        # Save the video file to the topic
                        if matching_video:
                            video_storage = Topic.video.field.storage
                            if video_storage.exists(matching_video):
                                topic.video = matching_video
                                topic.save()
                    except Exception as e:
                        logging.error(f"Error processing topic {topic_name}: {e}")

    # Remove files that are in DB but no longer in filesystem
    for file_path in existing_files - current_files:
        try:
            file = File.objects.get(file=file_path)
            file.delete()
            logging.info(f"Deleted missing file {file_path} from database.")
        except File.DoesNotExist:
            logging.warning(
                f"File {file_path} not found in database (already deleted)."
            )


def sync_folder():
    """
    Syncs all Missions from a folder:
    - Adds missions from folders in the filesystem that are not in the database.
    - Deletes missions from the database that are not in the filesystem.
    """
    # custom logger to track if any log message was emitted
    logger = logging.getLogger()
    log_tracker = LogTracker()
    logger.addHandler(log_tracker)

    # Get all existing missions in the database
    db_missions = Mission.objects.filter()
    db_mission_set = set(
        f"{mission.date.strftime('%Y.%m.%d')}_{mission.name}" for mission in db_missions
    )

    # Get all folder names in the filesystem
    fs_mission_set = set(storage.listdir("")[0])

    # Add missions for folders not yet in the database
    for folder in fs_mission_set - db_mission_set:
        add_mission_from_folder(folder, None, None)

    # Delete missions from the database not found in the filesystem
    for folder in db_mission_set - fs_mission_set:
        delete_mission_from_folder(folder)

    # find unused tags and delete them
    Tag.objects.filter(mission_tags=None).delete()

    # update db_missions after adding and deleting missions
    db_missions = Mission.objects.filter()

    # sync files for each mission
    for mission in db_missions:
        mission_path = f"{mission.date.strftime('%Y.%m.%d')}_{mission.name}"
        sync_files(mission_path, mission)

    # save metadata for each mission in the filesystem
    for mission in db_missions:
        # skip mission if nothing was modified
        if not mission.was_modified:
            continue
        # else save metadata
        Mission.objects.filter(id=mission.id).update(was_modified=False)
        tags = Tag.objects.filter(mission_tags__mission=mission)
        tag_serializer = TagSerializer(tags, many=True)
        mission_tags = [
            {"name": tag["name"], "color": tag["color"]} for tag in tag_serializer.data
        ]  # remove id field
        metadata = {
            "location": mission.location,
            "notes": mission.notes,
            "tags": mission_tags,
        }
        # save metadata to file inside mission folder
        metadata_file = f"{mission.date.strftime('%Y.%m.%d')}_{mission.name}/{mission.name}_metadata.json"
        with storage.open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=4)
            logging.info(
                f"Saved metadata for mission '{mission.name}' to the mission folder"
            )
    if not log_tracker.log_occurred:
        logging.info("Nothing was modified, no new metadata was saved")
    logger.removeHandler(log_tracker)


def extract_topics_from_mcap(mcap_path: str) -> dict[str:dict]:
    with storage.open(mcap_path, "rb") as f:
        reader = make_reader(f)
        schema_map = {
            schema.id: schema.name for schema in reader.get_summary().schemas.values()
        }
        channel_message_counts = reader.get_summary().statistics.channel_message_counts
        duration = get_duration_from_mcap(mcap_path)
        topic_info = {}
        for channel in reader.get_summary().channels.values():
            topic = channel.topic
            topic_type = schema_map.get(channel.schema_id, "Unknown")
            message_count = channel_message_counts.get(channel.id, 0)
            topic_info[topic] = {
                "name": topic,
                "type": topic_type,
                "message_count": message_count,
                "frequency": 0
                if duration == 0
                else message_count / (duration * 10**-9),
            }
        return topic_info


def get_duration_from_mcap(mcap_path: str) -> int:
    with storage.open(mcap_path, "rb") as f:
        reader = make_reader(f)
        statistics = reader.get_summary().statistics
        return statistics.message_end_time - statistics.message_start_time
