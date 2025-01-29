import os
import logging
from datetime import datetime
from .Command import Command
from django.core.files.storage import DefaultStorage
from restapi.models import Mission


class AddFolderCommand(Command):
    name = "addfolder"

    def parser_setup(self, subparser):
        """
        Parser setup for addfolder subcommand
        ### Parameters
        subparser: subparser to which this subcommand belongs to
        """
        folder_parser = subparser.add_parser(self.name, help="adds mission from folder")
        folder_parser.add_argument("--path", required=True, help="Filepath")
        folder_parser.add_argument("--location", required=False, help="location")
        folder_parser.add_argument(
            "--notes", required=False, help="other mission details"
        )

    def command(self, args):
        add_mission_from_folder(args.path, args.location, args.notes)


storage = DefaultStorage()


def add_mission_from_folder(folder_path, location=None, notes=None):
    """
    Adds a mission to the database based on the given folder path.
    Calls sync_mcap_files to process and store associated .mcap and metadata files.
    """
    from .SyncCommand import sync_mcap_files

    folder_name = os.path.basename(folder_path)
    try:
        date_str, name = folder_name.split("_", 1)
        mission_date = datetime.strptime(date_str, "%Y.%m.%d").date()
    except ValueError:
        logging.error(f"Invalid folder name format: {folder_name}")
        return

    if Mission.objects.filter(name=name, date=mission_date).exists():
        logging.warning(f"Mission '{name}' already exists, skipping.")
        return

    try:
        mission = Mission(name=name, date=mission_date, location=location, notes=notes)
        mission.save()
        logging.info(f"Mission '{name}' added successfully.")
        sync_mcap_files(folder_path, mission)
    except Exception as e:
        logging.error(f"Error adding mission: {e}")
