import { Modal, Text } from "@mantine/core";
import React from "react";
import { RowData } from "./Overview";

interface RenderViewProps {
  modalOpened: boolean;
  selectedRow: RowData | null;
  onClose: () => void;
}

const RenderView: React.FC<RenderViewProps> = ({
  modalOpened,
  selectedRow,
  onClose,
}) => {
  return (
    <Modal
      opened={modalOpened}
      onClose={onClose}
      title={
        selectedRow ? `Details for ${selectedRow.name}` : "Mission Details"
      }
      size="100%"
      styles={{
        content: {
          borderRadius: "20px",
          height: "90vh",
        },
      }}
    >
      {selectedRow && (
        <div>
          <Text>
            <strong>Location:</strong> {selectedRow.location}
          </Text>
          <Text>
            <strong>Duration:</strong> {selectedRow.duration}
          </Text>
          <Text>
            <strong>Size:</strong> {selectedRow.size}
          </Text>
          <Text>
            <strong>Robot:</strong> {selectedRow.robot}
          </Text>
          <Text>
            <strong>Tags:</strong> {selectedRow.tags.join(", ")}
          </Text>
        </div>
      )}
    </Modal>
  );
};

export default RenderView;
