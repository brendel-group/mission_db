from datetime import datetime
import logging
from django.core.files.storage import DefaultStorage
from .Command import Command
from .AddFolderCommand import add_mission_from_folder
from restapi.models import Mission, Tag


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
    for mission_str in db_mission_set - fs_mission_set:
        date_str, name = mission_str.split("_", 1)
        mission_date = datetime.strptime(date_str, "%Y.%m.%d").date()
        mission_to_delete = Mission.objects.filter(name=name, date=mission_date)[0]
        if mission_to_delete:
            try:
                mission_to_delete.delete()
                logging.info(
                    f"Deleted mission '{name}' from database as it's no longer in the filesystem."
                )
            except Exception as e:
                logging.error(f"Error deleting mission '{name}': {e}")

    # find unused tags and delete them
    Tag.objects.filter(mission_tags=None).delete()
