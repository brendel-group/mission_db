import {
  Badge,
  Button,
  Group,
  Menu,
  Text,
  Textarea,
  Stack,
  ThemeIcon,
  UnstyledButton,
} from "@mantine/core";
import { useClipboard } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { IconClipboard, IconPencil } from "@tabler/icons-react";
import { useState } from "react";
import { convertToMissionData, RenderedMission } from "~/data";
import { updateMission } from "~/fetchapi/missions";

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
    <Stack gap="0px">
      <Group gap="xs" align="center">
        {/* Field Name */}
        <Text>
          <strong>{fieldName}:</strong>
        </Text>

        {/* Menu for Editing */}
        <Menu
          opened={menuOpened}
          onOpen={() => setMenuOpened(true)}
          onClose={() => setMenuOpened(false)}
        >
          <Menu.Target>
            <Badge color="orange" variant="light" style={{ cursor: "pointer" }}>
              <IconPencil size={16} style={{ transform: "translateY(2px)" }} />
            </Badge>
          </Menu.Target>

          {/* Actions for the Editable Field */}
          <Menu.Dropdown style={{ padding: "10px", marginLeft: "-75px" }}>
            <Textarea
              variant="filled"
              placeholder={data === null ? startName : data}
              resize="vertical"
              autosize
              value={fieldValue}
              error={fieldValue.length > 65536 ? sizeError : ""}
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
                variant="gradient"
                gradient={{ from: "yellow", to: "orange", deg: 269 }}
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
      {/* Field Data */}
      <Text>
        <div style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>
          {data === null ? "" : data}
        </div>
      </Text>
    </Stack>
  );
};

interface ShowInformationViewProps {
  missionData: RenderedMission;
  setLocation_: (loc: string) => void;
  totalSize: string;
  totalDuration: string;
  basePath: string;
}

export const ShowInformationView: React.FC<ShowInformationViewProps> = ({
  missionData,
  setLocation_,
  totalSize,
  totalDuration,
  basePath,
}) => {
  const [location, setLocation] = useState<string>(missionData.location);
  const [notes, setNotes] = useState<string>(missionData.notes);
  const clipboard = useClipboard({ timeout: 500 });

  return (
    <div>
      <Text size="xl" mb="sm">
        Information
      </Text>
      <Text>
        <strong>Date:</strong> {missionData.date}
      </Text>
      <Text>
        <strong>Total Duration:</strong> {totalDuration}
      </Text>
      <Text>
        <strong>Total Size:</strong> {totalSize}
      </Text>

      <EditableField
        fieldName="Location"
        data={location}
        startName="Enter new location"
        sizeError="Location name too long"
        onValueChange={async (value) => {
          const oldLocation = location;
          if (oldLocation !== value) {
            setLocation(value);
            setLocation_(value);

            missionData.location = value;
            missionData.notes = notes;

            await updateMission(convertToMissionData(missionData));
          }
        }}
      />

      <EditableField
        fieldName="Notes"
        data={notes}
        startName="Add notes"
        sizeError="Notes too long"
        onValueChange={async (value) => {
          const oldNotes = notes;

          if (oldNotes !== value) {
            setNotes(value);

            missionData.location = location;
            missionData.notes = value;

            await updateMission(convertToMissionData(missionData));
          }
        }}
      />

      <Group>
        <Text>
          <strong>Base path:</strong>
        </Text>
        <UnstyledButton
          onClick={(e) => {
            e.stopPropagation();
            clipboard.copy(basePath);

            notifications.clean();

            notifications.show({
              title: "Copied to clipboard!",
              message: basePath,
              color: "orange",
              radius: "md",
            });
          }}
        >
          <Badge color="orange" variant="light" style={{ cursor: "pointer" }}>
              <IconClipboard stroke={2} size={16} style={{ transform: "translateY(2px)" }} />
            </Badge>
          
        </UnstyledButton>
      </Group>

      <Text>
        <div style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>
          {basePath === null ? "" : basePath}
        </div>
      </Text>
    </div>
  );
};
