import React, { useState } from "react";
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
  onAddNewTag: (tagName: string, tagColor: string) => void;
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
  onAddNewTag,
  onRemoveTag,
  onChangeTagColor,
}) => {
  const [newTagName, setNewTagName] = useState("");
  const [selectedColor, setSelectedColor] = useState("");
  const [newTagError, setNewTagError] = useState<string | null>(null);
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

  const handleAddTag = () => {
    if (newTagName) {
      // check if tag already exists
      if (tags.find((tag) => tag.name === newTagName)) {
        setNewTagError("This tag already exists");
        setNewTagName("");
        return;
      }
      // check if tag name is too long (max 42 characters)
      if (newTagName.length > 42) {
        setNewTagError("This tag name is too long");
        setNewTagName("");
        return;
      }

      // check if color is valid
      if (!isValidHexColor(selectedColor)) {
        setNewTagError("Invalid color");
        return;
      }
      onAddNewTag(newTagName, selectedColor);
      setNewTagName("");
      setSelectedColor("");
      setNewTagError(null);
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
          error={newTagError}
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
              <Popover.Dropdown>
                <Stack gap={0}>
                  <ColorInput
                    size="sm"
                    value={tag.color}
                    onChange={(color) => {
                      onChangeTagColor(tag.name, color);
                    }}
                    popoverProps={{ withinPortal: false }}
                    swatches={swatches}
                    swatchesPerRow={8}
                  />
                </Stack>
              </Popover.Dropdown>
            </Popover>

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
