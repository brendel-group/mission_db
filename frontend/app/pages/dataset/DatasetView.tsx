import { Modal, Text } from "@mantine/core";

// Interface describing expected properties of DatasetView
interface DatasetViewProps {
  opened: boolean;
  onClose: () => void;
  file: string | null;
  duration: string | null;
  size: string | null;
}

export function DatasetView({
  opened,
  onClose,
  file,
  duration,
  size,
}: DatasetViewProps) {
  //Create a modal view for the dataset
  return (
    <Modal
      opened={opened}
      onClose={onClose}
      fullScreen
      title={"Dataset View"}
      styles={{
        title: {
          fontSize: "30px",
        },
      }}
    >
      {file !== null ? (
        <div>
          <Text size="lg">File: {file}</Text>
          <Text size="lg">Duration: {duration}</Text>
          <Text size="lg">Size: {size} MB</Text>
        </div>
      ) : (
        <Text>No details available</Text>
      )}
    </Modal>
  );
}
