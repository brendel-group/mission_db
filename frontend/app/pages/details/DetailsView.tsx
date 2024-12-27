import { Grid } from "@mantine/core";
import React, { useEffect, useState } from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { ShowStatsView } from "./StatsView";
import { RenderedMission, DetailViewData } from "~/data";
import AbstractPage from "../AbstractPage";
import { getDetailsByMission } from "../../utilities/fetchapi";
import { ShowInformationView } from "./InformationView";

interface DetailsViewProps {
  missionData: RenderedMission;
}

const DetailsView: React.FC<DetailsViewProps> = ({
  missionData: selectedRow,
}) => {
  const [detailViewData, setDetailViewData] = useState<DetailViewData>();
  const [location, setLocation] = useState<string>(missionData.location);
  useEffect(() => {
    const fetchDetailViewData = async () => {
      if (selectedRow) {
        try {
          const fetchedData = await getDetailsByMission(selectedRow.missionId);
          setDetailViewData(fetchedData);
        } catch (error) {
          console.error("Error fetching detail view data:", error);
        }
      }
    };
  
    fetchDetailViewData();
  }, [selectedRow]);

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
