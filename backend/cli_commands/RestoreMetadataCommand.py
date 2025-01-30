from datetime import datetime
from django.core.files.storage import DefaultStorage
from restapi.models import Mission, Tag, Mission_tags
from .Command import Command
import json
import logging


class RestoreMetadataCommand(Command):
    name = "restoremetadata"

    def parser_setup(self, subparser):
        _ = subparser.add_parser(
            self.name, help="saves the metadata from the JSON files in the database"
        )

    def command(self, args):
        restore_metadata()


storage = DefaultStorage()


def restore_metadata():
    fs_mission_set = set(storage.listdir("")[0])

    for folder in fs_mission_set:
        try:
            mission_date, mission_name = folder.split("_", 1)
            mission_date = datetime.strptime(mission_date, "%Y.%m.%d").date()
            metadata_file = f"{folder}/{mission_name}_metadata.json"
            with DefaultStorage().open(metadata_file, "r") as f:
                metadata = json.load(f)

            mission = Mission.objects.get(name=mission_name, date=mission_date)
            location = metadata.get("location")
            notes = metadata.get("notes")
            tags_data = metadata.get("tags", [])

            # Update mission details if not created
            mission.location = location
            mission.notes = notes
            mission.save()

            # Process tags
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(
                    name=tag_data["name"], color=tag_data["color"]
                )
                Mission_tags.objects.get_or_create(mission=mission, tag=tag)

            logging.info(f"restored metadata from json file for mission {mission_name}")
        except Exception as e:
            logging.error(f"Error restoring metadata for folder {folder}: {e}")
            continue
