import { Grid } from "@mantine/core";
import React, { useState } from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { DetailViewData, RenderedMission, Tag } from "~/data";
import AbstractPage from "../AbstractPage";
import { ShowInformationView } from "./InformationView";

// This functions returns the robot names in the format x, y and z.
// For duplicate robot names, only the first occurance is used, e.g. x, y, x -> x and y and the camel case is ignored,
// meaning x, y, X -> x and y.
function formatRobotNames(robotNames: string[] | undefined | null): string {
  if (!robotNames) {
    return "";
  }

  // Create a Set to track normalized names and filter duplicates
  const seen = new Set<string>();
  const uniqueRobots = robotNames.filter((name) => {
    if (!name) {
      return false;
    }
    const normalizedName = name.toLowerCase();
    if (seen.has(normalizedName)) {
      return false;
    }
    seen.add(normalizedName);
    return true;
  });

  if (uniqueRobots.length === 0) {
    return "";
  } else if (uniqueRobots.length === 1) {
    return uniqueRobots[0];
  } else {
    const lastRobot = uniqueRobots.pop();
    return `${uniqueRobots.join(", ")} and ${lastRobot}`;
  }
}

interface DetailsViewProps {
  missionData: RenderedMission;
  detailViewData: DetailViewData | undefined;
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
      headline={`${missionData.name}${location ? ` in ${location}` : ""}${
        detailViewData?.robots && detailViewData?.robots.length > 0
          ? ` with ${formatRobotNames(detailViewData.robots)}`
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
