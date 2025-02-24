from pathlib import Path
import cv2
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
import numpy as np
import os
from mcap.reader import make_reader

bagpath = r""

# Create a type store to use if the bag has no message definitions.
typestore = get_typestore(Stores.ROS2_FOXY)


def extract_topics_from_mcap(mcap_path):
    with open(mcap_path, "rb") as f:
        reader = make_reader(f)
        summary = reader.get_summary()
        schema_map = {schema.id: schema.name for schema in summary.schemas.values()}
        channel_message_counts = summary.statistics.channel_message_counts
        duration = get_duration_from_mcap(mcap_path)
        topic_info = {
            channel.topic: {
                "type": schema_map.get(channel.schema_id, "Unknown"),
                "message_count": channel_message_counts.get(channel.id, 0),
                "frequency": 0
                if duration == 0
                else channel_message_counts.get(channel.id, 0) / (duration * 10**-9),
            }
            for channel in summary.channels.values()
        }
        return topic_info


def get_duration_from_mcap(mcap_path):
    with open(mcap_path, "rb") as f:
        reader = make_reader(f)
        statistics = reader.get_summary().statistics
        return statistics.message_end_time - statistics.message_start_time


def get_video_topics(mcap_path):
    topics = extract_topics_from_mcap(mcap_path)
    video_topics = [
        topic for topic in topics if topics[topic]["type"] == "sensor_msgs/msg/Image"
    ]
    return video_topics


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
    base_path = Path("\\".join(bagpath.split("\\")[:-1]))
    topics = get_video_topics(bagpath)
    print(topics)
    for topic in topics:
        data = get_video_data(base_path, topic)
        create_video(data[0], data[1], base_path)
