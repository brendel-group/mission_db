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
  Menu,
} from "@mantine/core";
import {
  IconSelector,
  IconChevronDown,
  IconChevronUp,
  IconSearch,
} from "@tabler/icons-react";
import classes from "./Overview.module.css";
import { mission_table_data } from "../../RandomData";
import { MissionData } from "~/data";
import RenderView from "../details/DetailsView";
import { RenderTagsOverview } from "../../utilities/TagList";

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

function filterData(data: MissionData[], search: string) {
  const query = search.toLowerCase().trim();
  return data.filter((item) =>
    keys(data[0]).some((key) => {
      const value = item[key];
      if (Array.isArray(value)) {
        // Durchsuche jedes Element im Array, falls `other` ein Array ist
        return value.some((tag) => tag.name.toLowerCase().includes(query));
      }
      return typeof value === "string" && value.toLowerCase().includes(query);
    }),
  );
}

function sortData(
  data: MissionData[],
  payload: {
    sortBy: keyof MissionData | null;
    reversed: boolean;
    search: string;
  },
) {
  const { sortBy } = payload;

  if (!sortBy) {
    return filterData(data, payload.search);
  }

  return filterData(
    [...data].sort((a, b) => {
      if (sortBy === "total_size") {
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
        const tagA = a.tags[0].name || ""; // Fallback, falls Array leer ist
        const tagB = b.tags[0].name || "";

        return payload.reversed
          ? tagB.localeCompare(tagA)
          : tagA.localeCompare(tagB);
      }

      // Other fields can be sorted alphabetically
      if (payload.reversed) {
        return String(b[sortBy]).localeCompare(String(a[sortBy]));
      }

      return String(a[sortBy]).localeCompare(String(b[sortBy]));
    }),
    payload.search,
  );
}

export function Overview() {
  const [search, setSearch] = useState("");
  const [sortedData, setSortedData] = useState(mission_table_data);
  const [sortBy, setSortBy] = useState<keyof MissionData | null>(null);
  const [reverseSortDirection, setReverseSortDirection] = useState(false);
  const [modalOpened, setModalOpened] = useState(false);
  const [selectedRow, setSelectedRow] = useState<MissionData | null>(null);

  const setSorting = (field: keyof MissionData) => {
    const reversed = field === sortBy ? !reverseSortDirection : false;
    setReverseSortDirection(reversed);
    setSortBy(field);
    setSortedData(
      sortData(mission_table_data, { sortBy: field, reversed, search }),
    );
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = event.currentTarget;
    setSearch(value);
    setSortedData(
      sortData(mission_table_data, {
        sortBy,
        reversed: reverseSortDirection,
        search: value,
      }),
    );
  };

  const openModal = (row: MissionData) => {
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
      <Table.Td>{row.total_duration}</Table.Td>
      <Table.Td>{row.total_size}</Table.Td>
      <Table.Td>{row.robot}</Table.Td>
      <Table.Td>{row.remarks}</Table.Td>
      <Table.Td
        onClick={(e) => e.stopPropagation()} // stops opening openModal
      >
        <Menu>
          <Menu.Target>
            <div>
              <RenderTagsOverview tags={row.tags} />
            </div>
          </Menu.Target>
          {/*Actions for the Tag Picker*/}
          <Menu.Dropdown>
            {/*TODO: Implement tag picker*/}
            <h3>Tag Picker</h3>
          </Menu.Dropdown>
        </Menu>
      </Table.Td>
    </Table.Tr>
  ));

  const columns: { key: keyof MissionData; label: string }[] = [
    { key: "name", label: "Name" },
    { key: "location", label: "Location" },
    { key: "total_duration", label: "Duration" },
    { key: "total_size", label: "Size (MB)" },
    { key: "robot", label: "Robot" },
    { key: "remarks", label: "Remarks" },
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
              <Table.Td colSpan={Object.keys(mission_table_data[0]).length}>
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
