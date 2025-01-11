import os
import logging
from .Command import Command
from .AddFolderCommand import add_mission_from_folder


class SyncFolderCommand(Command):
    name = "syncfolder"

    def parser_setup(self, subparser):
        sync_parser = subparser.add_parser(
            self.name, help="adds all missions from folder"
        )
        sync_parser.add_argument("--path", required=True, help="Filepath")
        sync_parser.add_argument("--location", required=False, help="location")
        sync_parser.add_argument(
            "--notes", required=False, help="other mission details"
        )

    def command(self, args):
        sync_folder(args.path, args.location, args.notes)


def sync_folder(folder_path, location=None, notes=None):
    """
    Adds all Missions from a folder wich are not yet in the DB
    """
    if os.path.isdir(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                add_mission_from_folder(item_path, location, notes)
    else:
        logging.error("invalid path")
