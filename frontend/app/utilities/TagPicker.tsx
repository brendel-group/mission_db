import React, { useState } from "react";
import {
  Badge,
  Button,
  Group,
  Menu,
  TextInput,
  Stack,
  ColorPicker,
  ColorInput,
} from "@mantine/core";
import { IconTrash, IconPlus, IconPalette } from "@tabler/icons-react";
import { Tag } from "~/data";

interface TagPickerProps {
  tags: Tag[];
  onAddNewTag: (tagName: string, tagColor: string) => void;
  onRemoveTag: (tagName: string) => void;
  onChangeTagColor: (tagName: string, newColor: string) => void;
}

export const TagPicker: React.FC<TagPickerProps> = ({
  tags,
  onAddNewTag,
  onRemoveTag,
  onChangeTagColor,
}) => {
  const [newTagName, setNewTagName] = useState("");
  const [selectedColor, setSelectedColor] = useState("#390099");
  const [newTagNameError, setNewTagNameError] = useState<string | null>(null);
  const [newTagColorError, setNewTagColorError] = useState<string | null>(null);
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

  function isHexCode(str: string) {
    const hexRegex = /^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$/;
    return hexRegex.test(str);
  }

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
      if (!isHexCode(selectedColor)) {
        setNewTagColorError("Color input is not a valid hex code");
        setSelectedColor("#390099");
        return;
      }
      onAddNewTag(newTagName, selectedColor);
      setNewTagName("");
      setNewTagNameError(null);
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
          disabled={!newTagName}
        >
          <IconPlus size={16} />
        </Button>
      </Group>

      {/*color input*/}
      <ColorInput
        placeholder="placeholder"
        value={selectedColor}
        onChange={setSelectedColor}
        style={{ marginBottom: -7, marginTop: 1 }}
        error={newTagColorError}
        onKeyDown={(e) => {
          e.key === "Enter" && handleAddTag();
        }}
      />

      {/*color picker*/}
      <ColorPicker
        onChange={setSelectedColor}
        value={selectedColor}
        swatchesPerRow={8}
        swatches={swatches}
        withPicker={false}
        style={{ width: "100%" }}
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
            <Menu
              withArrow
              shadow="md"
              styles={{
                dropdown: {
                  padding: 6,
                },
              }}
            >
              <Menu.Target>
                <Button
                  size="xs"
                  color="gray"
                  variant="subtle"
                  style={{ padding: 0 }}
                >
                  <IconPalette size={16} />
                </Button>
              </Menu.Target>
              <Menu.Dropdown>
                <Stack gap={0}>
                  <ColorInput
                    size="sm"
                    value={tag.color}
                    onChange={(color) => onChangeTagColor(tag.name, color)}
                    error={newTagColorError}
                    style={{ width: "179px", marginBottom: -3, marginTop: 2 }}
                  />
                  <ColorPicker
                    size="xs"
                    onChange={(color) => onChangeTagColor(tag.name, color)}
                    withPicker={false}
                    swatchesPerRow={4}
                    swatches={swatches}
                    style={{ marginBottom: -1 }}
                  />
                </Stack>
              </Menu.Dropdown>
            </Menu>

            {/* Button to remove tag */}
            <Button
              size="xs"
              color="red"
              variant="subtle"
              onClick={() => onRemoveTag(tag.name)}
              style={{ padding: 0 }}
            >
              <IconTrash size={16} />
            </Button>
          </Group>
        </Group>
      ))}
    </Stack>
  );
};
