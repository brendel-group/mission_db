from pathlib import Path
import cv2
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
import numpy as np
import os
import yaml

bagpath = Path(r"")

# Create a type store to use if the bag has no message definitions.
typestore = get_typestore(Stores.ROS2_FOXY)


def read_yaml_file(file_path):
    file_path = str(file_path) + r"\metadata.yaml"
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def parse_rosbag_info(file_path):
    data = read_yaml_file(file_path)
    duration_ns = (
        data.get("rosbag2_bagfile_information", {})
        .get("duration", {})
        .get("nanoseconds", 0)
    )
    topics = data.get("rosbag2_bagfile_information", {}).get(
        "topics_with_message_count", []
    )

    topic_msgcount = {}
    for topic in topics:
        topic_name = topic.get("topic_metadata", {}).get("name", "Unknown")
        message_count = topic.get("message_count", 0)
        topic_msgcount[topic_name] = message_count

    duration_s = duration_ns / 1e9
    topic_frequency = {}
    for topic in topic_msgcount:
        topic_frequency[topic] = round(topic_msgcount[topic] / duration_s, 2)
    print(duration_s, topic_msgcount, topic_frequency)
    return duration_s, topic_msgcount, topic_frequency


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
    with AnyReader([bagpath], default_typestore=typestore) as reader:
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

    return data, topic


def create_video(data, topic, save_dir=str(bagpath)):
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


if __name__ == "__main__":
    topics = get_video_topics(bagpath)
    parse_rosbag_info(bagpath)
    for topic in topics:
        data = get_video_data(bagpath, topic)
        create_video(data[0], data[1])
