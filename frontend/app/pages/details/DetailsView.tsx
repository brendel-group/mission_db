import { Grid } from "@mantine/core";
import React from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { ShowStatsView } from "./StatsView";
import { RenderedMission } from "~/data";
import AbstractPage from "../AbstractPage";

interface DetailsViewProps {
  missionData: RenderedMission;
}

const DetailsView: React.FC<DetailsViewProps> = ({
  missionData: selectedRow,
}) => {
  const detailViewData = {
    files: ["file1.mcap", "file2.mcap", "file3.mcap"],
    durations: ["00:01:30", "00:02:45", "00:00:50"],
    sizes: ["2000", "4500", "1000"],
  };

  return (
    <AbstractPage
      headline={
        selectedRow
          ? `${selectedRow.name}${
              selectedRow.location ? `, ${selectedRow.location}` : ""
            }${selectedRow.robot ? ` with ${selectedRow.robot}` : ""}`
          : "Mission Details"
      }
    >
      {/* Main content */}
      <Grid gutter="md">
        {/* Left column occupying 80% */}
        <Grid.Col span={9}>
          <Grid gutter="md">
            {/* Tags */}
            <Grid.Col span={12}>
              {selectedRow && (
                <RenderTagsDetailView
                  tags_={selectedRow.tags}
                  missionId={selectedRow.id}
                />
              )}
            </Grid.Col>
            {/* Table */}
            <Grid.Col span={12}>
              {detailViewData && <ShowDatasets data={detailViewData} />}
            </Grid.Col>
          </Grid>
        </Grid.Col>

        {/* Stats */}
        <Grid.Col span={3}>
          <ShowStatsView missionData={selectedRow} />
        </Grid.Col>
      </Grid>
    </AbstractPage>
  );
};

export default DetailsView;
