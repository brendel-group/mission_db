#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import os
import sys
import argcomplete
import argparse
import django
import logging
import shlex
import code
from datetime import datetime

try:
    import readline
except ImportError:
    readline = None

# Set up Django env
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # Adjust as needed
django.setup()

# Importing Models, adjust as needed
from restapi.models import Mission, Tag, Mission_tags  # noqa
from restapi.serializer import MissionSerializer, TagSerializer  # noqa

# Set up logging
logging.basicConfig(level=logging.INFO)

# set up repl
REPL_HISTFILE = os.path.expanduser("~/.polybot_mission_db_cli.py_hist")
REPL_HISTFILE_SIZE = 1000

# handle wrong home directory
HOME = os.path.expanduser("~")
if not HOME or HOME == "/" or not os.path.exists(HOME):
    # try env variable USERPROFILE
    HOME = os.environ.get("USERPROFILE")
    if HOME and os.path.exists(HOME):
        REPL_HISTFILE = os.path.join(HOME, ".polybot_mission_db_cli.py_hist")
    else:
        # fall back to current working directory
        REPL_HISTFILE = os.path.join(os.path.curdir, ".polybot_mission_db_cli.py_hist")


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


def check_mission(name, date):
    """
    Checks if Mission with the same name and date exists
    """
    return Mission.objects.filter(name=name, date=date).exists()


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


def add_mission_from_folder(folder_path, location=None, notes=None):
    """
    Add mission to DB with data from filesystem
    ### Parameters
    folder_path: path to a folder without trailing /\\
    location: optional string containing information about the location\\
    notes: optional string containing other extra information
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


def add_mission(name, mission_date, location=None, notes=None):
    """
    Add mission to DB
    ### Parameters
    name: string containing the mission name\\
    mission_date: date object of the date\\
    location: optional string containing information about the location\\
    notes: optional string containing other extra information 
    """
    try:
        mission = Mission(name=name, date=mission_date, location=location, notes=notes)
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
    """Add a tag to the database

    Args:
        name: Tag name
        color (optional): Tag color
    """
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
    """Remove a tag either by id or name. If both are given the id will be used and the name is ignored
    logs an error if neither are given

    Args:
        id (optional): id of tag to remove
        name (optional): name of tag to remove
    """
    if not (id or name):
        logging.error("No id or name given")
        return

    try:
        if id:
            tag = Tag.objects.get(id=id)
        else:
            tag = Tag.objects.get(name=name)

        missions_with_tag = Mission.objects.filter(mission_tags__tag=tag)
        if missions_with_tag.exists():
            response = input(
                f"The Tag is used in {len(missions_with_tag)} Mission(s).\nDo you really want to remove it? [y/N] "
            ).lower()
            if response == "y":
                tag.delete()
                logging.info(f"Tag '{tag.name}' has been removed.")
            else:
                logging.info("Tag not removed")
        else:
            tag.delete()
            logging.info(f"Tag '{tag.name}' has been removed.")
    except Tag.DoesNotExist:
        if id:
            logging.error(f"No Tag found with id '{id}'.")
        else:
            logging.error(f"No Tag found with name '{name}'.")


def list_tags():
    """
    list all Tags in a table
    """
    tags = Tag.objects.all().order_by("id")
    serializer = TagSerializer(tags, many=True)
    print_table(serializer.data)


def change_tag(id=None, name=None, color=None):
    """
    Change a Tag either by id or name. \\
    If the id is given then always the Tag with that id will be changed.\\
    If only the name is given the Tag will be identified by the name.

    Args:
        id (optional): the id of the Tag
        name (optional): the name or the new name of the Tag
        color (optional): the new color of the Tag
    """
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


def list_tags_by_mission(id):
    """
    List all Tags that belong to the same Mission

    Args:
        id: mission id
    """
    tags = Tag.objects.filter(mission_tags__mission_id=id).order_by("id")
    serializer = TagSerializer(tags, many=True)
    print_table(serializer.data)


def list_missions_by_tag(id=None, name=None):
    """
    List all Missions that have the same Tag
    Either id or name must be given. If both are given it is checked, that they belong
    to the same Tag.

    Args:
        id (optional): Tag id
        name (optional): Tag name
    """
    # Input check
    if id and name:
        try:
            tag = Tag.objects.get(id=id)
        except Tag.DoesNotExist:
            logging.error(f"No Tag with id {id} found")
            return
        if tag.name != name:
            logging.error("Tag id and name given but dont match.")
            return

    if not (id or name):
        logging.error("At least one of --id or --name must be provided")
        return

    # Actual processing
    if id:
        missions = Mission.objects.filter(mission_tags__tag_id=id).order_by("id")
    else:
        missions = Mission.objects.filter(mission_tags__tag__name=name).order_by("id")
    serializer = MissionSerializer(missions, many=True)
    print_table(serializer.data)


def add_tag_to_mission(id, tag_id=None, tag_name=None):
    """
    Either tag_id or tag_name must be given. If both are given it is checked, that they belong
    to the same Tag.

    Args:
        id: Mission id
        tag_id (optional): Tag id
        tag_name (optional): Tag name
    """
    # Input check
    if tag_id and tag_name:
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            logging.error(f"No Tag with id {tag_id} found")
            return
        if tag.name != tag_name:
            logging.error("Tag id and name given but dont match.")
            return

    if not (tag_id or tag_name):
        logging.error("At least one of --tag-id or --tag-name must be provided")
        return

    # Actual processing
    try:
        mission = Mission.objects.get(id=id)
        if tag_id:
            tag = Tag.objects.get(id=tag_id)
            created = False
        else:
            tag, created = Tag.objects.get_or_create(name=tag_name)
        mission_tag = Mission_tags(mission=mission, tag=tag)
        mission_tag.full_clean()
        mission_tag.save()

        # Output
        if created:
            logging.info(f"Tag '{tag.name}' created and tagged Mission with id {id}")
        else:
            logging.info(f"Tagged Mission with id {id} with '{tag.name}'")

    # Error handling
    except Mission.DoesNotExist:
        logging.error(f"No Mission with id {id} found")
    except Exception as e:
        logging.error(e)


def remove_tag_from_mission(id, tag_id=None, tag_name=None):
    """
    Either tag_id or tag_name must be given. If both are given it is checked, that they belong
    to the same Tag.

    Args:
        id: Mission id
        tag_id (optional): Tag id
        tag_name (_type_, optional): Tag name
    """
    # Input check
    if not (tag_id or tag_name):
        logging.error("At least one of --tag-id or --tag-name must be provided")
        return

    try:
        if tag_id and tag_name:
            tag = Tag.objects.get(id=tag_id)
            if tag.name != tag_name:
                logging.error("Tag id and name given but dont match.")
                return

        # Actual processing
        # using filter over get, because if for some reason the same Tag got added multiple times to the same Mission
        # filter will handle it properly, while get throws an error
        if tag_id:
            mission_tag = Mission_tags.objects.filter(mission_id=id, tag_id=tag_id)
        else:
            mission_tag = Mission_tags.objects.filter(mission_id=id, tag__name=tag_name)
        if not mission_tag.exists():
            raise Mission_tags.DoesNotExist
        mission_tag.delete()

        # Output
        tag = Tag.objects.filter(id=tag_id) | Tag.objects.filter(name=tag_name)
        tag = tag.first()
        logging.info(f"Removed Tag '{tag.name}' from Mission with id {id}")

    # Error handling
    except Mission.DoesNotExist:
        logging.error(f"No Mission with id {id} found")
    except Mission_tags.DoesNotExist:
        if tag_id:
            logging.error(f"No Tag with id {tag_id} found at Mission with id {id}")
        else:
            logging.error(
                f"No Tag with name '{tag_name}' found at Mission with id {id}"
            )
    except Tag.DoesNotExist:
        if tag_id:
            logging.error(f"No Tag with id {tag_id} found")
        else:
            logging.error(f"No Tag with name '{tag_name}' found")


class Interactive(code.InteractiveConsole):
    def __init__(self, help):
        super().__init__(locals=None, filename="<console>")
        self.help = help

    def runsource(self, source, filename="<input>", symbol="single"):
        args = shlex.split(source)
        if not args:
            return
        if "exit" in args:
            raise SystemExit
        if args == ["help"]:
            print(
                self.help
                + "\n"
                + "only interactive:\n"
                + "  exit\t\t\texit the command prompt\n"
                + "  help\t\t\tshow this help message"
            )
            return
        try:
            main(args)
        except SystemExit:
            pass


def interactive(parser: argparse.ArgumentParser):
    if readline:
        if os.path.exists(REPL_HISTFILE):
            try:
                readline.read_history_file(REPL_HISTFILE)
            except PermissionError as p:
                print(p, REPL_HISTFILE, "\nCould not read history file")

        readline.set_completer_delims("")
        readline.set_completer(argcomplete.CompletionFinder(parser).rl_complete)
        readline.parse_and_bind("tab: complete")

    console = Interactive(parser.format_help())
    try:
        console.interact(
            banner="cli.py interactive mode\n  type 'help' for help or 'exit' to exit",
            exitmsg="",
        )
    except SystemExit:
        pass

    if readline:
        readline.set_history_length(REPL_HISTFILE_SIZE)
        try:
            readline.write_history_file(REPL_HISTFILE)
        except PermissionError as p:
            print(
                p,
                REPL_HISTFILE,
                "\nCould not write history to file",
            )


def mission_command(mission_parser, mission_tag_parser, args):
    match args.mission:
        case "add":
            # Validate date
            validated_date = validate_date(args.date)
            if validated_date is None:
                return

            add_mission(
                args.name,
                validated_date,  # Pass the validated date
                args.location,
                args.notes,
            )
        case "remove":
            remove_mission(args.id)
        case "list":
            missions = Mission.objects.all().order_by("id")
            serializer = MissionSerializer(missions, many=True)
            print_table(serializer.data)
        case "tag":
            match args.mission_tag:
                case "list":
                    list_tags_by_mission(args.id)
                case "add":
                    add_tag_to_mission(args.id, args.tag_id, args.tag_name)
                case "remove":
                    remove_tag_from_mission(args.id, args.tag_id, args.tag_name)
                case _:
                    mission_tag_parser.print_help()
        case _:
            mission_parser.print_help()


def tag_command(tag_parser, tag_mission_parser, args):
    match args.tag:
        case "add":
            add_tag(args.name, args.color)
        case "remove":
            remove_tag(args.id, args.name)
        case "list":
            list_tags()
        case "change":
            change_tag(args.id, args.name, args.color)
        case "mission":
            match args.tag_mission:
                case "list":
                    list_missions_by_tag(args.id, args.name)
                case _:
                    tag_mission_parser.print_help()
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
    mission_subparser = mission_parser.add_subparsers(dest="mission")

    # Add command
    add_parser = mission_subparser.add_parser("add", help="Add mission")
    add_parser.add_argument("--name", required=True, help="Mission name")
    add_parser.add_argument("--date", required=True, help="Mission date (YYYY-MM-DD)")
    add_parser.add_argument("--location", required=False, help="Mission location")
    add_parser.add_argument("--notes", required=False, help="Notes mission details")

    # Remove command
    remove_parser = mission_subparser.add_parser("remove", help="Remove mission")
    remove_parser.add_argument("--id", required=True, help="ID")

    # List command
    _ = mission_subparser.add_parser("list", help="List all missions")

    # tag subcommand
    tag_parser = mission_subparser.add_parser("tag", help="Change tags of one mission")
    tag_subparser = tag_parser.add_subparsers(dest="mission_tag")

    # tag list
    list_tag_parser = tag_subparser.add_parser("list", help="List tags of one mission")
    list_tag_parser.add_argument("--id", required=True, help="Select mission by id")

    # tag add
    tag_add_parser = tag_subparser.add_parser("add", help="Add tag to mission")
    tag_add_parser.add_argument("--id", required=True, help="Select mission by id")
    tag_add_parser.add_argument(
        "--tag-name", required=False, help="Add or create tag by name"
    )
    tag_add_parser.add_argument("--tag-id", required=False, help="Add tag by id")

    # tag remove
    tag_remove_parser = tag_subparser.add_parser(
        "remove", help="Remove tag from mission"
    )
    tag_remove_parser.add_argument("--id", required=True, help="Select mission by id")
    tag_remove_parser.add_argument(
        "--tag-name", required=False, help="Remove tag by name"
    )
    tag_remove_parser.add_argument("--tag-id", required=False, help="Remove tag by id")

    return mission_parser, tag_parser


def folder_arg_parser(subparser):
    """
    Parser setup for addfolder subcommand
    ### Parameters
    subparser: subparser to which this subcommand belongs to
    """
    folder_parser = subparser.add_parser("addfolder", help="adds details from folder")
    folder_parser.add_argument("--path", required=True, help="Filepath")
    folder_parser.add_argument("--location", required=False, help="location")
    folder_parser.add_argument("--notes", required=False, help="notes mission details")


def sync_arg_parser(subparser):
    sync_parser = subparser.add_parser(
        "syncfolder", help="adds all missions from folder"
    )
    sync_parser.add_argument("--path", required=True, help="Filepath")
    sync_parser.add_argument("--location", required=False, help="location")
    sync_parser.add_argument("--notes", required=False, help="notes mission details")


def tag_arg_parser(subparser):
    tag_parser = subparser.add_parser("tag", help="Modify Tags")
    tag_subparser = tag_parser.add_subparsers(dest="tag")

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

    # mission subcommand
    mission_parser = tag_subparser.add_parser(
        "mission", help="Change tags of one mission"
    )
    mission_subparser = mission_parser.add_subparsers(dest="tag_mission")

    # mission list
    list_mission_parser = mission_subparser.add_parser(
        "list", help="List missions with selected tag"
    )
    list_mission_parser.add_argument("--id", required=False, help="Select tag by id")
    list_mission_parser.add_argument(
        "--name", required=False, help="Select tag by name"
    )

    return tag_parser, mission_parser


def main(args):
    # Arg parser
    parser = argparse.ArgumentParser(description="Mission CLI")
    subparser = parser.add_subparsers(dest="command")

    mission_parser, mission_tag_parser = mission_arg_parser(subparser)

    folder_arg_parser(subparser)

    sync_arg_parser(subparser)

    tag_parser, tag_mission_parser = tag_arg_parser(subparser)

    argcomplete.autocomplete(parser)

    args = parser.parse_args(args)

    # Execute command
    match args.command:
        case "mission":
            mission_command(mission_parser, mission_tag_parser, args)
        case "addfolder":
            add_mission_from_folder(args.path, args.location, args.notes)
        case "syncfolder":
            sync_folder(args.path, args.location, args.notes)
        case "tag":
            tag_command(tag_parser, tag_mission_parser, args)
        case _:
            interactive(parser)


if __name__ == "__main__":
    main(sys.argv[1:])
