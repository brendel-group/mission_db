import { Modal, Text } from "@mantine/core";
import React from "react";
import { MissionData } from "~/data";

interface RenderViewProps {
  modalOpened: boolean;
  selectedRow: MissionData | null;
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
            <strong>Total Duration:</strong> {selectedRow.total_duration}
          </Text>
          <Text>
            <strong>Total Size:</strong> {selectedRow.total_size}
          </Text>
          <Text>
            <strong>Robot:</strong> {selectedRow.robot}
          </Text>
          <Text>
            <strong>Remarks:</strong> {selectedRow.remarks}
          </Text>
        </div>
      )}
    </Modal>
  );
};

export default RenderView;
