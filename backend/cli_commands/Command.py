from abc import ABC, abstractmethod
import argparse
import environ
import os
from pydoc import pager

env = environ.Env(USE_UNICODE=(bool, True))
environ.Env.read_env("./backend/.env")

USE_UNICODE = env("USE_UNICODE")


class Command(ABC):
    """
    To implement a new command implement a new class that inherits from this class \\
    and implement the abstract methods and properties
    """

    def __init__(self, subparser: argparse._SubParsersAction):
        self.parser_setup(subparser)

    @property
    @abstractmethod
    def name() -> str:
        """
        The name of this command, has to be the same as the command when adding it to the subparser with\\
        subparser.add_parser    
        """
        pass

    @abstractmethod
    def parser_setup(self, subparser: argparse._SubParsersAction):
        """
        abstract method to implement the parser setup. Is called automatically with the constructor.\\
        Adds all the required arguments/parsers to the subparser
        
        Args:
            subparser (argparse._SubParsersAction): subparser of main parser
        """
        pass

    @abstractmethod
    def command(self, args: argparse.Namespace):
        """
        abstract method to implement command execution.\\
        Takes the args and processeses them.

        Args:
            args (argparse.Namespace): args preprocessed by argparse
        """
        pass

    @staticmethod
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
        if USE_UNICODE:
            vertical_bar = "│"  # U+2502
            horizontal_bar = "─"  # U+2500
            cross_bar = "┼"  # U+253C
        else:
            vertical_bar = "|"
            horizontal_bar = "-"
            cross_bar = "+"

        if not list_of_dict:
            print("Empty list nothing to display")
            return

        keys = list(list_of_dict[0])

        # get widths of columns

        widths = {}

        for key in keys:
            list_of_widths = list(
                map(lambda d: get_width_of_multiline_string(str(d[key])), list_of_dict)
            )
            list_of_widths.append(len(key))
            widths[key] = max(list_of_widths)

        table = ""

        # print header

        header = ""
        vertical_line = ""
        for key in keys:
            header += f"{key:<{widths[key]}} {vertical_bar} "
            vertical_line += (
                horizontal_bar * (widths[key] + 1) + cross_bar + horizontal_bar
            )

        # remove last 3 characters because there is no extra column
        header = header[:-3]
        vertical_line = vertical_line[:-3]
        table += header + "\n"
        table += vertical_line + "\n"

        # print content

        for entry in list_of_dict:
            line = ""
            next_line = {}

            # add normal content, but only first line
            for key in keys:
                content = str(entry[key])
                if "\n" in content:
                    # extract first line and store remaining lines in next_line dict
                    splitted = content.split("\n")
                    content = splitted[0]
                    next_line[key] = splitted[1:]

                line += f"{content:<{widths[key]}} {vertical_bar} "

            # add remaining lines
            while next_line:
                # trim line
                line = line[:-3]
                line += "\n"

                for key in keys:
                    # add empty field or content
                    if key in next_line:
                        contents = next_line[key]
                        content = str(contents.pop(0))
                        if not contents:
                            del next_line[key]

                        line += f"{content:<{widths[key]}} {vertical_bar} "
                    else:
                        line += f"{" ":<{widths[key]}} {vertical_bar} "

            table += line[:-3] + "\n"

        table = table[:-1]

        try:
            terminal_cols, terminal_rows = os.get_terminal_size()
        except Exception:
            terminal_cols = float("inf")
            terminal_rows = float("inf")

        terminal_rows -= 1  # the bottom line in interactive mode is the input line
        text_rows = table.count("\n") + 1
        text_cols = len(vertical_line)

        if (text_cols > terminal_cols) or (text_rows > terminal_rows):
            pager(table)
        else:
            print(table)


def get_width_of_multiline_string(str: str):
    widths = map(len, str.split("\n"))
    return max(widths)
