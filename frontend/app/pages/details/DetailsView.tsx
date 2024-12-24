import { Grid } from "@mantine/core";
import React, { useEffect, useState } from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { ShowStatsView } from "./StatsView";
import { MissionData, DetailViewData } from "~/data";
import AbstractPage from "../AbstractPage";
import { getDetailsByMission } from "../../utilities/fetchapi";



interface DetailsViewProps {
  missionData: MissionData | null;
}

const DetailsView: React.FC<DetailsViewProps> = ({
  missionData: selectedRow,
}) => {
  const [detailViewData, setDetailViewData] = useState<DetailViewData>();
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
      headline={
        selectedRow
          ? `${selectedRow.name}${selectedRow.location ? `, ${selectedRow.location}` : ""}${selectedRow.robot ? ` with ${selectedRow.robot}` : ""
          }`
          : "Mission Details"
      }
    >
      {/* Main content */}
      < Grid gutter="md" >
        {/* Left column occupying 80% */}
        < Grid.Col span={9} >
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
        </Grid.Col >

        {/* Stats */}
        < Grid.Col span={3} >
          <ShowStatsView missionData={selectedRow} />
        </Grid.Col >
      </Grid >
    </AbstractPage >
  );
};

export default DetailsView;
