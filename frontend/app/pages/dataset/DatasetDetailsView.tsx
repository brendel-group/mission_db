import { Text } from "@mantine/core";
import { VideoComponent } from "./VideoView";

export function DatasetDetails({
  size,
  duration,
  videoUrl,
}: {
  size: string;
  duration: string;
  videoUrl: URL | null;
}) {
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
        <VideoComponent videoUrl={videoUrl} />
      </div>
    </div>
  );
}
