import os
import logging
import yaml
from datetime import datetime
from .Command import Command
from restapi.models import Mission, File, Mission_files


class AddFolderCommand(Command):
    name = "addfolder"

    def parser_setup(self, subparser):
        """
        Parser setup for addfolder subcommand
        ### Parameters
        subparser: subparser to which this subcommand belongs to
        """
        folder_parser = subparser.add_parser(self.name, help="adds details from folder")
        folder_parser.add_argument("--path", required=True, help="Filepath")
        folder_parser.add_argument("--location", required=False, help="location")
        folder_parser.add_argument(
            "--notes", required=False, help="other mission details"
        )

    def command(self, args):
        add_mission_from_folder(args.path, args.location, args.notes)


def get_duration(path):
    metadata = load_yaml_metadata(path)
    duration = get_mcap_duration_from_yaml(metadata)
    return duration


def load_yaml_metadata(yaml_filepath):
    """Load YAML metadata."""
    with open(yaml_filepath, "r") as file:
        return yaml.safe_load(file)


def get_mcap_duration_from_yaml(metadata):
    """Extract duration in seconds from YAML."""
    nanoseconds = (
        metadata.get("rosbag2_bagfile_information", {})
        .get("duration", {})
        .get("nanoseconds", 0)
    )
    return nanoseconds / 1e9


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


def get_details_id(path):
    try:
        mission = File.objects.get(file_path=path)
        return mission
    except File.DoesNotExist:
        print(f"No Details found for file '{path}'")
        return None


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
                robot = None
                add_details(folder_path, robot, mission)
            except Exception as e:
                logging.error(f"Error adding mission: {e}")
        else:
            logging.warning("skipping because this mission has already been added")
    else:
        logging.warning("Skipping folder due to naming issues.")


def add_details(mission_path, robot, id):
    """
    iterates through the folders and subfolders to find the mcap files and metadata files
    this information is then stored in the database
    """
    mcap_path, metadata = None, None
    for folder in os.listdir(mission_path):
        folder_path = os.path.join(mission_path, folder)
        typ = os.path.basename(folder_path)

        if not os.path.isdir(folder_path):
            continue
        for subfolder in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subfolder)

            if not os.path.isdir(subfolder_path):
                continue
            for item in os.listdir(subfolder_path):
                if os.path.join(subfolder_path, item).endswith(".mcap"):
                    mcap_path = os.path.join(subfolder_path, item)
                if os.path.join(subfolder_path, item).endswith(".yaml"):
                    metadata = os.path.join(subfolder_path, item)
            if mcap_path and metadata:
                size = os.path.getsize(mcap_path)
                duration = get_duration(metadata)
                save_Details(mcap_path, size, duration, robot)
                details_id = get_details_id(mcap_path)
                save_missionfiles(id, details_id, typ)


def save_missionfiles(mission_id, details_id, typ):
    try:
        files = Mission_files(mission=mission_id, file=details_id, type=typ)
        files.save()
    except Exception as e:
        logging.error(f"Error Adding Mission_files: {e}")


def save_Details(path, size, duration, robot):
    if size and duration:
        file = File(file_path=path, robot=robot, duration=duration, size=size)
        try:
            file.save()
        except Exception as e:
            logging.error(f"Error Adding Details: {e}")
    else:
        logging.warning("Skipping due to issues with the metadata")
