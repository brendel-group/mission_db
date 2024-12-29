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
from cli_commands.TagCommand import TagCommand  # noqa

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


commands: dict[str, Command] = {
    "mission": MissionCommand(),
    "tag": TagCommand(),
}


def main(args):
    # Arg parser
    parser = argparse.ArgumentParser(description="Mission CLI")
    subparser = parser.add_subparsers(dest="command")

    for command in commands:
        commands[command].parser_setup(subparser)

    folder_arg_parser(subparser)

    sync_arg_parser(subparser)

    api_key_parser = api_key_arg_parser(subparser)

    argcomplete.autocomplete(parser)

    args = parser.parse_args(args)

    # Execute command
    match args.command:
        case "addfolder":
            add_mission_from_folder(args.path, args.location, args.notes)
        case "syncfolder":
            sync_folder(args.path, args.location, args.notes)
        case "api-key":
            api_key_command(api_key_parser, args)
        case _:
            if args.command in commands:
                commands[args.command].command(args)
            else:
                interactive(parser)


if __name__ == "__main__":
    main(sys.argv[1:])
