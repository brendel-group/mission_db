import { Text } from "@mantine/core";
import AbstractPage from "../AbstractPage";

// Interface describing expected properties of DatasetView
interface DatasetViewProps {
  file: string | null;
  fileUrl: URL | null;
  video: string | null;
  videoUrl: URL | null;
  duration: number | null;
  size: number | null;
  robot: string | null;
}

export function DatasetView(data: DatasetViewProps) {
  return (
    <AbstractPage headline="Dataset View">
      {data.file !== null ? (
        <div>
          <Text size="lg">File: {data.file}</Text>
          <Text size="lg">
            File download: <a href={String(data.fileUrl)}>download</a>
          </Text>
          <Text size="lg">Duration: {data.duration}</Text>
          <Text size="lg">Size: {data.size}</Text>
          <Text size="lg">Robot: {data.robot}</Text>
          <iframe
            width="320"
            height="320"
            src={String(data.videoUrl)}
            allowFullScreen
          ></iframe>
        </div>
      ) : (
        <Text>No data available</Text>
      )}
    </AbstractPage>
  );
}
