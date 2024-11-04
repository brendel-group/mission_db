import os
import sys
import argparse
import django
import logging
from datetime import datetime

# Set up Django env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'missionlister.settings')  # Adjust as needed
django.setup()

# Import model
from restapi.models import Mission  # Adjust as needed

# Set up logging
logging.basicConfig(level=logging.INFO)

# Check if mission exists
def check_mission_exists(id):
    return Mission.objects.filter(id=id).exists()

# Validate datetime format
def validate_datetime(datetime_str):
    try:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        logging.error("Date and time format should be YYYY-MM-DD HH:MM:SS.")
        return None

# Add mission to DB
def add_mission(id, name, date, location, other):
    if check_mission_exists(id):
        logging.warning(f"'{name}' on '{date}' with Id'{id}' already exists.")
        return

    try:
        mission = Mission(
            id=id,
            name=name,
            date=date,
            location=location,
            other=other
        )
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


def main():
    # Arg parser
    parser = argparse.ArgumentParser(description="Mission CLI")
    subparser = parser.add_subparsers(dest="command")

    # Add command
    add_parser = subparser.add_parser("add", help="Add mission")
    add_parser.add_argument("--id", required=True, help="ID")
    add_parser.add_argument("--name", required=True, help="Mission name")
    add_parser.add_argument("--datetime", required=True, help="Mission date and time (YYYY-MM-DD HH:MM:SS)")
    add_parser.add_argument("--location", required=True, help="Mission location")
    add_parser.add_argument("--other", required=True, help="Other mission details")

    #remove command
    remove_parser = subparser.add_parser("remove", help="Remove mission")
    remove_parser.add_argument("--id", required=True, help="ID")

    args = parser.parse_args()

    

    # Execute command
    if args.command == "add":
        # Validate datetime
        validated_datetime = validate_datetime(args.datetime)
        if validated_datetime is None:
            return
        
        add_mission(
            args.id,
            args.name,
            validated_datetime,  # Pass the validated datetime
            args.location,
            args.other
        )
    elif args.command == "remove":
        remove_mission(args.id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()