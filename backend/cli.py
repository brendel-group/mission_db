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
from restapi.models import Mission  # noqa
from cli_commands.MissionCommand import MissionCommand  # noqa
from cli_commands.TagCommand import TagCommand  # noqa
from cli_commands.ApiKeyCommand import ApiKeyCommand  # noqa

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


commands: dict[str, Command] = {
    "mission": MissionCommand(),
    "tag": TagCommand(),
    "api-key": ApiKeyCommand(),
}


def main(args):
    # Arg parser
    parser = argparse.ArgumentParser(description="Mission CLI")
    subparser = parser.add_subparsers(dest="command")

    for command in commands:
        commands[command].parser_setup(subparser)

    folder_arg_parser(subparser)

    sync_arg_parser(subparser)

    argcomplete.autocomplete(parser)

    args = parser.parse_args(args)

    # Execute command
    match args.command:
        case "addfolder":
            add_mission_from_folder(args.path, args.location, args.notes)
        case "syncfolder":
            sync_folder(args.path, args.location, args.notes)
        case _:
            if args.command in commands:
                commands[args.command].command(args)
            else:
                interactive(parser)


if __name__ == "__main__":
    main(sys.argv[1:])
