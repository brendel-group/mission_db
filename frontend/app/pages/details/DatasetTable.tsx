import { Table } from "@mantine/core";
import { useState } from "react";
import { DetailViewData } from "~/data";
import { DatasetView } from "../dataset/DatasetView";

export function ShowDatasets({ data }: { data: DetailViewData }) {
  const [opened, setOpened] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  const handleRowClick = (file: string, index: number) => {
    setSelectedFile(file);
    setSelectedIndex(index);
    setOpened(true);
  };

  const rows = data.files.map((file, index) => (
    <Table.Tr
      key={file}
      onClick={() => handleRowClick(file, index)}
      style={{
        cursor: "pointer",
        transition: "background-color 0.2s ease",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f1f3f5")}
      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "")}
    >
      <Table.Td>{file}</Table.Td>
      <Table.Td>{data.durations[index]}</Table.Td>
      <Table.Td>{data.sizes[index]}</Table.Td>
    </Table.Tr>
  ));

  return (
    <>
      <Table>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>File</Table.Th>
            <Table.Th>Duration</Table.Th>
            <Table.Th>Size (MB)</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>

      <DatasetView
        opened={opened}
        onClose={() => setOpened(false)}
        file={selectedFile}
        duration={selectedIndex !== null ? data.durations[selectedIndex] : null}
        size={selectedIndex !== null ? data.sizes[selectedIndex] : null}
      />
    </>
  );
}
