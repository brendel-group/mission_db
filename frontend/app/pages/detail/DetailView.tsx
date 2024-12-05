import { Container, Grid, Text, rem } from "@mantine/core";
import React from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { ShowStatsView } from "./StatsView";
import { MissionData } from "~/data";
import { detail_view_data } from "~/RandomData";

interface DetailsViewProps {
  missionData: MissionData | null;
}

const DetailView: React.FC<DetailsViewProps> = ({ missionData: selectedRow }) => {
  const detailViewData = selectedRow
    ? detail_view_data[selectedRow.missionId]
    : null;

  return (
    <Container
      my="md"
      style={{
        maxWidth: "100%", // Aligns it to the left
        padding: "0 1rem", // Adds padding to the container
      }}
    >
      {/* Title */}
      <Text
        size={rem(30)}
        style={{ marginBottom: "1rem" }}
      >
        {selectedRow
          ? `${selectedRow.name}, ${selectedRow.location} with ${selectedRow.robot}`
          : "Mission Details"}
      </Text>

      {/* Main content */}
      <Grid gutter="md">
        {/* Left column occupying 80% */}
        <Grid.Col span={9}>
          <Grid gutter="md">
            {/* Tags */}
            <Grid.Col span={12}>
              {selectedRow && (
                <RenderTagsDetailView tags={selectedRow.tags} />
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
    </Container>
  );
};

export default DetailView;
