import logging
from restapi.models import Mission, Tag, Mission_tags
from restapi.serializer import MissionSerializer, TagSerializer
from .Command import Command
from datetime import datetime


class MissionCommand(Command):
    def parser_setup(self, subparser):
        """
        Parser setup for mission subcommand
        ### Parameters
        subparser: subparser to which this subcommand belongs to
        ### Returns
        mission_parser: subparser here created
        """
        self.mission_parser = subparser.add_parser("mission", help="Modify Missions")
        mission_subparser = self.mission_parser.add_subparsers(dest="mission")

        # Add command
        add_parser = mission_subparser.add_parser("add", help="Add mission")
        add_parser.add_argument("--name", required=True, help="Mission name")
        add_parser.add_argument(
            "--date", required=True, help="Mission date (YYYY-MM-DD)"
        )
        add_parser.add_argument("--location", required=False, help="Mission location")
        add_parser.add_argument("--notes", required=False, help="Other mission details")

        # Remove command
        remove_parser = mission_subparser.add_parser("remove", help="Remove mission")
        remove_parser.add_argument("--id", required=True, help="ID")

        # List command
        _ = mission_subparser.add_parser("list", help="List all missions")

        # tag subcommand
        self.tag_parser = mission_subparser.add_parser(
            "tag", help="Change tags of one mission"
        )
        tag_subparser = self.tag_parser.add_subparsers(dest="mission_tag")

        # tag list
        list_tag_parser = tag_subparser.add_parser(
            "list", help="List tags of one mission"
        )
        list_tag_parser.add_argument("--id", required=True, help="Select mission by id")

        # tag add
        tag_add_parser = tag_subparser.add_parser("add", help="Add tag to mission")
        tag_add_parser.add_argument("--id", required=True, help="Select mission by id")
        tag_add_parser.add_argument(
            "--tag-name", required=False, help="Add or create tag by name"
        )
        tag_add_parser.add_argument("--tag-id", required=False, help="Add tag by id")

        # tag remove
        tag_remove_parser = tag_subparser.add_parser(
            "remove", help="Remove tag from mission"
        )
        tag_remove_parser.add_argument(
            "--id", required=True, help="Select mission by id"
        )
        tag_remove_parser.add_argument(
            "--tag-name", required=False, help="Remove tag by name"
        )
        tag_remove_parser.add_argument(
            "--tag-id", required=False, help="Remove tag by id"
        )

    def command(self, args):
        match args.mission:
            case "add":
                # Validate date
                validated_date = validate_date(args.date)
                if validated_date is None:
                    return

                add_mission(
                    args.name,
                    validated_date,  # Pass the validated date
                    args.location,
                    args.notes,
                )
            case "remove":
                remove_mission(args.id)
            case "list":
                missions = Mission.objects.all().order_by("id")
                serializer = MissionSerializer(missions, many=True)
                self.print_table(serializer.data)
            case "tag":
                match args.mission_tag:
                    case "list":
                        list_tags_by_mission(args.id)
                    case "add":
                        add_tag_to_mission(args.id, args.tag_id, args.tag_name)
                    case "remove":
                        remove_tag_from_mission(args.id, args.tag_id, args.tag_name)
                    case _:
                        self.tag_parser.print_help()
            case _:
                self.mission_parser.print_help()


def validate_date(date_str):
    """
    Validate datetime format
    ### Parameters
    date_str: date string in the format YYYY-MM-DD
    ### Returns
    datetime object if format is valid\\
    None if string is of invalid format
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logging.error("Date and time format should be YYYY-MM-DD.")
        return None


def add_mission(name, mission_date, location=None, notes=None):
    """
    Add mission to DB
    ### Parameters
    name: string containing the mission name\\
    mission_date: date object of the date\\
    location: optional string containing information about the location\\
    notes: optional string containing other extra information 
    """
    try:
        mission = Mission(name=name, date=mission_date, location=location, notes=notes)
        mission.full_clean()  # validation
        mission.save()
        logging.info(f"'{name}' added.")
    except Exception as e:
        logging.error(f"Error adding mission: {e}")


def remove_mission(mission_id):
    """
    Remove mission from DB
    ### Parameters
    mission_id: id of mission to remove
    """
    try:
        # Attempt to find the mission by ID
        mission = Mission.objects.get(id=mission_id)
        mission.delete()  # Delete the found mission
        print(f"Mission with ID {mission_id} has been removed.")
    except Mission.DoesNotExist:
        print(f"No mission found with ID {mission_id}.")


def list_tags_by_mission(id):
    """
    List all Tags that belong to the same Mission

    Args:
        id: mission id
    """
    tags = Tag.objects.filter(mission_tags__mission_id=id).order_by("id")
    serializer = TagSerializer(tags, many=True)
    MissionCommand.print_table(serializer.data)


def add_tag_to_mission(id, tag_id=None, tag_name=None):
    """
    Either tag_id or tag_name must be given. If both are given it is checked, that they belong
    to the same Tag.

    Args:
        id: Mission id
        tag_id (optional): Tag id
        tag_name (optional): Tag name
    """
    # Input check
    if tag_id and tag_name:
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            logging.error(f"No Tag with id {tag_id} found")
            return
        if tag.name != tag_name:
            logging.error("Tag id and name given but dont match.")
            return

    if not (tag_id or tag_name):
        logging.error("At least one of --tag-id or --tag-name must be provided")
        return

    # Actual processing
    try:
        mission = Mission.objects.get(id=id)
        if tag_id:
            tag = Tag.objects.get(id=tag_id)
            created = False
        else:
            tag, created = Tag.objects.get_or_create(name=tag_name)
        mission_tag = Mission_tags(mission=mission, tag=tag)
        mission_tag.full_clean()
        mission_tag.save()

        # Output
        if created:
            logging.info(f"Tag '{tag.name}' created and tagged Mission with id {id}")
        else:
            logging.info(f"Tagged Mission with id {id} with '{tag.name}'")

    # Error handling
    except Mission.DoesNotExist:
        logging.error(f"No Mission with id {id} found")
    except Exception as e:
        logging.error(e)


def remove_tag_from_mission(id, tag_id=None, tag_name=None):
    """
    Either tag_id or tag_name must be given. If both are given it is checked, that they belong
    to the same Tag.

    Args:
        id: Mission id
        tag_id (optional): Tag id
        tag_name (_type_, optional): Tag name
    """
    # Input check
    if not (tag_id or tag_name):
        logging.error("At least one of --tag-id or --tag-name must be provided")
        return

    try:
        if tag_id and tag_name:
            tag = Tag.objects.get(id=tag_id)
            if tag.name != tag_name:
                logging.error("Tag id and name given but dont match.")
                return

        # Actual processing
        # using filter over get, because if for some reason the same Tag got added multiple times to the same Mission
        # filter will handle it properly, while get throws an error
        if tag_id:
            mission_tag = Mission_tags.objects.filter(mission_id=id, tag_id=tag_id)
        else:
            mission_tag = Mission_tags.objects.filter(mission_id=id, tag__name=tag_name)
        if not mission_tag.exists():
            raise Mission_tags.DoesNotExist
        mission_tag.delete()

        # Output
        tag = Tag.objects.filter(id=tag_id) | Tag.objects.filter(name=tag_name)
        tag = tag.first()
        logging.info(f"Removed Tag '{tag.name}' from Mission with id {id}")

    # Error handling
    except Mission.DoesNotExist:
        logging.error(f"No Mission with id {id} found")
    except Mission_tags.DoesNotExist:
        if tag_id:
            logging.error(f"No Tag with id {tag_id} found at Mission with id {id}")
        else:
            logging.error(
                f"No Tag with name '{tag_name}' found at Mission with id {id}"
            )
    except Tag.DoesNotExist:
        if tag_id:
            logging.error(f"No Tag with id {tag_id} found")
        else:
            logging.error(f"No Tag with name '{tag_name}' found")
