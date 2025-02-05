import { Grid } from "@mantine/core";
import React, { useState } from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { DetailViewData, RenderedMission, Tag } from "~/data";
import AbstractPage from "../AbstractPage";
import { ShowInformationView } from "./InformationView";
import { formatRobotNames } from "~/utilities/FormatHandler";

interface DetailsViewProps {
  missionData: RenderedMission;
  detailViewData: DetailViewData | undefined;
  totalSize: string;
  totalDuration: string;
  allTags: Tag[];
  basePath: string;
}

const DetailsView: React.FC<DetailsViewProps> = ({
  missionData,
  detailViewData,
  totalSize,
  totalDuration,
  allTags,
  basePath
}) => {
  const [location, setLocation] = useState<string>(missionData.location);

  let formattedRobotNames = "";

  if (detailViewData?.robots) 
    formattedRobotNames = formatRobotNames(detailViewData.robots);

  return (
    <AbstractPage
      headline={`${missionData.name}${location ? ` in ${location}` : ""}${
        formattedRobotNames.length > 0
          ? ` with ${formattedRobotNames}`
          : ""
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
              {detailViewData && (
                <ShowDatasets data={detailViewData} basePath={basePath} />
              )}
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
            basePath={basePath}
          />
        </Grid.Col>
      </Grid>
    </AbstractPage>
  );
};

export default DetailsView;
