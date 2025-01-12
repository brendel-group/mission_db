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
  Skeleton,
  Badge,
  Popover,
} from "@mantine/core";
import { isValidHexColor } from "~/utilities/TagPicker";
import {
  IconSelector,
  IconChevronDown,
  IconChevronUp,
  IconSearch,
} from "@tabler/icons-react";
import classes from "./Overview.module.css";
import { MissionData, RenderedMission, Tag } from "~/data";
import {
  addTagToMission,
  changeTagName,
  changeTagColor,
  removeTagFromMission,
  createTag,
  getMissionsByTag,
  deleteTag,
  getMissions,
  getTagsByMission,
  getTotalDuration,
  getTotalSize,
  getTags,
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
  data: RenderedMission[],
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
  data: RenderedMission[],
  payload: {
    sortBy: keyof RenderedMission | null;
    reversed: boolean;
    search: string;
    searchedTags: string[];
  },
) {
  const { sortBy, reversed, search, searchedTags } = payload;

  // first filter the data
  const filteredData = filterData(data, search, searchedTags);

  // if no sortBy is specified, return the filtered data
  if (!sortBy) {
    return reversed ? filteredData.reverse() : filteredData;
  }

  // otherwise sort the data
  const sortedData = [...filteredData].sort((a, b) => {
    // numeric sorting
    if (sortBy === "totalSize") {
      const durationA = parseFloat(a[sortBy]);
      const durationB = parseFloat(b[sortBy]);
      return durationA - durationB;
    }

    // sort an array of tags by the first tag name
    if (sortBy === "tags") {
      const tagA = a.tags?.[0]?.name ?? "";
      const tagB = b.tags?.[0]?.name ?? "";
      return tagA.localeCompare(tagB);
    }

    // default sorting
    return String(a[sortBy]).localeCompare(String(b[sortBy]));
  });

  // return the sorted data in the correct order
  return reversed ? sortedData.reverse() : sortedData;
}

export function Overview() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [fetchedData, setFetchedData] = useState<RenderedMission[]>([]);
  const [renderedData, setRenderedData] = useState<RenderedMission[]>([]);
  const [sortBy, setSortBy] = useState<keyof RenderedMission | null>(null);
  const [reverseSortDirection, setReverseSortDirection] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchedTags, setSearchedTags] = useState<string[]>([]);
  const [allTags, setAllTags] = useState<Tag[]>([]);

  useEffect(() => {
    const fetchMissions = async () => {
      try {
        const missions: MissionData[] = await getMissions(); // Fetch the missions using the REST API

        // Map BackendMissionData missions to MissionData
        let renderedMissions: RenderedMission[] = [];
        for (let i = 0; i < missions.length; i++) {
          // Fetch tags for each mission
          const tags: Tag[] = await getTagsByMission(missions[i].id);
          tags.sort((a, b) => a.name.localeCompare(b.name));
          // Fetch total duration for each mission
          const totalDuration: string = await getTotalDuration(missions[i].id);
          // Fetch total size for each mission
          const totalSize: string = await getTotalSize(missions[i].id);
          renderedMissions.push({
            id: missions[i].id,
            name: missions[i].name,
            location: missions[i].location,
            date: missions[i].date,
            notes: missions[i].notes,
            totalDuration: totalDuration,
            totalSize: totalSize,
            robot: "Vader",
            tags: tags || [],
          });
        }

        if (renderedMissions.length <= 0) {
          throw new Error("Data is empty");
        }

        setFetchedData(renderedMissions);
        setRenderedData(renderedMissions);
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

    const fetchTags = async () => {
      try {
        const tags = await getTags();
        setAllTags(tags);
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

    fetchTags();
    fetchMissions();
    console.log(JSON.stringify(fetchedData));
  }, []);

  if (loading) return <Skeleton style={{ height: "30vh" }} />;

  if (error) return <p>Error: {error}</p>;

  const setSorting = (field: keyof RenderedMission) => {
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
      onClick={() => navigate("/details?id=" + row.id)}
      style={{
        cursor: "pointer",
        transition: "background-color 0.2s ease",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f1f3f5")}
      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "")}
    >
      <Table.Td>{row.name}</Table.Td>
      <Table.Td>{row.location === null ? "" : row.location}</Table.Td>
      <Table.Td>{row.totalDuration}</Table.Td>
      <Table.Td>{row.totalSize}</Table.Td>
      <Table.Td>{row.robot}</Table.Td>
      <Table.Td>{row.date}</Table.Td>
      <Table.Td>{row.notes === null ? "" : row.notes}</Table.Td>
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
                const updatedTags = searchedTags.includes(item.name)
                  ? searchedTags.filter((tag) => tag !== item.name) // remove tag from search
                  : [...searchedTags, item.name]; // add tag to search
                setSearchedTags(updatedTags);
                setRenderedData(
                  sortData(fetchedData, {
                    sortBy,
                    reversed: reverseSortDirection,
                    search,
                    searchedTags: updatedTags,
                  }),
                );
              }}
            >
              {item.name}
            </Badge>
          ))}
          <Popover>
            {/*edit button*/}
            <Popover.Target>
              <Badge color="grey" variant="light" style={{ cursor: "pointer" }}>
                <IconPencil
                  size={16}
                  style={{ transform: "translateY(2px)" }}
                />
              </Badge>
            </Popover.Target>
            {/*Actions for the Tag Picker*/}
            <Popover.Dropdown
              style={{
                padding: "10px",
                marginLeft: "-25px",
                marginTop: "2px",
                width: "300px",
              }}
            >
              <TagPicker
                tags={row.tags}
                allTags={allTags}
                onAddNewTag={async (tagName, tagColor) => {
                  //update tags in backend
                  await createTag(tagName, tagColor);
                  await addTagToMission(row.id, tagName);

                  // update tags in frontend
                  const newTag = { name: tagName, color: tagColor };
                  const updateMissionTags = (mission: RenderedMission) =>
                    mission.id === row.id
                      ? { ...mission, tags: [...mission.tags, newTag] }
                      : mission;
                  setAllTags([...allTags, newTag]);
                  setFetchedData(fetchedData.map(updateMissionTags));
                  setRenderedData(renderedData.map(updateMissionTags));
                }}
                onAddExistingTag={async (tagName) => {
                  // update tags in backend
                  await addTagToMission(row.id, tagName);

                  // update tags in frontend
                  const tagColor =
                    allTags.find((tag) => tag.name === tagName)?.color ||
                    "#000000";
                  const existingTag = { name: tagName, color: tagColor };
                  const updateMissionTags = (mission: RenderedMission) =>
                    mission.id === row.id
                      ? { ...mission, tags: [...mission.tags, existingTag] }
                      : mission;
                  setFetchedData(fetchedData.map(updateMissionTags));
                  setRenderedData(renderedData.map(updateMissionTags));
                }}
                onRemoveTag={async (tagName) => {
                  // update tags in backend
                  await removeTagFromMission(row.id, tagName);
                  const missionsWithTag = await getMissionsByTag(tagName);
                  if (missionsWithTag.length === 0) {
                    // delete tag from database if no missions are using it
                    await deleteTag(tagName);
                    setAllTags(allTags.filter((tag) => tag.name !== tagName));
                  }

                  // update tags in frontend
                  const updateMissionTags = (mission: RenderedMission) =>
                    mission.id === row.id
                      ? {
                          ...mission,
                          tags: mission.tags.filter(
                            (tag) => tag.name !== tagName,
                          ),
                        }
                      : mission;
                  setFetchedData(fetchedData.map(updateMissionTags));
                  setRenderedData(renderedData.map(updateMissionTags));
                }}
                onEditTag={async (tagName, newName, newColor) => {
                  // update tag name in backend
                  await changeTagName(tagName, newName);
                  // update tag color in backend
                  if (!isValidHexColor(newColor)) return;
                  await changeTagColor(newName, newColor);

                  // update tag in frontend
                  const updateTag = (mission: RenderedMission) => ({
                    ...mission,
                    tags: mission.tags.map((tag) =>
                      tag.name === tagName
                        ? { name: newName, color: newColor }
                        : tag,
                    ),
                  });
                  setAllTags(
                    allTags.map((tag) =>
                      tag.name === tagName
                        ? { name: newName, color: newColor }
                        : tag,
                    ),
                  );
                  setFetchedData(fetchedData.map(updateTag));
                  setRenderedData(renderedData.map(updateTag));
                }}
                onDeleteAllTags={async () => {
                  // update tags in backend
                  for (let i = 0; i < row.tags.length; i++) {
                    await removeTagFromMission(row.id, row.tags[i].name);
                    const missionsWithTag = await getMissionsByTag(
                      row.tags[i].name,
                    );
                    if (missionsWithTag.length === 0) {
                      // delete tag from database if no missions are using it
                      await deleteTag(row.tags[i].name);
                      setAllTags(
                        allTags.filter((tag) => tag.name !== row.tags[i].name),
                      );
                    }
                  }

                  // update tags in frontend
                  const clearTags = (mission: RenderedMission) =>
                    mission.id === row.id ? { ...mission, tags: [] } : mission;
                  setFetchedData(fetchedData.map(clearTags));
                  setRenderedData(renderedData.map(clearTags));
                }}
              />
            </Popover.Dropdown>
          </Popover>
        </Group>
      </Table.Td>
    </Table.Tr>
  ));

  const columns: { key: keyof RenderedMission; label: string }[] = [
    { key: "name", label: "Name" },
    { key: "location", label: "Location" },
    { key: "totalDuration", label: "Duration" },
    { key: "totalSize", label: "Size" },
    { key: "robot", label: "Robot" },
    { key: "date", label: "Date" },
    { key: "notes", label: "Notes" },
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
