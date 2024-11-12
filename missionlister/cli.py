import os
import argparse
import django
import logging
from datetime import datetime
from restapi.models import Mission  # Importing Models, adjust as needed

# Set up Django env
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "missionlister.settings"
)  # Adjust as needed
django.setup()

# Set up logging
logging.basicConfig(level=logging.INFO)


# Extract date and name from folder name
def extract_info_from_folder(folder_name):
    try:
        date_str, name = folder_name.split("_", 1)
        date_str = convert_date(date_str)
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date, name
    except ValueError:
        logging.error(
            f"Folder name '{folder_name}' does not match the expected format (YYYY-MM-DD_missionname)."
        )
        return None, None


# Check if mission exists
def check_mission_exists(id):
    return Mission.objects.filter(id=id).exists()


# Validate datetime format
def validate_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        logging.error("Date and time format should be YYYY-MM-DD.")
        return None


# Add mission to DB
def add_mission_from_folder(id, folder_path, location, other):
    folder_name = os.path.basename(folder_path)
    date, name = extract_info_from_folder(folder_name)

    if date and name:
        mission = Mission(id=id, name=name, date=date, location=location, other=other)
        try:
            mission.save()
            logging.info(f"Mission '{name}' from folder '{folder_name}' added.")
        except Exception as e:
            logging.error(f"Error adding mission: {e}")
    else:
        logging.warning("Skipping folder due to naming issues.")


# Add mission to DB
def add_mission(id, name, date, location, other):
    if check_mission_exists(id):
        logging.warning(f"'{name}' on '{date}' with Id'{id}' already exists.")
        return

    try:
        mission = Mission(id=id, name=name, date=date, location=location, other=other)
        mission.save()
        logging.info(f"'{name}' added.")
    except Exception as e:
        logging.error(f"Error adding mission: {e}")


def remove_mission(mission_id):
    try:
        # Attempt to find the mission by ID
        mission = Mission.objects.get(id=mission_id)
        mission.delete()  # Delete the found mission
        print(f"Mission with ID {mission_id} has been removed.")
    except Mission.DoesNotExist:
        print(f"No mission found with ID {mission_id}.")


def convert_date(date):
    return date.replace(".", "-")


def main():
    # Arg parser
    parser = argparse.ArgumentParser(description="Mission CLI")
    subparser = parser.add_subparsers(dest="command")

    # Add command
    add_parser = subparser.add_parser("add", help="Add mission")
    add_parser.add_argument("--id", required=True, help="ID")
    add_parser.add_argument("--name", required=True, help="Mission name")
    add_parser.add_argument("--date", required=True, help="Mission date (YYYY-MM-DD)")
    add_parser.add_argument(
        "--location", required=False, help="Mission location", default="unknown"
    )
    add_parser.add_argument(
        "--other", required=False, help="Other mission details", default="-"
    )

    # remove command
    remove_parser = subparser.add_parser("remove", help="Remove mission")
    remove_parser.add_argument("--id", required=True, help="ID")

    folder_parser = subparser.add_parser("addfolder", help="adds details from folder")
    folder_parser.add_argument("--id", required=True, help="ID")
    folder_parser.add_argument("--path", required=True, help="Filepath")
    folder_parser.add_argument(
        "--location", required=False, help="location", default="unknown"
    )
    folder_parser.add_argument(
        "--other", required=False, help="other mission details", default="-"
    )

    args = parser.parse_args()

    # Execute command
    if args.command == "add":
        # Validate date
        validated_date = validate_date(args.date)
        if validated_date is None:
            return

        add_mission(
            args.id,
            args.name,
            validated_date,  # Pass the validated date
            args.location,
            args.other,
        )
    elif args.command == "remove":
        remove_mission(args.id)
    elif args.command == "addfolder":
        add_mission_from_folder(args.id, args.path, args.location, args.other)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
