import logging
import argparse
from .Command import Command
from django.core.exceptions import ValidationError
from getpass import getpass
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class UserCommand(Command):
    name = "user"

    def parser_setup(self, subparser):
        self.parser: argparse.ArgumentParser = subparser.add_parser(
            self.name, help="Modifiy Users"
        )
        user_subparser: argparse._SubParsersAction = self.parser.add_subparsers(
            dest="user"
        )

        # Add command
        add_parser: argparse.ArgumentParser = user_subparser.add_parser(
            "add", help="Add User"
        )
        add_parser.add_argument("--name", required=True, help="User name")
        add_parser.add_argument(
            "--email", required=False, help="email of User"
        )  # email is used when requesting password reset via API ENDPOINT

        # Remove command
        remove_parser: argparse.ArgumentParser = user_subparser.add_parser(
            "remove", help="Remove User"
        )
        remove_parser.add_argument("--name", required=True, help="User name")

        # change-password command
        change_parser: argparse.ArgumentParser = user_subparser.add_parser(
            "change-password", help="Change the password of a user"
        )
        change_parser.add_argument("--name", required=True, help="User name")

        # List command
        _ = user_subparser.add_parser("list", help="List all Users")

    def command(self, args):
        match args.user:
            case "add":
                add_user(args.name, args.email)
            case "remove":
                remove_user(args.name)
            case "change-password":
                change_password(args.name)
            case "list":
                list_user()
            case _:
                self.parser.print_help()


def read_and_validate_password(
    prompt1="Password: ", prompt2="Verify Password: "
) -> str:
    password = getpass(prompt1)
    password_verify = getpass(prompt2)

    if password != password_verify:
        raise ValidationError("The passwords do not match")

    validate_password(password)
    return password


def add_user(name, email=None):
    try:
        User.username_validator(name)
    except ValidationError as e:
        logging.error(e)
        return

    try:
        password = read_and_validate_password()
    except ValidationError as e:
        logging.error(e)
        return

    try:
        user = User.objects.create_user(username=name, email=email, password=password)
        user.full_clean()
    except Exception as e:
        logging.error(e)
        try:
            user.delete()
        except Exception:
            pass
        return

    logging.info(f"User '{name}' added")


def change_password(name):
    try:
        user = User.objects.get(username=name)
    except User.DoesNotExist:
        logging.error(f"User '{name}' does not exist")
        return

    try:
        password = read_and_validate_password("New Password: ", "Verify new Password: ")
    except ValidationError as e:
        logging.error(e)
        return

    if user.check_password(password):
        logging.error("The new password can't be the same as the old password")
        return

    try:
        user.set_password(password)
        user.save()
    except Exception as e:
        logging.error(e)
        return

    logging.info(f"Pasword of user '{name}' changed successfully")


def remove_user(name):
    try:
        user = User.objects.get(username=name)
    except User.DoesNotExist:
        logging.error(f"User '{name}' does not exist")
        return

    try:
        user.delete()
    except Exception as e:
        logging.error(e)
        return

    logging.info(f"User '{name}' removed")


def list_user():
    users = User.objects.values()
    UserCommand.print_table(users)
