import { Grid } from "@mantine/core";
import React, { useEffect, useState } from "react";
import { RenderTagsDetailView } from "../../utilities/TagList";
import { ShowDatasets } from "./DatasetTable";
import { RenderedMission, DetailViewData } from "~/data";
import AbstractPage from "../AbstractPage";
import { getFormattedDetails, getTotalSize, getTotalDuration } from "../../utilities/fetchapi";
import { ShowInformationView } from "./InformationView";

interface DetailsViewProps {
  missionData: RenderedMission;
}

const DetailsView: React.FC<DetailsViewProps> = ({
  missionData: selectedRow,
}) => {
  const [detailViewData, setDetailViewData] = useState<DetailViewData>();
  const [location, setLocation] = useState<string>(selectedRow.location);
  const [totalSize, setTotalSize] = useState<string>(selectedRow.totalSize);
  const [totalDuration, setTotalDuration] = useState<string>(selectedRow.totalDuration);
  useEffect(() => {
    const fetchDetailViewData = async () => {
      if (selectedRow) {
        try {
          // data for the detail view
          const fetchedData = await getFormattedDetails(selectedRow.id);
          setDetailViewData(fetchedData);
          // data for the information view (size)
          const fetchedTotalSize = await getTotalSize(selectedRow.id);
          setTotalSize(fetchedTotalSize);
          // data for the information view (duration)
          const fetchedTotalDuration = await getTotalDuration(selectedRow.id);
          setTotalDuration(fetchedTotalDuration);
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
            totalSize = {totalSize}
            totalDuration = {totalDuration}
          />
        </Grid.Col>
      </Grid>
    </AbstractPage>
  );
};

export default DetailsView;
