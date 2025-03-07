from datetime import datetime
from django.core.files.storage import DefaultStorage
from restapi.models import Mission, Tag, Mission_tags
from .Command import Command
from .AddFolderCommand import add_mission_from_folder
import json
import logging


class RestoreDatabaseCommand(Command):
    name = "restoredb"

    def parser_setup(self, subparser):
        _ = subparser.add_parser(
            self.name,
            help="Adds missing missions and saves the metadata from the JSON files into the database.",
        )

    def command(self, args):
        confirmation = input(
            "This will overwrite the metadata in the database. Are you sure? [y/N]: "
        )
        if confirmation.lower() != "y":
            print("Aborted")
            return
        restore_database()


storage = DefaultStorage()


def restore_database():
    fs_mission_set = set(storage.listdir("")[0])

    for folder in fs_mission_set:
        try:
            mission_date, mission_name = folder.split("_", 1)
            mission_date = datetime.strptime(mission_date, "%Y.%m.%d").date()
            if f"{mission_name}_metadata.json" not in storage.listdir(folder)[1]:
                continue
            metadata_file = f"{folder}/{mission_name}_metadata.json"
            with storage.open(metadata_file, "r") as f:
                metadata = json.load(f)

            if not Mission.objects.filter(
                date=mission_date, name=mission_name
            ).exists():
                add_mission_from_folder(folder, None, None)
            mission = Mission.objects.get(date=mission_date, name=mission_name)
            location = metadata.get("location")
            notes = metadata.get("notes")
            tags_data = metadata.get("tags", [])

            # Update mission details if not created
            mission.location = location
            mission.notes = notes
            mission.save()

            # overwrite Mission_tags and Tags with the ones from the metadata
            Mission_tags.objects.filter(mission=mission).delete()
            for tag in tags_data:
                tag_name = tag.get("name")
                tag_color = tag.get("color")
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name, color=tag_color)
                Mission_tags.objects.create(mission=mission, tag=tag_obj)

            logging.info(f"restored metadata from json file for mission {mission_name}")
        except Exception as e:
            logging.error(f"Error restoring metadata for folder {folder}: {e}")
            continue
