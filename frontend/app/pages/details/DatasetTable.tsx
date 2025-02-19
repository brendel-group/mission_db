import {
  Badge,
  Table,
  ThemeIcon,
  Tooltip,
  UnstyledButton,
} from "@mantine/core";
import { DetailViewData } from "~/data";
import { useNavigate } from "@remix-run/react";
import { IconClipboard, IconDownload } from "@tabler/icons-react";
import { useClipboard } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { useRef, useState } from "react";

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

  // Deterministic color management without the need of a database :))
  const typeColorsRef = useRef<Record<string, string>>({});
  const colorIndexRef = useRef<number>(0);

  const colorList = [
    "red",
    "blue",
    "green",
    "orange",
    "purple",
    "yellow",
    "cyan",
    "magenta",
    "teal",
    "brown",
  ];

  const getColorForType = (type: string): string => {
    if (!typeColorsRef.current[type]) {
      typeColorsRef.current[type] =
        colorList[colorIndexRef.current % colorList.length];
      colorIndexRef.current += 1;
    }
    return typeColorsRef.current[type];
  };

  // Creates rows of table
  const rows = data.files.map((file, index) => {
    let type = data.types[index];
    let url = data.fileUrls[index];

    let displayFile = file;
    if (
      type !== "?" &&
      (displayFile.startsWith(type + "/") ||
        displayFile.startsWith(type + "\\"))
    )
      displayFile = displayFile.slice(type.length + 1);

    displayFile = displayFile.replace(/^[^\\\/]+[\\\/]/, "");

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
          {/* Copy buttom */}
          <Tooltip label="Copy path">
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
              style={{ marginRight: "1px" }}
            >
              <ThemeIcon variant="white">
                <IconClipboard
                  stroke={2}
                  color="#fd7e14"
                  style={{ width: "50%", height: "50%" }}
                />
              </ThemeIcon>
            </UnstyledButton>
          </Tooltip>

          {/* Download bottom */}
          <Tooltip label="Download">
            <UnstyledButton
              onClick={(e) => {
                e.stopPropagation();

                const link = document.createElement("a");
                link.href = url.toString();
                link.download = displayFile;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }}
              style={{ marginRight: "1px" }}
            >
              <ThemeIcon variant="white">
                <IconDownload
                  stroke={2}
                  color="#fd7e14"
                  style={{ width: "50%", height: "50%" }}
                />
              </ThemeIcon>
            </UnstyledButton>
          </Tooltip>

          {/* Foxglove bottom */}
          <Tooltip label="Open in Foxglove">
            <UnstyledButton
              onClick={(e) => {
                e.stopPropagation();

                const link = document.createElement("a");
                link.href =
                  "foxglove://open?ds=remote-file&ds.url=" + String(url);
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }}
              style={{ marginRight: "1px" }}
            >
              <ThemeIcon variant="white">
                <img
                  src="/fox_glove.svg"
                  alt="Fox Glove Icon"
                  style={{ width: "50%", height: "50%" }}
                />
              </ThemeIcon>
            </UnstyledButton>
          </Tooltip>
          {displayFile}
        </Table.Td>
        <Table.Td>{data.durations[index]}</Table.Td>
        <Table.Td>{data.sizes[index]}</Table.Td>
        <Table.Td>
          {(() => {
            let color = "gray";

            if (type !== "?") color = getColorForType(type);

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
