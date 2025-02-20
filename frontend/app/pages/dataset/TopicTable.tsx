import { useState } from 'react';
import { ScrollArea, Table } from "@mantine/core";
import cx from 'clsx';
import classes from './TopicTableArea.module.css';
import { Topic } from "~/data";

export function TopicTableArea({ topics = [] }: { topics: Topic[] }) {
  const [scrolled, setScrolled] = useState(false);

  if (!Array.isArray(topics)) {
    return <html> No topics available </html>
  }

  const rows = topics.map((row) => (
    <Table.Tr key={row.name}>
      <Table.Td>{row.name}</Table.Td>
      <Table.Td>{row.type}</Table.Td>
      <Table.Td>{row.message_count}</Table.Td>
      <Table.Td>{row.frequency}</Table.Td>
    </Table.Tr>
  ));

  return (
    <ScrollArea h={300} onScrollPositionChange={({ y }) => setScrolled(y !== 0)}>
      <Table miw={700}>
        <Table.Thead className={cx(classes.header, { [classes.scrolled]: scrolled })}>
          <Table.Tr>
            <Table.Th>Name</Table.Th>
            <Table.Th>Type</Table.Th>
            <Table.Th>Count</Table.Th>
            <Table.Th>Frequency</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>
    </ScrollArea>
  );
}