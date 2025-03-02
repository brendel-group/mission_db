import { Topic } from "~/data";
import { useState } from 'react';
import { IconChevronDown, IconChevronUp, IconSearch, IconSelector } from '@tabler/icons-react';
import {
  Center,
  Group,
  keys,
  ScrollArea,
  Table,
  Text,
  TextInput,
  UnstyledButton,
} from '@mantine/core';
import classes from './TopicTable.module.css';

interface ThProps {
children: React.ReactNode;
reversed: boolean;
sorted: boolean;
onSort: () => void;
}

function Th({ children, reversed, sorted, onSort }: ThProps) {
const Icon = sorted ? (reversed ? IconChevronUp : IconChevronDown) : IconSelector;
return (
  <Table.Th className={classes.th}>
    <UnstyledButton onClick={onSort} className={classes.control}>
      <Group justify="space-between">
        <Text fw={500} fz="sm">
          {children}
        </Text>
        <Center className={classes.icon}>
          <Icon size={16} stroke={1.5} />
        </Center>
      </Group>
    </UnstyledButton>
  </Table.Th>
);
}

function filterData(data: Topic[], search: string) {
const query = search.toLowerCase().trim();

return data.filter((item) =>
  keys(data[0]).some((key) => {
    const value = item[key];
    if (typeof value === 'number') {
      return value.toString() === query;
    }
    return (
      value !== null &&
      value !== undefined &&
      value.toString().toLowerCase().includes(query));
  })
);
}

function sortData(
data: Topic[],
payload: { sortBy: keyof Topic | null; reversed: boolean; search: string }
) {
const { sortBy } = payload;

if (!sortBy) {
  return filterData(data, payload.search);
}

return filterData(
  [...data].sort((a, b) => {
    if (typeof a[sortBy] === 'number' && typeof b[sortBy] === 'number') {
      return payload.reversed
        ? (b[sortBy] as number) - (a[sortBy] as number)
        : (a[sortBy] as number) - (b[sortBy] as number);
    }

    if (payload.reversed) {
      return (b[sortBy]?.toString() ?? '').localeCompare(a[sortBy]?.toString() ?? '');
    }

    return (a[sortBy]?.toString() ?? '').localeCompare(b[sortBy]?.toString() ?? '');
  }),
  payload.search
);
}

export function TopicTable({ topics }: { topics: Topic[] }) {
const [search, setSearch] = useState('');
const [sortedData, setSortedData] = useState(topics);
const [sortBy, setSortBy] = useState<keyof Topic | null>(null);
const [reverseSortDirection, setReverseSortDirection] = useState(false);

const setSorting = (field: keyof Topic) => {
  const reversed = field === sortBy ? !reverseSortDirection : false;
  setReverseSortDirection(reversed);
  setSortBy(field);
  setSortedData(sortData(topics, { sortBy: field, reversed, search }));
};

const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  const { value } = event.currentTarget;
  setSearch(value);
  setSortedData(sortData(topics, { sortBy, reversed: reverseSortDirection, search: value }));
};

const rows = sortedData.map((row) => (
  <Table.Tr key={row.name}>
    <Table.Td>{row.name}</Table.Td>
    <Table.Td>{row.type}</Table.Td>
    <Table.Td>{row.message_count}</Table.Td>
    <Table.Td>{row.frequency}</Table.Td>
  </Table.Tr>
));

return (
  <ScrollArea>
    <TextInput
      placeholder="Search by any field"
      mb="md"
      leftSection={<IconSearch size={16} stroke={1.5} />}
      value={search}
      onChange={handleSearchChange}
    />
    <Table horizontalSpacing="md" verticalSpacing="xs" miw={700} layout="fixed">
      <Table.Tbody>
        <Table.Tr>
          <Th
            sorted={sortBy === 'name'}
            reversed={reverseSortDirection}
            onSort={() => setSorting('name')}
          >
            Name
          </Th>
          <Th
            sorted={sortBy === 'type'}
            reversed={reverseSortDirection}
            onSort={() => setSorting('type')}
          >
            Type
          </Th>
          <Th
            sorted={sortBy === 'message_count'}
            reversed={reverseSortDirection}
            onSort={() => setSorting('message_count')}
          >
            Message Count
          </Th>
          <Th
            sorted={sortBy === 'frequency'}
            reversed={reverseSortDirection}
            onSort={() => setSorting('frequency')}
          >
            Frequency
          </Th>
        </Table.Tr>
      </Table.Tbody>
      <Table.Tbody>
        {rows.length > 0 ? (
          rows
        ) : (
          <Table.Tr>
            <Table.Td colSpan={4}>
              <Text fw={500} ta="center">
                Nothing found
              </Text>
            </Table.Td>
          </Table.Tr>
        )}
      </Table.Tbody>
    </Table>
  </ScrollArea>
);
}
interface ThProps {
  children: React.ReactNode;
  reversed: boolean;
  sorted: boolean;
  onSort: () => void;
}
