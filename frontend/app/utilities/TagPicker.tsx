import React, { useState } from "react";
import {
  Badge,
  Button,
  Group,
  Menu,
  TextInput,
  Stack,
  ColorPicker,
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
  const [error, setError] = useState<string | null>(null);
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
        setError("This tag already exists");
        setNewTagName("");
        return;
      }
      // check if tag name is too long (max 42 characters)
      if (newTagName.length > 42) {
        setError("This tag name is too long");
        setNewTagName("");
        return;
      }
      onAddNewTag(newTagName, selectedColor);
      setNewTagName("");
      setError(null);
    }
  };

  return (
    <Stack gap={4}>
      <Group gap="xs" style={{ display: "flex", marginBottom: "2px" }}>
        {/*input for new tag name*/}
        <TextInput
          value={newTagName}
          onChange={(e) => setNewTagName(e.target.value)}
          placeholder="Add a new tag"
          error={error}
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
      {/*custom color picker*/}
      <div style={{ display: "flex", gap: "8px" }}>
        {swatches.map((swatch) => (
          <div
            key={swatch}
            style={{
              width: "30px",
              height: "30px",
              backgroundColor: swatch,
              border:
                selectedColor === swatch ? "3px solid black" : "1px solid gray",
              borderRadius: "4px",
              cursor: "pointer",
            }}
            onClick={() => setSelectedColor(swatch)}
          />
        ))}
      </div>

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
                  padding: 4,
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
                <ColorPicker
                  size="xs"
                  onChange={(color) => onChangeTagColor(tag.name, color)}
                  withPicker={false}
                  swatchesPerRow={4}
                  swatches={swatches}
                />
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
