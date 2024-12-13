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
  Skeleton,
  Badge,
} from "@mantine/core";
import {
  IconSelector,
  IconChevronDown,
  IconChevronUp,
  IconSearch,
} from "@tabler/icons-react";
import classes from "./Overview.module.css";
import { MissionData } from "~/data";
import {
  fetchAndTransformMissions,
  addTagToMission,
  changeTagColor,
  removeTagFromMission,
  createTag,
  getMissionsByTag,
  deleteTag,
} from "~/utilities/fetchapi";
import { TagPicker } from "~/utilities/TagPicker";
import { IconPencil } from "@tabler/icons-react";
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

function filterData(
  data: MissionData[],
  search: string,
  searchedTags: string[] = [],
) {
  const query = search.toLowerCase().trim();
  return data.filter((item) => {
    const matchesSearch = keys(data[0]).some((key) => {
      const value = item[key];
      if (Array.isArray(value)) {
        return value.some((tag) => tag.name.toLowerCase().includes(query));
      }
      return typeof value === "string" && value.toLowerCase().includes(query);
    });

    const matchesTags =
      searchedTags.length === 0 ||
      (item.tags &&
        searchedTags.every((tag) =>
          item.tags.some((itemTag) => itemTag.name === tag),
        ));

    return matchesSearch && matchesTags;
  });
}

function sortData(
  data: MissionData[],
  payload: {
    sortBy: keyof MissionData | null;
    reversed: boolean;
    search: string;
    searchedTags: string[];
  },
) {
  const { sortBy } = payload;

  if (!sortBy) {
    return filterData(data, payload.search, payload.searchedTags);
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
  const [fetchedData, setFetchedData] = useState<MissionData[]>([]);
  const [renderedData, setRenderedData] = useState<MissionData[]>([]);
  const [sortBy, setSortBy] = useState<keyof MissionData | null>(null);
  const [reverseSortDirection, setReverseSortDirection] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchedTags, setSearchedTags] = useState<string[]>([]);

  useEffect(() => {
    const fetchMissions = async () => {
      try {
        const data = await fetchAndTransformMissions(); // Fetch data from API
        if (data.length <= 0) {
          throw new Error("Data is empty");
        }

        setFetchedData(data);
        setRenderedData(data);
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
    console.log(JSON.stringify(fetchedData));
  }, []);

  if (loading) return <Skeleton style={{ height: "30vh" }} />;

  if (error) return <p>Error: {error}</p>;

  const setSorting = (field: keyof MissionData) => {
    const reversed = field === sortBy ? !reverseSortDirection : false;
    setReverseSortDirection(reversed);
    setSortBy(field);
    setRenderedData(
      sortData(fetchedData, { sortBy: field, reversed, search, searchedTags }),
    );
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = event.currentTarget;
    setSearch(value);
    setRenderedData(
      sortData(fetchedData, {
        sortBy,
        reversed: reverseSortDirection,
        search: value,
        searchedTags,
      }),
    );
  };

  const rows = renderedData.map((row) => (
    <Table.Tr
      key={row.name}
      onClick={() => navigate("/details?id=" + row.missionId)}
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
        onClick={(e) => e.stopPropagation()}
        style={{ cursor: "default" }}
      >
        <Group gap="xs">
          {/* render tags */}
          {row.tags.map((item) => (
            <Badge
              key={item.name}
              color={item.color}
              variant={"light"}
              style={{
                textTransform: "none",
                cursor: "pointer",
                border: searchedTags.includes(item.name) ? "2px solid" : "none",
              }}
              onClick={(e) => {
                e.stopPropagation();
                setSearchedTags(
                  (current) =>
                    current.includes(item.name)
                      ? current.filter((tag) => tag !== item.name) // remove Tag
                      : [...current, item.name], // add Tag
                );
                setRenderedData(
                  sortData(fetchedData, {
                    sortBy,
                    reversed: reverseSortDirection,
                    search,
                    searchedTags: searchedTags.includes(item.name)
                      ? searchedTags.filter((tag) => tag !== item.name)
                      : [...searchedTags, item.name],
                  }),
                );
              }}
            >
              {item.name}
            </Badge>
          ))}
          <Menu>
            {/*edit button*/}
            <Menu.Target>
              <Badge color="grey" variant="light" style={{ cursor: "pointer" }}>
                <IconPencil
                  size={16}
                  style={{ transform: "translateY(2px)" }}
                />
              </Badge>
            </Menu.Target>
            {/*Actions for the Tag Picker*/}
            <Menu.Dropdown
              style={{ padding: "10px", marginLeft: "-25px", marginTop: "2px" }}
            >
              <TagPicker
                tags={row.tags}
                onAddNewTag={(tagName, tagColor) => {
                  //update tags in backend
                  createTag(tagName, tagColor);
                  addTagToMission(row.missionId, tagName);
                  // update tags in frontend
                  row.tags.push({ tagId: 0, name: tagName, color: tagColor });
                  setRenderedData([...renderedData]);
                }}
                onRemoveTag={async (tagName) => {
                  // update tags in backend
                  await removeTagFromMission(row.missionId, tagName);
                  const missionsWithTag = await getMissionsByTag(tagName);
                  if (missionsWithTag.length === 0) {
                    // delete tag from database if no missions are using it
                    deleteTag(tagName);
                  }
                  // update tags in frontend
                  row.tags = row.tags.filter((tag) => tag.name !== tagName);
                  setRenderedData([...renderedData]);
                }}
                onChangeTagColor={(tagName, newColor) => {
                  // update tag color in backend
                  changeTagColor(tagName, newColor);

                  // update tags in frontend
                  const updatedRenderedData = renderedData.map((missionRow) => {
                    // Find the tag in each row and update its color if found
                    const updatedTags = missionRow.tags.map((tag) => {
                      if (tag.name === tagName) {
                        return { ...tag, color: newColor }; // update the color of the matching tag
                      }
                      return tag;
                    });

                    // Return the updated row with the updated tags
                    return { ...missionRow, tags: updatedTags };
                  });

                  // Set the updated state with the updated array
                  setRenderedData(updatedRenderedData);
                }}
              />
            </Menu.Dropdown>
          </Menu>
        </Group>
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
              <Table.Td colSpan={columns.length}>
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
