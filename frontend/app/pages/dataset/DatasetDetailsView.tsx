import { Text } from "@mantine/core";
import { VideoComponent } from "./video/VideoView";
import { Topic } from "~/data";
import { useState } from "react";

export function DatasetDetails({
  size,
  duration,
  topics,
}: {
  size: string;
  duration: string;
  topics: Topic[];
}) {
  const [videoIndex, setVideoIndex] = useState<number>(0);

  // Identify valid videos
  const videos: { topic: string; videoUrl: string }[] = [];

  for (const topic of topics)
    if (topic.video_path && topic.video_url)
      videos.push({ topic: topic.name, videoUrl: topic.video_url });

  return (
    <div>
      <Text size="xl" mb="sm">
        Details
      </Text>
      <Text>
        <strong>Size:</strong> {size}
      </Text>
      <Text>
        <strong>Duration:</strong> {duration}
      </Text>
      <Text>
        <strong>Video:</strong>
      </Text>
      <div style={{ marginTop: "8px" }}>
        {videos.length === 0 ? (
          <VideoComponent topicName={null} videoUrl={null} />
        ) : (
          <VideoComponent
            topicName={videos[videoIndex].topic}
            videoUrl={new URL(videos[videoIndex].videoUrl)}
            onLeftClick={() =>
              setVideoIndex(
                (prev) => (prev - 1 + videos.length) % videos.length
              )
            }
            onRightClick={() =>
              setVideoIndex((prev) => (prev + 1) % videos.length)
            }
          />
        )}
      </div>
    </div>
  );
}
