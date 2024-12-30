from abc import ABC, abstractmethod
import argparse


class Command(ABC):
    def __init__(self, subparser: argparse._SubParsersAction):
        self.parser_setup(subparser)

    @property
    @abstractmethod
    def name() -> str:
        pass

    @abstractmethod
    def parser_setup(self, subparser: argparse._SubParsersAction):
        pass

    @abstractmethod
    def command(self, args: argparse.Namespace):
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
            vertical_line += (
                horizontal_bar * (widths[key] + 1) + cross_bar + horizontal_bar
            )

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
