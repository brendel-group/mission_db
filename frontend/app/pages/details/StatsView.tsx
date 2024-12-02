import { Text } from "@mantine/core";
import { MissionData } from "~/data";

interface ShowStatsViewProps {
  missionData: MissionData | null;
}

export const ShowStatsView: React.FC<ShowStatsViewProps> = ({
  missionData,
}) => {
  if (!missionData) return null;

  return (
    <div>
      <Text size="xl" mb="sm">
        Stats
      </Text>
      <Text>Total Duration: {missionData.totalDuration}</Text>
      <Text>Total Size: {missionData.totalSize} GB</Text>
      <Text>Remarks: {missionData.remarks}</Text>
    </div>
  );
};
