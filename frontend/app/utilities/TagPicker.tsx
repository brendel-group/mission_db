import React, { useRef, useState } from "react";
import {
  Badge,
  Button,
  Group,
  TextInput,
  Stack,
  ColorInput,
  Popover,
} from "@mantine/core";
import { IconTrash, IconPlus, IconPalette } from "@tabler/icons-react";
import { Tag } from "~/data";

interface TagPickerProps {
  tags: Tag[];
  allTags: Tag[];
  onAddNewTag: (tagName: string, tagColor: string) => void;
  onAddExistingTag: (tagName: string) => void;
  onRemoveTag: (tagName: string) => void;
  onChangeTagColor: (tagName: string, newColor: string) => void;
}

export function isValidHexColor(input: string): boolean {
  // checks if input is a valid hex color with 3 or 6 characters
  const hexRegex = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/;
  return hexRegex.test(input);
}

export const TagPicker: React.FC<TagPickerProps> = ({
  tags,
  allTags,
  onAddNewTag,
  onAddExistingTag,
  onRemoveTag,
  onChangeTagColor,
}) => {
  const [newTagName, setNewTagName] = useState("");
  const [selectedColor, setSelectedColor] = useState("");
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const [newColor, setNewColor] = useState(selectedColor);
  const [changeColorError, setChangeColorError] = useState<string | null>(null);
  const [newTagNameError, setNewTagNameError] = useState<string | null>(null);
  const [newTagColorError, setNewTagColorError] = useState<string | null>(null);
  const [otherExistingTags, setOtherExistingTags] = useState<Tag[]>(
    allTags
      .filter(
        (tag) => !tags.some((existingTag) => existingTag.name === tag.name),
      )
      .sort((a, b) => a.name.localeCompare(b.name)),
  );
  const swatches = [
    "#390099",
    "#2c7da0",
    "#9e0059",
    "#ff0054",
    "#ff5400",
    "#ffbd00",
    "#007f5f",
    "#80b918",
  ];

  const handleColorChange = (tagName: string, newTagColor: string) => {
    setNewColor(newTagColor);

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      if (isValidHexColor(newTagColor)) {
        onChangeTagColor(tagName, newTagColor);
        setChangeColorError("");
      } else {
        setChangeColorError("Invalid color");
      }
    }, 1); // This delay is needed because without delay it is not possible to edit the color input field anymore
  };

  const handleAddTag = () => {
    if (newTagName) {
      // check if tag already exists
      if (tags.find((tag) => tag.name === newTagName)) {
        setNewTagNameError("This tag already exists");
        setNewTagName("");
        return;
      }
      // check if tag name is too long (max 42 characters)
      if (newTagName.length > 42) {
        setNewTagNameError("This tag name is too long");
        setNewTagName("");
        return;
      }

      // check if color is valid
      if (!isValidHexColor(selectedColor)) {
        setNewTagColorError("Invalid color");
        setSelectedColor("");
        return;
      }

      // check if the new tag name is already in existing tags
      if (otherExistingTags.find((tag) => tag.name === newTagName)) {
        setNewTagNameError("Please add this tag with the button below");
        setNewTagName("");
        return;
      }
      onAddNewTag(newTagName, selectedColor);
      setNewTagName("");
      setSelectedColor("");
      setNewTagColorError("");
      setNewTagNameError("");
    }
  };

  return (
    <Stack gap={4}>
      <Group gap="xs" style={{ display: "flex" }}>
        {/*input for new tag name*/}
        <TextInput
          value={newTagName}
          onChange={(e) => setNewTagName(e.target.value)}
          placeholder="Add a new tag"
          error={newTagNameError}
          onKeyDown={(e) => {
            e.key === "Enter" && handleAddTag();
          }}
          style={{ flex: 0.89 }}
        />

        {/*button to add tag*/}
        <Button
          onClick={handleAddTag}
          style={{ flex: 0.11, alignSelf: "flex-start" }}
          disabled={!newTagName || !isValidHexColor(selectedColor)}
        >
          <IconPlus size={16} />
        </Button>
      </Group>

      {/*color input*/}
      <ColorInput
        placeholder="#ffffff"
        value={selectedColor}
        onChange={setSelectedColor}
        style={{ marginTop: 3 }}
        onKeyDown={(e) => {
          e.key === "Enter" && handleAddTag();
        }}
        swatches={swatches}
        swatchesPerRow={8}
        popoverProps={{
          withinPortal: false,
        }}
        withEyeDropper={false}
        error={newTagColorError}
      />

      {/*list of tags*/}
      {tags.map((tag) => (
        <Group key={tag.name} gap="apart">
          <Badge
            color={tag.color}
            variant="light"
            style={{ textTransform: "none" }}
          >
            {tag.name}
          </Badge>
          <Group gap="xs">
            {/* Button to change tag color */}
            <Popover
              withArrow
              shadow="md"
              styles={{
                dropdown: {
                  padding: 6,
                },
              }}
              width={120}
              withinPortal={false}
              onOpen={() => {
                setNewColor(tag.color);
              }}
            >
              <Popover.Target>
                <Button
                  size="xs"
                  color="gray"
                  variant="subtle"
                  style={{ padding: 0 }}
                >
                  <IconPalette size={16} />
                </Button>
              </Popover.Target>
              <Popover.Dropdown style={{ padding: 6 }}>
                <Stack gap={0}>
                  <ColorInput
                    size="sm"
                    value={newColor}
                    onChange={(color) => {
                      handleColorChange(tag.name, color);
                    }}
                    popoverProps={{ withinPortal: false }}
                    swatches={swatches}
                    swatchesPerRow={8}
                    withEyeDropper={false}
                    error={changeColorError}
                  />
                </Stack>
              </Popover.Dropdown>
            </Popover>

            {/* Button to remove tag */}
            <Button
              size="xs"
              color="red"
              variant="subtle"
              onClick={() => {
                onRemoveTag(tag.name);
                setOtherExistingTags((prevTags) => [
                  ...prevTags,
                  { name: tag.name, color: tag.color },
                ]);
              }}
              style={{ padding: 0 }}
            >
              <IconTrash size={16} />
            </Button>
          </Group>
        </Group>
      ))}

      <Group gap="xs" style={{ marginTop: 3 }}>
        {/* add already existing tags */}
        <Popover withArrow withinPortal={false}>
          <Popover.Target>
            <Button
              color="#228be6"
              size="xs"
              style={{ textTransform: "none", cursor: "pointer", width: "48%" }}
            >
              Add existing tags
            </Button>
          </Popover.Target>
          <Popover.Dropdown
            style={{
              padding: 8,
              maxHeight: "200px",
              overflowY: "auto",
            }}
          >
            <Stack gap={8}>
              {otherExistingTags.map((tag) => (
                <Group key={tag.name} gap="md">
                  <Badge
                    color={tag.color}
                    variant="light"
                    style={{ textTransform: "none" }}
                  >
                    {tag.name}
                  </Badge>
                  <IconPlus
                    size={16}
                    color={"grey"}
                    style={{ cursor: "pointer" }}
                    onClick={() => {
                      onAddExistingTag(tag.name);
                      setOtherExistingTags(
                        otherExistingTags.filter(
                          (existingTag) => existingTag.name !== tag.name,
                        ),
                      );
                    }}
                  />
                </Group>
              ))}
              {otherExistingTags.length === 0 && (
                <div>no already existing tags</div>
              )}
            </Stack>
          </Popover.Dropdown>
        </Popover>

        {/* delete all tags */}
        <Button
          color="red"
          size="xs"
          style={{ textTransform: "none", cursor: "pointer", width: "48%" }}
          onClick={() => {
            if (
              window.confirm(
                "Are you sure you want to remove all tags from this mission?",
              )
            ) {
              tags.forEach((tag) => onRemoveTag(tag.name));
              setOtherExistingTags(
                allTags.sort((a, b) => a.name.localeCompare(b.name)),
              );
            }
          }}
        >
          Remove all tags
        </Button>
      </Group>
    </Stack>
  );
};
