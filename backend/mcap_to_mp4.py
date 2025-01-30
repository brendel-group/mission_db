import os
from mcap.reader import make_reader
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import numpy as np
import cv2


def decode_bgr8(raw_data, width, height):
    """
    Decodes raw BGR8 image data into a NumPy array.

    Args:
        raw_data (bytes): Raw BGR8 image data.
        width (int): Image width.
        height (int): Image height.

    Returns:
        numpy.ndarray: Decoded image.
    """
    # ensure the size matches width * height * 3 (for BGR channels)
    expected_size = width * height * 3
    if len(raw_data) != expected_size:
        print(f"Unexpected frame size: {len(raw_data)} (expected {expected_size})")
        return None

    # reshape the data into a (height, width, 3) array
    bgr = np.frombuffer(raw_data, np.uint8).reshape((height, width, 3))
    # convert bgr to rgb
    rgb = bgr[:, :, ::-1]
    return rgb


def extract_mcap_data(mcap_file):
    """
    Extracts audio and video data from an MCAP file.

    Args:
        mcap_file (str): Path to the MCAP file.

    Returns:
        list of frames
    """
    frames = []
    width, height = 224, 224

    with open(mcap_file, "rb") as f:
        reader = make_reader(f)
        for schema, channel, message in reader.iter_messages():
            # process video frames
            if channel.topic == "/camera/argus/image":
                # extract image data from BGR8 byte string (removing header)
                frame_data = message.data[message.data.find(b"bgr8") + 16 :]
                np_arr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                # if decoding fails, assume raw BGR8
                if frame is None:
                    frame = decode_bgr8(frame_data, width, height)

                if frame is not None:
                    frames.append(frame)
                else:
                    print("Failed to decode a frame")

    print(f"Number of video frames extracted: {len(frames)}")

    return frames


def convert_mcap_to_mp4(mcap_file, output_file):
    """
    Converts an MCAP file to an MP4 file.

    Args:
        mcap_file (str): Path to the MCAP file.
        output_file (str): Path to the output MP4 file.
    """
    frames = extract_mcap_data(mcap_file)

    # save video frames as an MP4 file
    if frames:
        clip = ImageSequenceClip(frames, fps=30)
        clip.write_videofile(output_file, codec="libx264")


if __name__ == "__main__":
    mcap_file = r""  # MCAP file path
    output_file = r".\output.mp4"  # path of output path

    if not os.path.exists(mcap_file):
        print(f"MCAP file not found: {mcap_file}")
    else:
        convert_mcap_to_mp4(mcap_file, output_file)
        print(f"MP4 file saved: {output_file}")
