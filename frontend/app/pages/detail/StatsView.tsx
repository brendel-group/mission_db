import { Text } from "@mantine/core";
import { MissionData } from "~/data";

interface ShowStatsViewProps {
  selectedRow: MissionData | null;
}

export const ShowStatsView: React.FC<ShowStatsViewProps> = ({
  selectedRow,
}) => {
  if (!selectedRow) return null;

  return (
    <div>
      <Text size="xl" mb="sm">
        Stats
      </Text>
      <Text>Total Duration: {selectedRow.totalDuration}</Text>
      <Text>Total Size: {selectedRow.totalSize} GB</Text>
      <Text>Remarks: {selectedRow.remarks}</Text>
    </div>
  );
};
