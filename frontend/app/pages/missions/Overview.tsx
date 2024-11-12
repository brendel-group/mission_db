import { useState } from "react";
import {
  Table,
  ScrollArea,
  UnstyledButton,
  Group,
  Text,
  Center,
  TextInput,
  rem,
  keys,
} from "@mantine/core";
import {
  IconSelector,
  IconChevronDown,
  IconChevronUp,
  IconSearch,
} from "@tabler/icons-react";
import classes from "./Overview.module.css";
import data from "./RandomData";
import RenderView from "./RenderView";

export interface RowData {
  name: string;
  location: string;
  duration: string;
  size: string;
  robot: string;
  tags: string[];
}

interface ThProps {
  children: React.ReactNode;
  reversed: boolean;
  sorted: boolean;
  onSort(): void;
}

function Th({ children, reversed, sorted, onSort }: ThProps) {
  const Icon = sorted
    ? reversed
      ? IconChevronUp
      : IconChevronDown
    : IconSelector;
  return (
    <Table.Th className={classes.th}>
      <UnstyledButton onClick={onSort} className={classes.control}>
        <Group justify="space-between">
          <Text fw={500} fz="sm">
            {children}
          </Text>
          <Center className={classes.icon}>
            <Icon style={{ width: rem(16), height: rem(16) }} stroke={1.5} />
          </Center>
        </Group>
      </UnstyledButton>
    </Table.Th>
  );
}

function filterData(data: RowData[], search: string) {
  const query = search.toLowerCase().trim();
  return data.filter((item) =>
    keys(data[0]).some((key) => {
      const value = item[key];
      if (Array.isArray(value)) {
        // Durchsuche jedes Element im Array, falls `other` ein Array ist
        return value.some((str) => str.toLowerCase().includes(query));
      }
      return typeof value === 'string' && value.toLowerCase().includes(query);
    })
  );
}

function sortData(
  data: RowData[],
  payload: { sortBy: keyof RowData | null; reversed: boolean; search: string }
) {
  const { sortBy } = payload;

  if (!sortBy) {
    return filterData(data, payload.search);
  }

  return filterData(
    [...data].sort((a, b) => {
      if (sortBy === "size") {
        // Duration needs a numeric sort
        const durationA = parseFloat(a[sortBy]);
        const durationB = parseFloat(b[sortBy]);

        if (payload.reversed) {
          return durationB - durationA;
        }

        return durationA - durationB;
      }

      // Sortierung für `tags`, basierend auf dem ersten Element im Array
      if (sortBy === "tags") {
        const tagA = a.tags[0] || "";  // Fallback, falls Array leer ist
        const tagB = b.tags[0] || "";

        return payload.reversed
          ? tagB.localeCompare(tagA)
          : tagA.localeCompare(tagB);
      }

      // Other fields can be sorted alphabetically
      if (payload.reversed) {
        return b[sortBy].localeCompare(a[sortBy]);
      }

      return a[sortBy].localeCompare(b[sortBy]);
    }),
    payload.search
  );
}

export function Overview() {
  const [search, setSearch] = useState("");
  const [sortedData, setSortedData] = useState(data);
  const [sortBy, setSortBy] = useState<keyof RowData | null>(null);
  const [reverseSortDirection, setReverseSortDirection] = useState(false);
  const [modalOpened, setModalOpened] = useState(false);
  const [selectedRow, setSelectedRow] = useState<RowData | null>(null);

  const setSorting = (field: keyof RowData) => {
    const reversed = field === sortBy ? !reverseSortDirection : false;
    setReverseSortDirection(reversed);
    setSortBy(field);
    setSortedData(sortData(data, { sortBy: field, reversed, search }));
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = event.currentTarget;
    setSearch(value);
    setSortedData(
      sortData(data, { sortBy, reversed: reverseSortDirection, search: value })
    );
  };

  const openModal = (row: RowData) => {
    setSelectedRow(row);
    setModalOpened(true);
  };

  const rows = sortedData.map((row) => (
    <Table.Tr
      key={row.name}
      onClick={() => openModal(row)}
      style={{
        cursor: "pointer",
        transition: "background-color 0.2s ease",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f1f3f5")}
      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "")}
    >
      <Table.Td>{row.name}</Table.Td>
      <Table.Td>{row.location}</Table.Td>
      <Table.Td>{row.duration}</Table.Td>
      <Table.Td>{row.size}</Table.Td>
      <Table.Td>{row.robot}</Table.Td>
      <Table.Td>{row.tags.join(", ")}</Table.Td>
    </Table.Tr>
  ));

  const columns: { key: keyof RowData; label: string }[] = [
    { key: "name", label: "Name" },
    { key: "location", label: "Location" },
    { key: "duration", label: "Duration" },
    { key: "size", label: "Size (MB)" },
    { key: "robot", label: "Robot" },
    { key: "tags", label: "Tags" },
  ];

  return (
    <ScrollArea>
      <TextInput
        placeholder="Search"
        mb="md"
        leftSection={
          <IconSearch
            style={{ width: rem(16), height: rem(16) }}
            stroke={1.5}
          />
        }
        value={search}
        onChange={handleSearchChange}
      />
      <Table
        horizontalSpacing="md"
        verticalSpacing="xs"
        miw={700}
        layout="fixed"
      >
        <Table.Tbody>
          <Table.Tr>
            {columns.map((col) => (
              <Th
                key={col.key}
                sorted={sortBy === col.key}
                reversed={reverseSortDirection}
                onSort={() => setSorting(col.key)}
              >
                {col.label}
              </Th>
            ))}
          </Table.Tr>
        </Table.Tbody>
        <Table.Tbody>
          {rows.length > 0 ? (
            rows
          ) : (
            <Table.Tr>
              <Table.Td colSpan={Object.keys(data[0]).length}>
                <Text fw={500} ta="center">
                  Nothing found
                </Text>
              </Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>

      {/* Modal Component */}
      <RenderView
        modalOpened={modalOpened}
        selectedRow={selectedRow}
        onClose={() => setModalOpened(false)}
      />
    </ScrollArea>
  );
}
