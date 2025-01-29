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


class SyncCommand(Command):
    name = "sync"

    def parser_setup(self, subparser):
        _ = subparser.add_parser(self.name, help="synchronize filesystem and database")

    def command(self, args):
        sync_folder()


storage = DefaultStorage()

def sync_mcap_files(mission_path, mission):
    """
    Iterates through folders to find .mcap and metadata files, then stores their details in the database.
    """
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
                try:
                    size = storage.size(mcap_path)
                    metadata = load_yaml_metadata(metadata_path)
                    duration = metadata.get("rosbag2_bagfile_information", {}).get("duration", {}).get("nanoseconds", 0) / 1e9
                    file = File(file=mcap_path, duration=duration, size=size)
                    file.save()
                    mission_file = Mission_files(mission=mission, file=file, type=typ)
                    mission_file.save()
                    logging.info(f"Stored file {mcap_path} for mission {mission.name}.")
                except Exception as e:
                    logging.error(f"Error processing {mcap_path}: {e}")

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

    # flag if any mission was modified
    modified_mission_found = False

    # save metadata for each mission in the filesystem
    for mission in db_missions:
        # skip mission if nothing was modified
        if not mission.was_modified:
            continue
        # else save metadata
        modified_mission_found = True
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
    if not modified_mission_found:
        logging.info("Nothing was modified, no new metadata was saved")
