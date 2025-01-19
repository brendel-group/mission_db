from datetime import datetime
import os
import logging
from .Command import Command
from .AddFolderCommand import add_mission_from_folder
from restapi.models import Mission


class SyncFolderCommand(Command):
    name = "syncfolder"

    def parser_setup(self, subparser):
        sync_parser = subparser.add_parser(
            self.name, help="adds all missions from folder"
        )
        sync_parser.add_argument("--path", required=True, help="Filepath")

    def command(self, args):
        sync_folder(args.path)


def sync_folder(folder_path):
    """
    Syncs all Missions from a folder:
    - Adds missions from folders in the filesystem that are not in the database.
    - Deletes missions from the database that are not in the filesystem.
    """
    if os.path.isdir(folder_path):
        # Get all existing missions in the database
        db_missions = Mission.objects.filter()
        db_mission_set = set(
            f"{mission.date.strftime('%Y.%m.%d')}_{mission.name}"
            for mission in db_missions
        )

        # Get all folder names in the filesystem
        fs_mission_set = set(
            folder
            for folder in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, folder))
        )

        # Add missions for folders not yet in the database
        for folder in fs_mission_set - db_mission_set:
            folder_path_full = os.path.join(folder_path, folder)
            add_mission_from_folder(folder_path_full, None, None)

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
    else:
        logging.error("Invalid path")
