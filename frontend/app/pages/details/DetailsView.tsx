import { Modal, Container, Grid, Text, rem } from "@mantine/core";
import React from "react";
import { RenderTagsDetailsView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { ShowStatsView } from "./StatsView";
import { MissionData } from "~/data";
import { detail_view_data } from "~/RandomData";

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
  const detailViewData = selectedRow
    ? detail_view_data[selectedRow.mission_id]
    : null;

  return (
    <Modal
      opened={modalOpened}
      onClose={onClose}
      title={
        selectedRow
          ? `${selectedRow.name}, ${selectedRow.location} with ${selectedRow.robot}`
          : "Mission Details"
      }
      fullScreen
      styles={{
        title: {
          fontSize: "30px",
        },
      }}
    >
      <Container my="md" mx={0} px={0}>
        <Grid gutter="md">
          {/* Left column occupying 80% */}
          <Grid.Col span={9}>
            <Grid>
              {/* Tags */}
              <Grid.Col span={12}>
                {selectedRow && (
                  <RenderTagsDetailsView tags={selectedRow.tags} />
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
            <ShowStatsView selectedRow={selectedRow} />
          </Grid.Col>
        </Grid>
      </Container>
    </Modal>
  );
};

export default RenderView;
