import logging
from .Command import Command
from rest_framework_api_key.models import APIKey


class ApiKeyCommand(Command):
    name = "api-key"

    def parser_setup(self, subparser):
        self.__api_key_parser = subparser.add_parser(self.name, help="Modify API-KEYS")
        api_key_subparser = self.__api_key_parser.add_subparsers(dest="api_key")

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

    def command(self, args):
        match args.api_key:
            case "add":
                add_api_key(args.name, args.expiry_date)
            case "remove":
                remove_api_key(args.prefix, args.name)
            case "list":
                list_api_keys()
            case _:
                self.__api_key_parser.print_help()


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
    ApiKeyCommand.print_table(keys)
