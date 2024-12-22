import { Badge, Button, Group, Menu, Text, Textarea } from "@mantine/core";
import { IconPencil } from "@tabler/icons-react";
import { useState } from "react";
import { RenderedMission } from "~/data";

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
  const [menuOpened, setMenuOpened] = useState(false);

  return (
    <Group gap="xs">
      {/* Field Name and Current Value */}
      <Text>
        {fieldName}: {data === null ? "None" : data}
      </Text>

      {/* Menu for Editing */}
      <Menu
        opened={menuOpened}
        onOpen={() => setMenuOpened(true)}
        onClose={() => setMenuOpened(false)}
      >
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
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault(); // Prevent newline
                setMenuOpened(false);
                onValueChange(fieldValue);
              }
            }}
            mb="sm"
          />
          <div style={{ display: "flex", justifyContent: "center" }}>
            <Button
              onClick={() => {
                setMenuOpened(false);
                onValueChange(fieldValue);
              }}
            >
              Update
            </Button>
          </div>
        </Menu.Dropdown>
      </Menu>
    </Group>
  );
};

interface ShowInformationViewProps {
  missionData: RenderedMission;
  setLocation_: (loc: string) => void;
}

export const ShowInformationView: React.FC<ShowInformationViewProps> = ({
  missionData,
  setLocation_,
}) => {
  const [location, setLocation] = useState<string>(missionData.location);
  const [notes, setNotes] = useState<string>(missionData.notes);

  return (
    <div>
      <Text size="xl" mb="sm">
        Information
      </Text>
      <Text>Date: {missionData.date}</Text>
      <Text>Total Duration: {missionData.totalDuration}</Text>
      <Text>Total Size: {missionData.totalSize} GB</Text>

      <EditableField
        fieldName="Location"
        data={location}
        startName="Enter new location"
        sizeError="Location name too long"
        onValueChange={(value) => {
          console.log("Location updated to:", value);
          setLocation(value);
          setLocation_(value);
        }}
      />

      <EditableField
        fieldName="Notes"
        data={notes}
        startName="Add notes"
        sizeError="Notes too long"
        onValueChange={(value) => {
          console.log("Notes updated to", value);
          setNotes(value);
        }}
      />
    </div>
  );
};
