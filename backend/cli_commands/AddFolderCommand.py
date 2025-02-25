import os
import logging
from datetime import datetime
from .Command import Command
from restapi.models import Mission, File
from django.core.files.storage import Storage
from mcap.reader import make_reader


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


storage = File.file.field.storage


def get_duration(path, storage: Storage = storage):
    with storage.open(path, "rb") as f:
        reader = make_reader(f)
        statistics = reader.get_summary().statistics
        return (statistics.message_end_time - statistics.message_start_time) * 10**-9


def extract_topics_from_mcap(mcap_path, storage: Storage = storage):
    with storage.open(mcap_path, "rb") as f:
        reader = make_reader(f)
        summary = reader.get_summary()
        schema_map = {schema.id: schema.name for schema in summary.schemas.values()}
        channel_message_counts = summary.statistics.channel_message_counts
        duration = get_duration(mcap_path)
        topic_info = {
            channel.topic: {
                "type": schema_map.get(channel.schema_id, "Unknown"),
                "message_count": channel_message_counts.get(channel.id, 0),
                "frequency": 0
                if duration == 0
                else channel_message_counts.get(channel.id, 0) / duration,
            }
            for channel in summary.channels.values()
        }
        return topic_info


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
        file = File.objects.get(file=path)
        return file
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


def add_details(mission_path, robot, mission):
    """
    iterates through the folders and subfolders to find the mcap files and metadata files
    this information is then stored in the database
    """
    # storage.listdir returns a tuple where the first element is a list of all directories
    # and the second element a list of all files
    for folder in storage.listdir(mission_path)[0]:
        folder_path = os.path.join(mission_path, folder)
        typ = os.path.basename(folder_path)

        for subfolder in storage.listdir(folder_path)[0]:
            subfolder_path = os.path.join(folder_path, subfolder)

            mcap_path = None
            for item in storage.listdir(subfolder_path)[1]:
                if os.path.join(subfolder_path, item).endswith(".mcap"):
                    mcap_path = os.path.join(subfolder_path, item)
            if mcap_path:
                size = storage.size(mcap_path)
                duration = get_duration(mcap_path)
                save_Details(mcap_path, size, duration, robot, mission, typ)


def save_Details(path, size, duration, robot, mission, type):
    if size and duration:
        file = File(
            file=path,
            robot=robot,
            duration=duration,
            size=size,
            mission=mission,
            type=type,
        )
        try:
            file.save()
        except Exception as e:
            logging.error(f"Error Adding Details: {e}")
    else:
        logging.warning("Skipping due to issues with the metadata")
