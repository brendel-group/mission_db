import { Grid } from "@mantine/core";
import React, { useState } from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { RenderedMission } from "~/data";
import AbstractPage from "../AbstractPage";
import { ShowInformationView } from "./InformationView";

interface DetailsViewProps {
  missionData: RenderedMission;
}

const DetailsView: React.FC<DetailsViewProps> = ({ missionData }) => {
  const detailViewData = {
    files: ["file1.mcap", "file2.mcap", "file3.mcap"],
    durations: ["00:01:30", "00:02:45", "00:00:50"],
    sizes: ["2000", "4500", "1000"],
  };

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
