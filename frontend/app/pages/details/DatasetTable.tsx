import { Table } from "@mantine/core";
import { DetailViewData } from "~/data";

export function ShowDatasets({ data }: { data: DetailViewData }) {
  const rows = data.files.map((file, index) => (
    <Table.Tr key={file}>
      <Table.Td>{file}</Table.Td>
      <Table.Td>{data.durations[index]}</Table.Td>
      <Table.Td>{data.sizes[index]}</Table.Td>
    </Table.Tr>
  ));

  return (
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
  );
}
