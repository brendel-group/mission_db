import { Grid } from "@mantine/core";
import React from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { ShowStatsView } from "./StatsView";
import { MissionData } from "~/data";
import { detail_view_data } from "~/RandomData";
import AbstractPage from "../AbstractPage";

interface DetailsViewProps {
  missionData: MissionData | null;
}

const DetailsView: React.FC<DetailsViewProps> = ({
  missionData: selectedRow,
}) => {
  const detailViewData = selectedRow
    ? detail_view_data[selectedRow.missionId]
    : null;

  return (
    <AbstractPage
      headline={
        selectedRow
          ? `${selectedRow.name}, ${selectedRow.location} with ${selectedRow.robot}`
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
                  missionId={selectedRow.missionId}
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
