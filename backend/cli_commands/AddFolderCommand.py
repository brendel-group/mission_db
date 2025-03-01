import os
import logging
from datetime import datetime
from .Command import Command
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


def check_mission(name, date):
    """
    Checks if Mission with the same name and date exists
    """
    return Mission.objects.filter(name=name, date=date).exists()


def extract_info_from_folder(folder_name):
    """
    Extract date and name from folder name
    ### Parameters
    folder_name: basename of folder in format YYYY.MM.DD_missionname
    ### Returns
    date: date object of extracted date
    name: extracted mission name
    """
    try:
        date_str, name = folder_name.split("_", 1)
        mission_date = datetime.strptime(date_str, "%Y.%m.%d").date()
        return mission_date, name
    except ValueError:
        logging.error(
            f"Folder name '{folder_name}' does not match the expected format (YYYY.MM.DD_missionname)."
        )
        return None, None


def add_mission_from_folder(folder_path, location=None, notes=None):
    """
    Add mission to DB with data from filesystem
    ### Parameters
    folder_path: path to a folder without trailing /\\
    location: optional string containing information about the location\\
    other: optional string containing other extra information
    """
    folder_name = os.path.basename(folder_path)
    mission_date, name = extract_info_from_folder(folder_name)

    if mission_date and name:
        if not check_mission(name, mission_date):
            mission = Mission(
                name=name, date=mission_date, location=location, notes=notes
            )
            try:
                mission.save()
                logging.info(f"Mission '{name}' from folder '{folder_name}' added.")
            except Exception as e:
                logging.error(f"Error adding mission: {e}")
        else:
            logging.warning("skipping because this mission has already been added")
    else:
        logging.warning("Skipping folder due to naming issues.")
