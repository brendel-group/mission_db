import { Grid } from "@mantine/core";
import React, { useState } from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { ShowInformationView } from "./InformationView";
import { MissionData } from "~/data";
import { detail_view_data } from "~/RandomData";
import AbstractPage from "../AbstractPage";

interface DetailsViewProps {
  missionData: MissionData;
}

const DetailsView: React.FC<DetailsViewProps> = ({ missionData }) => {
  const detailViewData = missionData
    ? detail_view_data[missionData.missionId]
    : null;

  const [location, setLocation] = useState<string>(missionData.location);

  return (
    <AbstractPage
      headline={`${missionData.name}${location ? `, ${location}` : ""}${
        missionData.robot ? ` with ${missionData.robot}` : ""
      }`}
    >
      {/* Main content */}
      <Grid gutter="md">
        {/* Left column occupying 80% */}
        <Grid.Col span={9}>
          <Grid gutter="md">
            {/* Tags */}
            <Grid.Col span={12}>
              {missionData && (
                <RenderTagsDetailView
                  tags_={missionData.tags}
                  missionId={missionData.missionId}
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
          <ShowInformationView
            missionData={missionData}
            setLocation_={setLocation}
          />
        </Grid.Col>
      </Grid>
    </AbstractPage>
  );
};

export default DetailsView;
