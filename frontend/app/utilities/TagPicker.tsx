import React, { useRef, useState, useEffect } from "react";
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
  onEditTag: (tagName: string, newTagName: string, newTagColor: string) => void;
  onDeleteAllTags: () => void;
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
  onEditTag,
  onDeleteAllTags,
}) => {
  const [newTagName, setNewTagName] = useState("");
  const [selectedColor, setSelectedColor] = useState("");
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const [changedTagName, setChangedTagName] = useState<string>("");
  const [newColor, setNewColor] = useState<string>("");
  const [changeTagNameError, setChangeTagNameError] = useState<string | null>(
    null,
  );
  const [changeColorError, setChangeColorError] = useState<string | null>(null);
  const [newTagNameError, setNewTagNameError] = useState<string | null>(null);
  const [newTagColorError, setNewTagColorError] = useState<string | null>(null);
  const [otherExistingTags, setOtherExistingTags] = useState<Tag[]>([]);
  const swatches = [
    "#ff5400",
    "#ffbd00",
    "#007f5f",
    "#80b918",
    "#2c7da0",
    "#390099",
    "#ff0054",
    "#9e0059",
  ];

  useEffect(() => {
    setOtherExistingTags(
      allTags
        .filter(
          (tag) => !tags.some((existingTag) => existingTag.name === tag.name),
        )
        .sort((a, b) => a.name.localeCompare(b.name)),
    );
  }, [tags, allTags]);

  const handleTagEdit = (
    tagName: string,
    newTagName: string,
    newTagColor: string,
  ) => {
    // check if tag name already exists
    if (tags.find((tag) => tag.name === newTagName) && tagName !== newTagName) {
      setChangeTagNameError("This tag name is already in use");
      return;
    }

    // check if tag name is too long (max 42 characters)
    if (newTagName.length > 42) {
      setChangeTagNameError("This tag name is too long");
      return;
    }

    // check if the new tag name is already in existing tags
    if (otherExistingTags.find((tag) => tag.name === newTagName)) {
      setChangeTagNameError(
        "Please add this tag with the 'Add existing tags' button",
      );
      return;
    }

    // check if color is valid
    if (!isValidHexColor(newTagColor)) {
      setChangeColorError("Invalid color");
      return;
    }

    // reset errors and update tag
    setChangeTagNameError("");
    setChangeColorError("");
    onEditTag(tagName, newTagName, newTagColor);
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
          onChange={(e) => {
            setNewTagName(e.target.value);
            setNewTagNameError("");
          }}
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
        onChange={(color) => {
          setSelectedColor(color);
          setNewTagColorError("");
        }}
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
          <Group gap="xs">
            {/* popover for tag edit */}
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
                setChangedTagName(tag.name);
                setNewColor(tag.color);
              }}
              onClose={() => {
                setChangeTagNameError("");
                setChangeColorError("");
              }}
            >
              <Popover.Target>
                <Badge
                  color={tag.color}
                  variant="light"
                  style={{ textTransform: "none", cursor: "pointer" }}
                >
                  {tag.name}
                </Badge>
              </Popover.Target>
              <Popover.Dropdown style={{ padding: 6 }}>
                {/* edit tag menu */}
                <Stack gap={6}>
                  {/* name change */}
                  <TextInput
                    size="sm"
                    value={changedTagName}
                    onChange={(e) => (
                      setChangedTagName(e.target.value),
                      setChangeTagNameError("")
                    )}
                    onKeyDown={(e) => {
                      e.key === "Enter" &&
                        handleTagEdit(tag.name, changedTagName, newColor);
                    }}
                    error={changeTagNameError}
                  />
                  {/* color change */}
                  <ColorInput
                    size="sm"
                    value={newColor}
                    onChange={(color) => {
                      setNewColor(color);
                      setChangeColorError("");
                    }}
                    onKeyDown={(e) => {
                      e.key === "Enter" &&
                        handleTagEdit(tag.name, changedTagName, newColor);
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
                <span style={{ color: "grey" }}>No more tags to add</span>
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
              onDeleteAllTags();
            }
          }}
        >
          Remove all tags
        </Button>
      </Group>
    </Stack>
  );
};
