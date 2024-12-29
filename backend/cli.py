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
from cli_commands.Command import Command

try:
    import readline
except ImportError:
    readline = None

# Set up Django env
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # Adjust as needed
django.setup()

# Importing Commands
from cli_commands.MissionCommand import MissionCommand  # noqa
from cli_commands.TagCommand import TagCommand  # noqa
from cli_commands.ApiKeyCommand import ApiKeyCommand  # noqa
from cli_commands.AddFolderCommand import AddFolderCommand  # noqa
from cli_commands.SyncFolderCommand import SyncFolderCommand  # noqa

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


commands: dict[str, Command] = {
    "mission": MissionCommand(),
    "tag": TagCommand(),
    "api-key": ApiKeyCommand(),
    "addfolder": AddFolderCommand(),
    "syncfolder": SyncFolderCommand(),
}

# Arg parser
parser = argparse.ArgumentParser(description="Mission CLI")
subparser = parser.add_subparsers(dest="command")

for command in commands:
    commands[command].parser_setup(subparser)

argcomplete.autocomplete(parser)


def main(args):
    args = parser.parse_args(args)

    # Execute command

    if args.command in commands:
        commands[args.command].command(args)
    else:
        interactive(parser)


if __name__ == "__main__":
    main(sys.argv[1:])
