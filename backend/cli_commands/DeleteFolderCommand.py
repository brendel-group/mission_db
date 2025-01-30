import os
import logging
from datetime import datetime
from .Command import Command
from restapi.models import Mission


class DeleteFolderCommand(Command):
    name = "deletefolder"

    def parser_setup(self, subparser):
        """
        Parser setup for deletefolder subcommand
        ### Parameters
        subparser: subparser to which this subcommand belongs to
        """
        folder_parser = subparser.add_parser(
            self.name, help="deletes mission from database based on folder path"
        )
        folder_parser.add_argument("--path", required=True, help="Filepath")

    def command(self, args):
        delete_mission_from_folder(args.path)


def delete_mission_from_folder(folder_path):
    """
    Delete mission and related data from DB based on folder path
    ### Parameters
    folder_path: path to a folder without trailing /\\
    """
    folder_name = os.path.basename(folder_path)
    mission_date, name = extract_info_from_folder(folder_name)

    if mission_date and name:
        try:
            # find mission
            mission = Mission.objects.get(name=name, date=mission_date)

            # delete mission
            mission.delete()

            logging.info(
                f"Mission '{name}' from folder '{folder_name}' and corresponding files deleted from the database."
            )
        except Mission.DoesNotExist:
            logging.warning(
                f"No mission found for name '{name}' and date '{mission_date}'."
            )
        except Exception as e:
            logging.error(f"Error deleting mission: {e}")
    else:
        logging.warning("Skipping folder due to naming issues.")


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
