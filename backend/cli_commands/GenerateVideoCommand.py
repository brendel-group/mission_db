from pathlib import Path
import cv2
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
import numpy as np
import os
from .Command import Command
from django.core.files.storage import FileSystemStorage, Storage
from restapi.models import File
from django.conf import settings
import logging


class GenerateVideosCommand(Command):
    name = "generate-videos"

    def parser_setup(self, subparser):
        parser = subparser.add_parser(
            self.name, help="Generate Videos of all Topics with videos in a file"
        )

        parser.add_argument(
            "--path", required=True, type=Path, help="Path to folder with mcap file"
        )

    def command(self, args):
        generate_videos(args.path)


def generate_videos(path):
    file = File.objects.get(file=path).file
    storage = File.file.field.storage

    if isinstance(storage, FileSystemStorage):
        local_path = Path(os.path.dirname(file.path))
        local_storage = storage
    else:
        local_storage = FileSystemStorage(settings.TEMP_FOLDER)
        metadata_path = os.path.dirname(file.name) + "/metadata.yaml"

        logger = logging.getLogger("botocore.httpchecksum")
        logger.disabled = True  # Disable checksum messages

        # Move files from remote storage to local filesystem
        with file.open() and storage.open(metadata_path) as metadata_file:
            local_storage.save(file.name, file)
            local_storage.save(metadata_path, metadata_file)
        logger.disabled = False

        local_path = Path(os.path.dirname(local_storage.path(file.name)))

    try:
        topics = get_video_topics(local_path)
        video_paths: list[str] = []
        for topic in topics:
            data = get_video_data(local_path, topic)
            video_path = create_video(data, topic, local_path)
            video_paths.append(video_path)

    finally:
        if isinstance(storage, FileSystemStorage):
            return
        # Move videos to remote storage
        for video_path in video_paths:
            video_path = video_path[len(str(local_storage.location)) + 1 :]
            with local_storage.open(video_path) as file:
                storage.save(video_path, file)
        delete_all(local_storage, path)


def delete_all(storage: Storage, path: Path):
    """Delete all files and folders created by video generation
    Starts by deleting all files in the folder where the videos where created
    Moves up and deletes the folder until it hits a non empty folder or base folder.

    Args:
        storage (Storage): the storage where to delete files from
        path (Path): the path to the deepest file (ex: example/test/bag123/bag123.mcap)
    """
    parent = os.path.dirname(str(path))
    _, files = storage.listdir(parent)
    for file in files:
        storage.delete(os.path.join(parent, file))

    while parent:
        try:
            storage.delete(parent)
        except OSError:
            return
        parent = os.path.dirname(parent)


# Create a type store to use if the bag has no message definitions.
typestore = get_typestore(Stores.ROS2_FOXY)


def get_video_topics(path):
    # Open the bag file using AnyReader
    with AnyReader([path], default_typestore=typestore) as reader:
        # Extract topics that have message type "sensor_msgs/msg/Image"
        connections = [
            x.topic for x in reader.connections if x.msgtype == "sensor_msgs/msg/Image"
        ]

        return connections


def get_video_data(path, topic):
    data = []
    width = 0
    height = 0
    step = 0
    # Open the bag file using AnyReader
    with AnyReader([path], default_typestore=typestore) as reader:
        # Filter connections for the specified topic
        connections = [x for x in reader.connections if x.topic == topic]
        # Iterate through messages in the filtered connections
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            # Deserialize the raw data to get the message
            msg = reader.deserialize(rawdata, connection.msgtype)
            width = msg.width
            height = msg.height
            step = msg.step
            if msg.encoding == "mono16":
                # Convert raw bytes to numpy 16-bit grayscale image
                tmp = np.frombuffer(msg.data, dtype=np.uint16).reshape(
                    (height, width, 1)
                )

                # Normalize to 8-bit range (0-255) for visualization
                normalized = (tmp / 256).astype(np.uint8)

                data.append(normalized)
            else:
                # Normal RGB or Mono8 case
                data.append(
                    np.frombuffer(msg.data, dtype=np.uint8).reshape(
                        height, width, int(step / width)
                    )
                )

    return data


def create_video(data, topic, save_dir):
    # Print data and shape of the first frame for debugging
    height, width, channels = data[0].shape
    # Create a filename based on the topic name
    filename = os.path.join(
        save_dir, str(topic).replace("/", "-") + ".mp4"
    )  # Initialize the video writer
    video = cv2.VideoWriter(
        filename,
        cv2.VideoWriter_fourcc(*"mp4v"),
        30,
        (width, height),
        isColor=channels == 3,
    )

    # Write each frame to the video file
    for frame in data:
        video.write(frame)

    # Release the video writer
    video.release()

    return filename
