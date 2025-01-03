from abc import ABC, abstractmethod
import argparse
import environ

env = environ.Env(USE_UNICODE=(bool, True))
environ.Env.read_env("./backend/.env")

USE_UNICODE = env("USE_UNICODE")


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

            line = line[:-3]
            print(line)


def get_width_of_multiline_string(str: str):
    widths = map(len, str.split("\n"))
    return max(widths)
