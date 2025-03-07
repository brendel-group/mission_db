from .Command import Command
from restapi.models import Denied_topics, Topic
import logging


class TopicCommand(Command):
    name = "topic"

    def parser_setup(self, subparser):
        self.topic_parser = subparser.add_parser(self.name, help="Modify denied topics")
        topic_subparser = self.topic_parser.add_subparsers(dest=self.name)

        # list-denied command
        topic_subparser.add_parser("list-denied", help="List denied topic names")

        # allow command
        allow_parser = topic_subparser.add_parser(
            "allow", help="Remove topic name from denied names"
        )
        allow_parser.add_argument("name", help="topic name")

        # deny command
        deny_parser = topic_subparser.add_parser(
            "deny", help="Add topic name to denied names"
        )
        deny_parser.add_argument("name", help="topic name")

    def command(self, args):
        match args.topic:
            case "allow":
                remove_denied_topic(args.name)
            case "deny":
                add_denied_topic(args.name)
            case "list-denied":
                self.print_table(Denied_topics.objects.values())
            case _:
                self.topic_parser.print_help()


def remove_denied_topic(name: str):
    """remove a topic from the Denied_topics table

    Args:
        name (str): topic name
    """
    try:
        denied_topic = Denied_topics.objects.get(name=name)
    except Denied_topics.DoesNotExist:
        logging.info(f"'{name}' not found in denied topic names")
        return

    denied_topic.delete()
    logging.info(f"Removed '{name}' from denied topic names")


def add_denied_topic(name: str):
    """add a topic to the Denied_topics table and remove all topics with that name

    Args:
        name (str): topic name
    """
    try:
        denied_topic = Denied_topics.objects.create(name=name)
        denied_topic.full_clean()
    except Exception as e:
        logging.error(e)
        return

    # remove all topics that have this name
    topics = Topic.objects.filter(name=name)

    if topics.exists():
        try:
            topics.delete()
        except Exception as e:
            logging.error(e)
    logging.info(f"Topic name '{name}' will be denied from now on")
