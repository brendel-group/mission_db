#!/usr/bin/env python3
import os
import sys
import argparse
import django
import logging
from datetime import datetime

# Set up Django env
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # Adjust as needed
django.setup()

# Importing Models, adjust as needed
from restapi.models import Mission, Tag  # noqa
from restapi.serializer import MissionSerializer, TagSerializer  # noqa

# Set up logging
logging.basicConfig(level=logging.INFO)


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


def check_mission_exists(id):
    """
    Check if mission exists
    ### Parameters
    id: mission_id
    ### Returns
    true if mission exists\\
    false it mission doesn't exist
    """
    return Mission.objects.filter(id=id).exists()


def validate_date(date_str):
    """
    Validate datetime format
    ### Parameters
    date_str: date string in the format YYYY-MM-DD
    ### Returns
    datetime object if format is valid\\
    None if string is of invalid format
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logging.error("Date and time format should be YYYY-MM-DD.")
        return None


def print_table(list_of_dict: list[dict]):
    """
    Print the contents of a list of dictionaries as a table.\\
    A dictionary and a json are essentially the same in python.\\
    So this function can be called with the data of a ListSerializer
    to print a table of DB entries.\\
    The keys/labels are printed in the header.\\
    It assumes that the dictionaries are flat an contain the same keys.\\
    The width of the columns are automatically adjusted to the max width
    of any value in that column.
    ### Parameters
    list_of_dict: A list containing flat dictionaries which all have the same keys
    """
    vertical_bar = "│"  # U+2502
    horizontal_bar = "─"  # U+2500
    cross_bar = "┼"  # U+253C

    if not list_of_dict:
        print("Empty list nothing to display")
        return

    keys = list(list_of_dict[0])

    # get widths of columns

    widths = {}

    for key in keys:
        list_of_widths = list(map(lambda d: len(str(d[key])), list_of_dict))
        list_of_widths.append(len(key))
        widths[key] = max(list_of_widths)

    # print header

    header = ""
    vertical_line = ""
    for key in keys:
        header += f"{key:<{widths[key]}} {vertical_bar} "
        vertical_line += horizontal_bar * (widths[key] + 1) + cross_bar + horizontal_bar

    # remove last 3 characters because there is no extra column
    header = header[:-3]
    vertical_line = vertical_line[:-3]

    print(header)
    print(vertical_line)

    # print content

    for entry in list_of_dict:
        line = ""
        for key in keys:
            line += f"{str(entry[key]):<{widths[key]}} {vertical_bar} "
        line = line[:-3]
        print(line)


def add_mission_from_folder(folder_path, location=None, other=None):
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
        mission = Mission(name=name, date=mission_date, location=location, other=other)
        try:
            mission.save()
            logging.info(f"Mission '{name}' from folder '{folder_name}' added.")
        except Exception as e:
            logging.error(f"Error adding mission: {e}")
    else:
        logging.warning("Skipping folder due to naming issues.")


def add_mission(name, mission_date, location=None, other=None):
    """
    Add mission to DB
    ### Parameters
    name: string containing the mission name\\
    mission_date: date object of the date\\
    location: optional string containing information about the location\\
    other: optional string containing other extra information 
    """
    try:
        mission = Mission(name=name, date=mission_date, location=location, other=other)
        mission.full_clean()  # validation
        mission.save()
        logging.info(f"'{name}' added.")
    except Exception as e:
        logging.error(f"Error adding mission: {e}")


def remove_mission(mission_id):
    """
    Remove mission from DB
    ### Parameters
    mission_id: id of mission to remove
    """
    try:
        # Attempt to find the mission by ID
        mission = Mission.objects.get(id=mission_id)
        mission.delete()  # Delete the found mission
        print(f"Mission with ID {mission_id} has been removed.")
    except Mission.DoesNotExist:
        print(f"No mission found with ID {mission_id}.")


def add_tag(name, color=None):
    if color:
        tag = Tag(name=name, color=color)
    else:
        tag = Tag(name=name)
    try:
        tag.full_clean()  # validation
        tag.save()
        logging.info(f"'{name}' Tag added.")
    except Exception as e:
        logging.error(f"Error adding Tag: {e}")


def remove_tag(id=None, name=None):
    if not (id or name):
        logging.error("No id or name given")
        return

    try:
        if id:
            tag = Tag.objects.get(id=id)
        else:
            tag = Tag.objects.get(name=name)
        tag.delete()
        logging.info(f"Tag '{tag.name}' has been removed.")
    except Tag.DoesNotExist:
        if id:
            logging.error(f"No Tag found with id '{id}'.")
        else:
            logging.error(f"No Tag found with name '{name}'.")


def list_tags():
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    print_table(serializer.data)


def change_tag(id=None, name=None, color=None):
    if not (id or name):
        logging.error("At least one of --id or --name must be provided")
        return
    if not (name or color):
        logging.info("Nothing to change")
        return
    try:
        if id:
            tag = Tag.objects.get(id=id)
        elif name:
            tag = Tag.objects.get(name=name)
        else:
            logging.error("At least one of --id or --name must be provided")
            return

        if name:
            tag.name = name
        if color:
            tag.color = color
        tag.full_clean()
        tag.save()
        logging.info(f"Tag changed to '{tag}'")
    except Exception as e:
        logging.error(f"Error changing Tag: {e}")


def tag_command(tag_parser, args):
    match args.command:
        case "add":
            add_tag(args.name, args.color)
        case "remove":
            remove_tag(args.id, args.name)
        case "list":
            list_tags()
        case "change":
            change_tag(args.id, args.name, args.color)
        case _:
            tag_parser.print_help()


def mission_arg_parser(subparser):
    """
    Parser setup for mission subcommand
    ### Parameters
    subparser: subparser to which this subcommand belongs to
    ### Returns
    mission_parser: subparser here created
    """
    mission_parser = subparser.add_parser("mission", help="Modify Missions")
    mission_subparser = mission_parser.add_subparsers(dest="command")

    # Add command
    add_parser = mission_subparser.add_parser("add", help="Add mission")
    add_parser.add_argument("--name", required=True, help="Mission name")
    add_parser.add_argument("--date", required=True, help="Mission date (YYYY-MM-DD)")
    add_parser.add_argument("--location", required=False, help="Mission location")
    add_parser.add_argument("--other", required=False, help="Other mission details")

    # Remove command
    remove_parser = mission_subparser.add_parser("remove", help="Remove mission")
    remove_parser.add_argument("--id", required=True, help="ID")

    # List command
    _ = mission_subparser.add_parser("list", help="List all missions")

    return mission_parser


def folder_arg_parser(subparser):
    """
    Parser setup for addfolder subcommand
    ### Parameters
    subparser: subparser to which this subcommand belongs to
    """
    folder_parser = subparser.add_parser("addfolder", help="adds details from folder")
    folder_parser.add_argument("--path", required=True, help="Filepath")
    folder_parser.add_argument("--location", required=False, help="location")
    folder_parser.add_argument("--other", required=False, help="other mission details")


def tag_arg_parser(subparser):
    tag_parser = subparser.add_parser("tag", help="Modify Tags")
    tag_subparser = tag_parser.add_subparsers(dest="command")

    # Add command
    add_parser = tag_subparser.add_parser("add", help="Add mission")
    add_parser.add_argument("--name", required=True, help="Tag name")
    add_parser.add_argument("--color", required=False, help="Tag color")

    # Remove command
    remove_parser = tag_subparser.add_parser("remove", help="Remove Tag")
    remove_parser.add_argument("--id", required=False, help="id of Tag to remove")
    remove_parser.add_argument("--name", required=False, help="name of Tag to remove")

    # remove_parser.add_argument("--id", required=True, help="ID")

    # List command
    _ = tag_subparser.add_parser("list", help="List all Tags")

    # change command
    change_parser = tag_subparser.add_parser("change", help="Change Tag by name or id")
    change_parser.add_argument("--id", required=False, help="Tag id")
    change_parser.add_argument("--name", required=False, help="Tag name")
    change_parser.add_argument("--color", required=False, help="Tag color")

    return tag_parser


def main(args):
    # Arg parser
    parser = argparse.ArgumentParser(description="Mission CLI")
    subparser = parser.add_subparsers(dest="type")

    mission_parser = mission_arg_parser(subparser)

    folder_arg_parser(subparser)

    tag_parser = tag_arg_parser(subparser)

    args = parser.parse_args(args)

    # Execute command
    match args.type:
        case "mission":
            match args.command:
                case "add":
                    # Validate date
                    validated_date = validate_date(args.date)
                    if validated_date is None:
                        return

                    add_mission(
                        args.name,
                        validated_date,  # Pass the validated date
                        args.location,
                        args.other,
                    )
                case "remove":
                    remove_mission(args.id)
                case "list":
                    missions = Mission.objects.all()
                    serializer = MissionSerializer(missions, many=True)
                    print_table(serializer.data)
                case _:
                    mission_parser.print_help()
        case "addfolder":
            add_mission_from_folder(args.path, args.location, args.other)
        case "tag":
            tag_command(tag_parser, args)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])
