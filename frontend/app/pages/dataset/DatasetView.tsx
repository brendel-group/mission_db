import { Container, Text } from "@mantine/core";
import { rem } from "@mantine/core";

// Interface describing expected properties of DatasetView
interface DatasetViewProps {
  file: string | null;
  duration: string | null;
  size: string | null;
}

export function DatasetView({ file, duration, size }: DatasetViewProps) {
  return (
    <Container
      my="md"
      style={{
        maxWidth: "100%", // Aligns it to the left
        padding: "0 1rem", // Adds padding to the container
      }}
    >
      <Text
        size={rem(30)}
        style={{ marginBottom: "1rem" }}
      >
        Dataset View
      </Text>
      {file !== null ? (
        <div>
          <Text size="lg">File: {file}</Text>
          <Text size="lg">Duration: {duration}</Text>
          <Text size="lg">Size: {size} MB</Text>
        </div>
      ) : (
        <Text>No details available</Text>
      )}
    </Container>
  );
}
