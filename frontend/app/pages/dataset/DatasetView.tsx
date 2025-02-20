import { Badge, Group, Grid, Text } from "@mantine/core";
import { FileData, Topic } from "~/data";
import { ActionButtons } from "./ActionButtons";
import { DatasetDetails } from "./DatasetDetailsView";
import { TopicTableArea } from "./TopicTable";

interface DatasetViewProps {
  data: FileData;
  topics: Topic[];
}

export const DatasetView = ({ data, topics }: DatasetViewProps) => {
  const displayFile = (data.filePath ?? "").split(/[\\/]/).pop() ?? "";

  return (
    <div>
      <Group align="center" style={{ marginBottom: "17px" }}>
        <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: "normal" }}>
          {displayFile +
            (data.robot && data.robot.length > 0 ? " on " + data.robot : "")}
        </h1>

        <Badge key={data.type} color="orange" variant="light" size="lg">
          {data.type}
        </Badge>
      </Group>

      <Grid gutter="md">
        {/* Full width on small screens, 9/3 split on md+ screens */}
        <Grid.Col span={{ base: 12, sm: 12, md: 8 }}>
          <Grid gutter="md">
            <Grid.Col span={12}>
              <ActionButtons
                filePath={data.filePath ?? ""}
                fileUrl={data.fileUrl}
                displayFile={displayFile}
              />
            </Grid.Col>
            <Grid.Col span={12}>
              <Text size = "xl" mb = "sm"> Topics </Text>
              <TopicTableArea topics={topics} />
            </Grid.Col>
          </Grid>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 12, md: 4 }}>
          <DatasetDetails
            duration={data.duration}
            size={data.size}
            videoUrl={data.videoUrl}
          />
        </Grid.Col>
      </Grid>
    </div>
  );
}
