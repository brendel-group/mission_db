import { Grid } from "@mantine/core";
import React, { useState } from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { DetailViewData, RenderedMission, Tag } from "~/data";
import AbstractPage from "../AbstractPage";
import { ShowInformationView } from "./InformationView";

interface DetailsViewProps {
  missionData: RenderedMission;
  detailViewData: DetailViewData;
  totalSize: string;
  totalDuration: string;
  allTags: Tag[];
}

const DetailsView: React.FC<DetailsViewProps> = ({
  missionData,
  detailViewData,
  totalSize,
  totalDuration,
  allTags,
}) => {
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
                  missionId={missionData.id}
                  allTags_={allTags}
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
            totalSize={totalSize}
            totalDuration={totalDuration}
          />
        </Grid.Col>
      </Grid>
    </AbstractPage>
  );
};

export default DetailsView;
