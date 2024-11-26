import { Modal, Container, Grid, Text, rem } from "@mantine/core";
import React from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { ShowStatsView } from "./StatsView";
import { MissionData } from "~/data";
import { detail_view_data } from "~/RandomData";

interface DetailViewProps {
  modalOpened: boolean;
  missionData: MissionData | null;
  onClose: () => void;
}

const RenderView: React.FC<DetailViewProps> = ({
  modalOpened,
  missionData,
  onClose,
}) => {
  const detailViewData = missionData
    ? detail_view_data[missionData.missionId]
    : null;

  return (
    <Modal
      opened={modalOpened}
      onClose={onClose}
      title={
        missionData
          ? `${missionData.name}, ${missionData.location} with ${missionData.robot}`
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
                {missionData && (
                  <RenderTagsDetailView tags={missionData.tags} />
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
            <ShowStatsView selectedRow={missionData} />
          </Grid.Col>
        </Grid>
      </Container>
    </Modal>
  );
};

export default RenderView;
