import logging
import os
from django.core.files.storage import DefaultStorage
import yaml
from restapi.serializer import TagSerializer
from .Command import Command
from .AddFolderCommand import add_mission_from_folder
from .DeleteFolderCommand import delete_mission_from_folder
from restapi.models import File, Mission, Mission_files, Tag
import json

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

def sync_mcap_files(mission_path, mission):
    """
    Syncs .mcap and metadata files:
    - Adds new files if they appear in the filesystem.
    - Removes files from the database if they are missing.
    """

    existing_files = {mf.file.file for mf in Mission_files.objects.filter(mission=mission)}
    current_files = set()

    for folder in storage.listdir(mission_path)[0]:
        folder_path = os.path.join(mission_path, folder)
        typ = os.path.basename(folder_path)

        for subfolder in storage.listdir(folder_path)[0]:
            subfolder_path = os.path.join(folder_path, subfolder)
            mcap_path, metadata_path = None, None

            for item in storage.listdir(subfolder_path)[1]:
                item_path = os.path.join(subfolder_path, item)
                if item_path.endswith(".mcap"):
                    mcap_path = item_path
                elif item_path.endswith(".yaml"):
                    metadata_path = item_path

            if mcap_path and metadata_path:
                current_files.add(mcap_path)  # Track found files

                if mcap_path not in existing_files:  # New file found
                    try:
                        size = storage.size(mcap_path)
                        metadata = load_yaml_metadata(metadata_path)
                        duration = metadata.get("rosbag2_bagfile_information", {}).get("duration", {}).get("nanoseconds", 0) / 1e9
                        file = File(file=mcap_path, duration=duration, size=size)
                        file.save()
                        mission_file = Mission_files(mission=mission, file=file, type=typ)
                        mission_file.save()
                        logging.info(f"Added new file {mcap_path} for mission {mission.name}.")
                    except Exception as e:
                        logging.error(f"Error processing {mcap_path}: {e}")

    # Remove files that are in DB but no longer in filesystem
    for file_path in existing_files - current_files:
        try:
            file = File.objects.get(file=file_path)
            file.delete()
            logging.info(f"Deleted missing file {file_path} from database.")
        except File.DoesNotExist:
            logging.warning(f"File {file_path} not found in database (already deleted).")

def load_yaml_metadata(yaml_filepath):
    """Loads YAML metadata."""
    with storage.open(yaml_filepath, "r") as file:
        return yaml.safe_load(file)


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
        add_mission_from_folder(folder)

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
        sync_mcap_files(mission_path, mission)

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
        logging.info("No changes detected.")
    logger.removeHandler(log_tracker)
