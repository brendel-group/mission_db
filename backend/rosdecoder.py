from pathlib import Path
import cv2
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

bagpath = Path(r"")

# Create a type store to use if the bag has no message definitions.
typestore = get_typestore(Stores.ROS2_FOXY)


def get_video_topics(path):
    with AnyReader([path], default_typestore=typestore) as reader:
        connections = [
            x.topic for x in reader.connections if x.msgtype == "sensor_msgs/msg/Image"
        ]

        return connections


def get_video_data(path, topic):
    data = []
    encoding = ""
    width = 0
    height = 0
    step = 0
    with AnyReader([bagpath], default_typestore=typestore) as reader:
        connections = [x for x in reader.connections if x.topic == topic]
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = reader.deserialize(rawdata, connection.msgtype)
            encoding = msg.encoding
            width = msg.width
            height = msg.height
            step = msg.step
            data.append(msg.data.reshape(height, width, int(step / width)))
    return data, topic


def create_video(data, topic):
    print(data)
    print(data[0].shape)
    height, width, channels = data[0].shape
    filename = str(topic).replace("/", "-") + ".mp4"
    print(filename)
    video = cv2.VideoWriter(
        filename,
        cv2.VideoWriter_fourcc(*"mp4v"),
        30,
        (width, height),
        isColor=channels == 3,
    )

    for frame in data:
        video.write(frame)

    video.release()


if __name__ == "__main__":
    topics = get_video_topics(bagpath)
    for topic in topics:
        data = get_video_data(bagpath, topic)
        create_video(data[0], data[1])
