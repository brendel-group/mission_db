import { Badge, Table, ThemeIcon, UnstyledButton } from "@mantine/core";
import { DetailViewData } from "~/data";
import { useNavigate } from "@remix-run/react";
import { IconClipboard } from "@tabler/icons-react";
import { useClipboard } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { useState } from "react";

export function ShowDatasets({
  data,
  basePath,
}: {
  data: DetailViewData;
  basePath: string;
}) {
  const navigate = useNavigate();
  const clipboard = useClipboard({ timeout: 500 });
  const missionPathSplitted: string[] = basePath.split("/").slice(-2, -1);

  const [searchFor, setSearchFor] = useState<string>("");

  // Creates rows of table
  const rows = data.files.map((file, index) => {
    let type = "?";
    if (file.startsWith("train/") || file.startsWith("train\\")) type = "train";
    else if (file.startsWith("test/") || file.startsWith("test\\"))
      type = "test";

    if (searchFor !== "" && searchFor !== type) return;

    return (
      <Table.Tr
        key={file}
        onClick={() =>
          navigate(
            "/dataset?fileName=" + missionPathSplitted.concat(file).join("/")
          )
        }
        // Change color on mouse hover
        style={{
          cursor: "pointer",
          transition: "background-color 0.2s ease",
        }}
        onMouseEnter={(e) =>
          (e.currentTarget.style.backgroundColor = "#f1f3f5")
        }
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "")}
      >
        {/* Inserts data from DetailViewData, see data.tsx */}
        <Table.Td>
          <UnstyledButton
            onClick={(e) => {
              e.stopPropagation();
              clipboard.copy(basePath + file);

              notifications.clean();

              notifications.show({
                title: "Copied to clipboard!",
                message: basePath + file,
                color: "orange",
                radius: "md",
              });
            }}
          >
            <ThemeIcon variant="white">
              <IconClipboard
                stroke={2}
                color="orange"
                style={{ width: "50%", height: "50%" }}
              />
            </ThemeIcon>
          </UnstyledButton>
          {(() => {
            let displayFile = file;
            if (file.startsWith("train/") || file.startsWith("train\\"))
              displayFile = file.replace("train/", "").replace("train\\", "");
            else if (file.startsWith("test/") || file.startsWith("test\\"))
              displayFile = file.replace("test/", "").replace("test\\", "");

            //Remove the redundant folder extension with the same name:
            displayFile = displayFile.replace(/^[^\\\/]+[\\\/]/, '')

            return displayFile;
          })()}
        </Table.Td>
        <Table.Td>{data.durations[index]}</Table.Td>
        <Table.Td>{data.sizes[index]}</Table.Td>
        <Table.Td>
          {(() => {
            let color = "gray";

            if (type === "train") color = "green";
            else if (type === "test") color = "red";

            return (
              <Badge
                onClick={(e) => {
                  e.stopPropagation();

                  if (searchFor === type) setSearchFor("");
                  else setSearchFor(type);
                }}
                key={type}
                color={color}
                variant="light"
                style={{
                  textTransform: "none",
                  cursor: "pointer",
                  border: searchFor == type ? "2px solid" : "none",
                }}
              >
                {type}
              </Badge>
            );
          })()}
        </Table.Td>
        <Table.Td>{data.robots[index]}</Table.Td>
      </Table.Tr>
    );
  });

  // Returns the filled table with DatasetView
  return (
    <>
      <Table>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>File</Table.Th>
            <Table.Th>Duration</Table.Th>
            <Table.Th>Size</Table.Th>
            <Table.Th>Type</Table.Th>
            <Table.Th>Robot</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </>
  );
}
