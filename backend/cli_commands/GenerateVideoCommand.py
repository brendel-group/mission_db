from pathlib import Path
import cv2
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
import numpy as np
import os
from .Command import Command
from django.core.files.storage import FileSystemStorage, Storage
from restapi.models import File, Topic
from django.conf import settings
from .AddFolderCommand import extract_topics_from_mcap
import logging


class GenerateVideosCommand(Command):
    name = "generate-videos"

    def parser_setup(self, subparser):
        parser = subparser.add_parser(
            self.name, help="Generate Videos of all Topics with videos in a file"
        )

        parser.add_argument(
            "--path",
            required=True,
            help="Path to a mcap file",
            choices=File.objects.values_list("file", flat=True),
        )

    def command(self, args):
        generate_videos(args.path)


logger = logging.getLogger()


def generate_videos(path: str):
    """wrapper for generating videos and use django storages\\
    If the files are stored in the local filesystem, videos are directly generated there.\\
    If the files are in a remote storage (like S3) the files are copied to the TEMP_FOLDER,
    videos are generated there and are moved to the remote storage afterwards, cleans the TEMP_FOLDER.\\
    If it is preferred that the videos are kept in the local filesystem that can be achieved with the env var
    STORE_VIDEO_LOCALLY. They will be stored in the folder declared by VIDEO_ROOT.    

    Args:
        path (str): path to the mcap file
    """
    try:
        file = File.objects.get(file=path).file
    except File.DoesNotExist:
        logger.error(f"File not found: '{path}'")
        return []

    storage = File.file.field.storage

    local_storage, local_path = _get_file_from_external(storage, file)

    try:
        # generate videos
        topics = get_video_topics(local_path)
        topic_data = extract_topics_from_mcap(path, local_storage)
        video_paths: list[str] = []
        for topic in topics:
            filename = create_video_filename(topic, local_path)
            # skip existing videos
            if settings.STORE_VIDEO_LOCALLY:
                if local_storage.exists(filename):
                    continue
            else:
                if storage.exists(filename):
                    continue

            logger.info(f"Generating video for topic '{topic}'")
            data = get_video_data(local_path, topic)
            video_path = create_video(
                data, topic, local_path, topic_data[topic]["frequency"]
            )
            video_paths.append(video_path)

    except (FileNotFoundError, IsADirectoryError):
        logger.error(f"File not found: '{path}'")
        return []
    finally:
        _move_file_to_external(storage, local_storage, path, local_path, video_paths)

    logger.info("Succesfully generated all videos and moved files")
    return video_paths


def _get_file_from_external(
    external_storage: Storage, file: File
) -> tuple[Storage, Path]:
    """Checks if files are stored in a remote storage and moves them to
    the local Filesystem

    Args:
        external_storage (Storage): storage where to look for files
        file (File): File model object

    Returns:
        tuple[Storage, Path]: The storage where the files are accessible locally and the path to the folder
    """
    if isinstance(external_storage, FileSystemStorage):
        return external_storage, Path(os.path.dirname(file.path))

    if settings.STORE_VIDEO_LOCALLY:
        # generate videos directly in local folder
        local_storage = Topic.video.field.storage
    else:
        # generate videos in folder for temporary files
        local_storage = FileSystemStorage(settings.TEMP_FOLDER)

    metadata_path = os.path.dirname(file.name) + "/metadata.yaml"

    checksum_logger = logging.getLogger("botocore.httpchecksum")
    checksum_logger.disabled = True  # Disable checksum messages

    logger.info("Moving files to local storage")
    # Move files from remote storage to local filesystem
    with file.open() and external_storage.open(metadata_path) as metadata_file:
        local_storage.save(file.name, file)
        local_storage.save(metadata_path, metadata_file)

    checksum_logger.disabled = False

    local_path = Path(os.path.dirname(local_storage.path(file.name)))

    return local_storage, local_path


def _move_file_to_external(
    external_storage: Storage,
    local_storage: Storage,
    path: str,
    local_path: Path,
    video_paths: list[Path],
):
    """Moves the videos back to the remote storage if necessary and cleans the local Filesystem

    Args:
        external_storage (Storage): Where to move files to
        local_storage (Storage): Where to move files from
        path (str): Path to mcap file to delete
        local_path (Path): Path to local folder
        video_paths (list[Path]): videos which should be moved
    """
    if isinstance(external_storage, FileSystemStorage):
        return

    if settings.STORE_VIDEO_LOCALLY:
        # Delete mcap and metadata.yaml from local_storage
        local_storage.delete(path)
        local_storage.delete(local_path / "metadata.yaml")
        return

    logger.info("Moving videos to external storage")
    # Move videos to remote storage
    for video_path in video_paths:
        video_path = video_path[len(str(local_storage.location)) + 1 :]
        with local_storage.open(video_path) as file:
            external_storage.save(video_path, file)
    _delete_all(local_storage, path)


def _delete_all(storage: Storage, path: Path):
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


def create_video_filename(topic, save_dir):
    return os.path.join(save_dir, str(topic).replace("/", "-") + ".mp4")


def create_video(data, topic, save_dir, fps=30):
    # Print data and shape of the first frame for debugging
    height, width, channels = data[0].shape
    # Create a filename based on the topic name
    filename = create_video_filename(topic, save_dir)
    # Initialize the video writer
    video = cv2.VideoWriter(
        filename,
        cv2.VideoWriter_fourcc(*"avc1"),
        fps,
        (width, height),
        isColor=channels == 3,
    )

    # Write each frame to the video file
    for frame in data:
        video.write(frame)

    # Release the video writer
    video.release()

    return filename
