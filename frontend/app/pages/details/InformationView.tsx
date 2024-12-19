import {
  Badge,
  Button,
  Group,
  Menu,
  Text,
  Textarea,
  TextInput,
} from "@mantine/core";
import { IconPencil } from "@tabler/icons-react";
import { useState } from "react";
import { MissionData } from "~/data";

type EditableFieldProps = {
  fieldName: string;
  data: string;
  startName: string;
  sizeError: string;
  onValueChange: (value: string) => void;
};

const EditableField: React.FC<EditableFieldProps> = ({
  fieldName,
  data,
  startName,
  sizeError,
  onValueChange,
}) => {
  const [fieldValue, setFieldValue] = useState<string>(data ?? "");

  return (
    <Group gap="xs">
      {/* Field Name and Current Value */}
      <Text>
        {fieldName}: {data === null ? "None" : data}
      </Text>

      {/* Menu for Editing */}
      <Menu>
        <Menu.Target>
          <Badge color="grey" variant="light" style={{ cursor: "pointer" }}>
            <IconPencil size={16} style={{ transform: "translateY(2px)" }} />
          </Badge>
        </Menu.Target>

        {/* Actions for the Editable Field */}
        <Menu.Dropdown style={{ padding: "10px", marginLeft: "75px" }}>
          <Textarea
            variant="filled"
            placeholder={data === null ? startName : data}
            resize="vertical"
            autosize
            value={fieldValue}
            error={fieldValue.length > 42 ? sizeError : ""}
            onChange={(event) => setFieldValue(event.currentTarget.value)}
            mb="sm"
          />
          <div style={{ display: "flex", justifyContent: "center" }}>
            <Button onClick={() => onValueChange(fieldValue)}>Update</Button>
          </div>
        </Menu.Dropdown>
      </Menu>
    </Group>
  );
};

interface ShowInformationViewProps {
  missionData: MissionData | null;
}

export const ShowStatsView: React.FC<ShowInformationViewProps> = ({
  missionData,
}) => {
  if (!missionData) return null;

  return (
    <div>
      <Text size="xl" mb="sm">
        Information
      </Text>
      <Text>Total Duration: {missionData.totalDuration}</Text>
      <Text>Total Size: {missionData.totalSize} GB</Text>

      <EditableField
        fieldName="Location"
        data={missionData.location}
        startName="Enter new location"
        sizeError="Location name too long"
        onValueChange={(value) => {
          console.log("Location updated to:", value);
        }}
      />

      <EditableField
        fieldName="Notes"
        data={missionData.notes}
        startName="Add notes"
        sizeError="Notes too long"
        onValueChange={(value) => {
          console.log("Notes updated to", value);
        }}
      />
    </div>
  );
};
