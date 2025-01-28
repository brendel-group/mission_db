import { Table, ThemeIcon, UnstyledButton } from "@mantine/core";
import { DetailViewData } from "~/data";
import { useNavigate } from "@remix-run/react";
import { IconClipboard } from "@tabler/icons-react";
import { useClipboard } from "@mantine/hooks";
import { notifications } from '@mantine/notifications';

export function ShowDatasets({
  data,
  basePath,
}: {
  data: DetailViewData;
  basePath: string;
}) {
  const navigate = useNavigate();
  const clipboard = useClipboard({ timeout: 500 });
  
  // Creates rows of table
  const rows = data.files.map((file, index) => (
    <Table.Tr
      key={file}
      onClick={() =>
        navigate(
          "/dataset?fileName=" +
            file +
            "&duration=" +
            data.durations[index] +
            "&size=" +
            data.sizes[index]
        )
      }
      // Change color on mouse hover
      style={{
        cursor: "pointer",
        transition: "background-color 0.2s ease",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f1f3f5")}
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
              title: 'Copied to clipboard!',
              message: basePath + file,
              color: 'orange',
              radius: 'md',
            })

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
        {file}
      </Table.Td>
      <Table.Td>{data.durations[index]}</Table.Td>
      <Table.Td>{data.sizes[index]}</Table.Td>
      <Table.Td>{data.robots[index]}</Table.Td>
    </Table.Tr>
  ));

  // Returns the filled table with DatasetView
  return (
    <>
      <Table>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>File</Table.Th>
            <Table.Th>Duration</Table.Th>
            <Table.Th>Size</Table.Th>
            <Table.Th>Robot</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </>
  );
}
