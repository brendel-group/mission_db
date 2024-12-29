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
from cli_commands.Command import Command

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
from rest_framework_api_key.models import APIKey  # noqa
from cli_commands.MissionCommand import MissionCommand  # noqa

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
    Command.print_table(serializer.data)


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
    Command.print_table(serializer.data)


def add_api_key(name, expiry_date=None):
    """
    Add/create a new API KEY with an optional expiration date.
    The date is expected to be a date and time, but can also be just a date.

    Args:
        name: Name of new API
        expiry_date (optional): Expiration date. Defaults to None.
    """
    try:
        name, key = APIKey.objects.create_key(name=name, expiry_date=expiry_date)
    except Exception as e:
        logging.error(f"Couldn't create API KEY with name '{name}': {e}")
        return

    logging.info(
        f"Api Key '{name}' created\nkey: '{key}'\nThis key will not be visible again!"
    )


def remove_api_key(prefix=None, name=None):
    """"
    Remove an API KEY either by name or prefix.\\
    The prefix can be found with `api-key list`.\\
    Both are optional but one has to be given.\\
    If both are given the prefix is preferred, since it's unique.\\
    If the name is used and there are mutliple entries with the same name, all are removed.
    
    Args:
        prefix (optional): the prefix of an API KEY
        name (optional): the name of one or more API KEYs
    """
    if prefix:
        api_key = APIKey.objects.filter(prefix=prefix)
    elif name:
        api_key = APIKey.objects.filter(name=name)
    else:
        logging.error("Either 'prefix' or 'name' must be provided")
        return

    if not api_key.exists():
        logging.error(f"API KEY '{prefix if prefix else name}' not found")
        return

    try:
        api_key.delete()
    except Exception as e:
        logging.error(f"Couldn't remove API KEY: {e}")
        return

    logging.info(f"Removed API KEY '{prefix if prefix else name}'")


def list_api_keys():
    keys = APIKey.objects.values()
    Command.print_table(keys)


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


def api_key_command(api_key_parser, args):
    match args.api_key:
        case "add":
            add_api_key(args.name, args.expiry_date)
        case "remove":
            remove_api_key(args.prefix, args.name)
        case "list":
            list_api_keys()
        case _:
            api_key_parser.print_help()


def folder_arg_parser(subparser):
    """
    Parser setup for addfolder subcommand
    ### Parameters
    subparser: subparser to which this subcommand belongs to
    """
    folder_parser = subparser.add_parser("addfolder", help="adds details from folder")
    folder_parser.add_argument("--path", required=True, help="Filepath")
    folder_parser.add_argument("--location", required=False, help="location")
    folder_parser.add_argument("--notes", required=False, help="other mission details")


def sync_arg_parser(subparser):
    sync_parser = subparser.add_parser(
        "syncfolder", help="adds all missions from folder"
    )
    sync_parser.add_argument("--path", required=True, help="Filepath")
    sync_parser.add_argument("--location", required=False, help="location")
    sync_parser.add_argument("--notes", required=False, help="other mission details")


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


def api_key_arg_parser(subparser: argparse._SubParsersAction):
    api_key_parser = subparser.add_parser("api-key", help="Modify API-KEYS")
    api_key_subparser = api_key_parser.add_subparsers(dest="api_key")

    # Add command
    add_parser = api_key_subparser.add_parser("add", help="Add API KEY")
    add_parser.add_argument("--name", required=True, help="Name of API KEY")
    add_parser.add_argument(
        "--expiry-date", required=False, help="Set expiry date for key"
    )

    # Remove command
    remove_parser = api_key_subparser.add_parser("remove", help="Remove API KEY")
    remove_parser.add_argument("--name", required=False, help="Name of API KEY")
    remove_parser.add_argument("--prefix", required=False, help="Prefix of API KEY")

    # List command
    _ = api_key_subparser.add_parser("list", help="List all API KEYS")

    return api_key_parser


commands: dict[str, Command] = {"mission": MissionCommand()}


def main(args):
    # Arg parser
    parser = argparse.ArgumentParser(description="Mission CLI")
    subparser = parser.add_subparsers(dest="command")

    for command in commands:
        commands[command].parser_setup(subparser)

    folder_arg_parser(subparser)

    sync_arg_parser(subparser)

    tag_parser, tag_mission_parser = tag_arg_parser(subparser)

    api_key_parser = api_key_arg_parser(subparser)

    argcomplete.autocomplete(parser)

    args = parser.parse_args(args)

    # Execute command
    match args.command:
        case "addfolder":
            add_mission_from_folder(args.path, args.location, args.notes)
        case "syncfolder":
            sync_folder(args.path, args.location, args.notes)
        case "tag":
            tag_command(tag_parser, tag_mission_parser, args)
        case "api-key":
            api_key_command(api_key_parser, args)
        case _:
            if args.command in commands:
                commands[args.command].command(args)
            else:
                interactive(parser)


if __name__ == "__main__":
    main(sys.argv[1:])
