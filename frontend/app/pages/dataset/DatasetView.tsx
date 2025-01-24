import { Text } from "@mantine/core";
import AbstractPage from "../AbstractPage";

// Interface describing expected properties of DatasetView
interface DatasetViewProps {
  file: string | null;
  duration: string | null;
  size: string | null;
}

export function DatasetView({ file, duration, size }: DatasetViewProps) {
  return (
    <AbstractPage headline="Dataset View">
      {file !== null ? (
        <div>
          <Text size="lg">File: {file}</Text>
          <Text size="lg">Duration: {duration}</Text>
          <Text size="lg">Size: {size}</Text>
        </div>
      ) : (
        <Text>No data available</Text>
      )}
    </AbstractPage>
  );
}
