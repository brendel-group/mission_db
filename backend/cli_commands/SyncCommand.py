import logging
from django.core.files.storage import DefaultStorage
from .Command import Command
from .AddFolderCommand import add_mission_from_folder
from .DeleteFolderCommand import delete_mission_from_folder
from restapi.models import Mission, Mission_tags, Tag
import json


class SyncCommand(Command):
    name = "sync"

    def parser_setup(self, subparser):
        _ = subparser.add_parser(self.name, help="synchronize filesystem and database")

    def command(self, args):
        sync_folder()


storage = DefaultStorage()


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
        add_mission_from_folder(folder, None, None)

    # Delete missions from the database not found in the filesystem
    for folder in db_mission_set - fs_mission_set:
        delete_mission_from_folder(folder)

    # find unused tags and delete them
    Tag.objects.filter(mission_tags=None).delete()

    # save metadata for each mission in the filesystem
    for mission in db_missions:
        tags = Mission_tags.objects.filter(mission=mission)
        tag_data = []
        for mission_tag in tags:
            tag = Tag.objects.get(id=mission_tag.tag_id)
            tag_data.append({"name": tag.name, "color": tag.color})
        metadata = {
            "location": mission.location,
            "notes": mission.notes,
            "tags": tag_data,
        }
        # save metadata to file inside mission folder
        metadata_file = f"{mission.date.strftime('%Y.%m.%d')}_{mission.name}/{mission.name}_metadata.json"
        metadata_file_path = storage.path(metadata_file)
        with open(metadata_file_path, "w") as f:
            json.dump(metadata, f, indent=4)
            logging.info(
                f"Saved metadata for mission '{mission.name}' to '{metadata_file_path}'"
            )
