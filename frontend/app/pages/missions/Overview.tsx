import { useState, useEffect } from "react";
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
import { MissionData } from "~/data";
import { fetchAndTransformMissions } from "~/utilities/fetchapi";
import { RenderTagsOverview } from "../../utilities/TagList";
import { TagPicker } from "~/utilities/TagPicker";
import { IconPlus } from "@tabler/icons-react";
import { useNavigate } from "@remix-run/react";

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
        // Search every element in the array if value is an array (needed for tags)
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
      if (sortBy === "totalSize") {
        // Duration needs a numeric sort
        const durationA = parseFloat(a[sortBy]);
        const durationB = parseFloat(b[sortBy]);

        if (payload.reversed) {
          return durationB - durationA;
        }

        return durationA - durationB;
      }

      // sorting for tags based on the first tag of the tags list
      if (sortBy === "tags") {
        const tagA = a.tags && a.tags.length > 0 ? a.tags[0]?.name ?? "" : "";
        const tagB = b.tags && b.tags.length > 0 ? b.tags[0]?.name ?? "" : "";

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
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [sortedData, setSortedData] = useState<MissionData[]>([]);
  const [sortBy, setSortBy] = useState<keyof MissionData | null>(null);
  const [reverseSortDirection, setReverseSortDirection] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMissions = async () => {
      try {
        const data = await fetchAndTransformMissions(); // Fetch data from API
        if (data.length <= 0) {
          throw new Error("Data is empty");
        }
        setSortedData(data);
      } catch (e: any) {
        if (e instanceof Error) {
          setError(e.message); // Display Error information
        } else {
          setError("An unknown error occurred"); // For non-Error types
        }
      } finally {
        setLoading(false);
      }
    };

    fetchMissions();
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  const setSorting = (field: keyof MissionData) => {
    const reversed = field === sortBy ? !reverseSortDirection : false;
    setReverseSortDirection(reversed);
    setSortBy(field);
    setSortedData(sortData(sortedData, { sortBy: field, reversed, search }));
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = event.currentTarget;
    setSearch(value);
    setSortedData(
      sortData(sortedData, {
        sortBy,
        reversed: reverseSortDirection,
        search: value,
      }),
    );
  };

  const rows = sortedData.map((row) => (
    <Table.Tr
      key={row.name}
      onClick={() => navigate('/detail?id=' + row.missionId)}
      style={{
        cursor: "pointer",
        transition: "background-color 0.2s ease",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f1f3f5")}
      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "")}
    >
      <Table.Td>{row.name}</Table.Td>
      <Table.Td>{row.location}</Table.Td>
      <Table.Td>{row.totalDuration}</Table.Td>
      <Table.Td>{row.totalSize}</Table.Td>
      <Table.Td>{row.robot}</Table.Td>
      <Table.Td>{row.remarks}</Table.Td>
      <Table.Td
        onClick={(e) => e.stopPropagation()} // stops opening openModal
      >
        <Menu styles={{ dropdown: { border: "1px solid #ccc" } }}>
          <Menu.Target>
            <div>
              <RenderTagsOverview tags={row.tags} />
              {row.tags.length === 0 && (
                <Center>
                  <IconPlus size={16} stroke={1.5} color="gray" />
                </Center>
              )}
            </div>
          </Menu.Target>
          {/*Actions for the Tag Picker*/}
          <Menu.Dropdown style={{ padding: "10px" }}>
            <TagPicker
              tags={row.tags}
              onAddTag={(newTag) => {
                // update tags in frontend. TODO: Implement API call to update tags in backend
                row.tags.push(newTag);
                setSortedData([...sortedData]);
              }}
              onRemoveTag={(tagName) => {
                // update tags in frontend. TODO: Implement API call to update tags in backend
                row.tags = row.tags.filter((tag) => tag.name !== tagName);
                setSortedData([...sortedData]);
              }}
              onChangeTagColor={(tagName, newColor) => {
                // update tags in frontend. TODO: Implement API call to update tags in backend
                const tag = row.tags.find((tag) => tag.name === tagName);
                if (tag) {
                  tag.color = newColor;
                  setSortedData([...sortedData]);
                }
              }}
            />
          </Menu.Dropdown>
        </Menu>
      </Table.Td>
    </Table.Tr>
  ));

  const columns: { key: keyof MissionData; label: string }[] = [
    { key: "name", label: "Name" },
    { key: "location", label: "Location" },
    { key: "totalDuration", label: "Duration" },
    { key: "totalSize", label: "Size (MB)" },
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
              <Table.Td colSpan={Object.keys(sortedData[0]).length}>
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
