import { Grid } from "@mantine/core";
import React, { useEffect, useState } from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
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
  const [location, setLocation] = useState<string>(selectedRow.location);
  useEffect(() => {
    const fetchDetailViewData = async () => {
      if (selectedRow) {
        try {
          const fetchedData = await getDetailsByMission(selectedRow.id);
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
      headline={`${selectedRow.name}${location ? `, ${location}` : ""}${
        selectedRow.robot ? ` with ${selectedRow.robot}` : ""
      }`}
    >
      {/* Main content */}
      <Grid gutter="md">
        {/* Left column occupying 80% */}
        <Grid.Col span={9}>
          <Grid gutter="md">
            {/* Tags */}
            <Grid.Col span={12}>
              {selectedRow && (
                <RenderTagsDetailView
                  tags_={selectedRow.tags}
                  missionId={selectedRow.id}
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
            missionData={selectedRow}
            setLocation_={setLocation}
          />
        </Grid.Col>
      </Grid>
    </AbstractPage>
  );
};

export default DetailsView;
