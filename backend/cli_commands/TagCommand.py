import logging
from .Command import Command
from restapi.models import Tag, Mission
from restapi.serializer import TagSerializer, MissionSerializer


class TagCommand(Command):
    name = "tag"

    def parser_setup(self, subparser):
        self.__tag_parser = subparser.add_parser(self.name, help="Modify Tags")
        tag_subparser = self.__tag_parser.add_subparsers(dest="tag")

        # Add command
        add_parser = tag_subparser.add_parser("add", help="Add mission")
        add_parser.add_argument("--name", required=True, help="Tag name")
        add_parser.add_argument("--color", required=False, help="Tag color")

        # Remove command
        remove_parser = tag_subparser.add_parser("remove", help="Remove Tag")
        group = remove_parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--id", required=False, help="id of Tag to remove")
        group.add_argument("--name", required=False, help="name of Tag to remove")

        # List command
        _ = tag_subparser.add_parser("list", help="List all Tags")

        # change command
        change_parser = tag_subparser.add_parser(
            "change", help="Change Tag by name or id"
        )
        change_parser.add_argument("--id", required=False, help="Tag id")
        change_parser.add_argument("--name", required=False, help="Tag name")
        change_parser.add_argument("--color", required=False, help="Tag color")

        # mission subcommand
        self.__mission_parser = tag_subparser.add_parser(
            "mission", help="Change tags of one mission"
        )
        mission_subparser = self.__mission_parser.add_subparsers(dest="tag_mission")

        # mission list
        list_mission_parser = mission_subparser.add_parser(
            "list", help="List missions with selected tag"
        )
        group = list_mission_parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--id", required=False, help="Select tag by id")
        group.add_argument("--name", required=False, help="Select tag by name")

    def command(self, args):
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
                        self.__mission_parser.print_help()
            case _:
                self.__tag_parser.print_help()


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
    TagCommand.print_table(serializer.data)


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
    TagCommand.print_table(serializer.data)
