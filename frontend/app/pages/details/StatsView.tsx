import { Text } from "@mantine/core";
import { RenderedMission } from "~/data";

interface ShowStatsViewProps {
  missionData: RenderedMission | null;
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
      <Text>
        Notes: {missionData.notes === null ? "None" : missionData.notes}
      </Text>
    </div>
  );
};
