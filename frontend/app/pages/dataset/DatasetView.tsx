import { Text } from "@mantine/core";
import AbstractPage from "../AbstractPage";

// Interface describing expected properties of DatasetView
interface DatasetViewProps {
  file: string | null;
  fileUrl: URL | null;
  video: string | null;
  videoUrl: URL | null;
  duration: string | null;
  size: string | null;
  robot: string | null;
  topics: string[] | null;
}

export function DatasetView(data: DatasetViewProps) {
  return (
    <AbstractPage headline="Dataset View">
      {data.file !== null ? (
        <div>
          <Text size="lg">File: {data.file}</Text>
          <Text size="lg">
            File download: <a href={String(data.fileUrl)}>download</a>{" "}
            <a
              href={
                "foxglove://open?ds=remote-file&ds.url=" + String(data.fileUrl)
              }
            >
              open in Foxglove
            </a>
          </Text>
          <Text size="lg">Duration: {data.duration}</Text>
          <Text size="lg">Size: {data.size}</Text>
          <Text size="lg">Robot: {data.robot}</Text>
          <Text size="lg">Topics: {data.topics ? data.topics.join(", ") : "No topics available"}</Text>
          <Text size="lg">Video:</Text>
          {data.video ? (
            <iframe
              width="320"
              height="320"
              src={String(data.videoUrl)}
              allowFullScreen
            ></iframe>
          ) : (
            <Text size="lg">No video available</Text>
          )}
        </div>
      ) : (
        <Text>No data available</Text>
      )}
    </AbstractPage>
  );
}
