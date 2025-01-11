import { Table } from "@mantine/core";
import { useState } from "react";
import { DetailViewData } from "~/data";
import { useNavigate } from "@remix-run/react";

export function ShowDatasets({ data }: { data: DetailViewData }) {
  const navigate = useNavigate();

  // Creates rows of table
  const rows = data.files.map((file, index) => (
    <Table.Tr
      key={file}
      onClick={() => navigate('/dataset?fileName=' + file + "&duration=" + data.durations[index] + "&size=" + data.sizes[index])}
      // Change color on mouse hover
      style={{
        cursor: "pointer",
        transition: "background-color 0.2s ease",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f1f3f5")}
      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "")}
    >
      {/* Inserts data from DetailViewData, see data.tsx */}
      <Table.Td>{file}</Table.Td>
      <Table.Td>{data.durations[index]}</Table.Td>
      <Table.Td>{data.sizes[index]}</Table.Td>
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
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </>
  );
}
