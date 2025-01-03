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
  allTags: Tag[];
  onAddNewTag: (tagName: string, tagColor: string) => void;
  onRemoveTag: (tagName: string) => void;
  onChangeTagColor: (tagName: string, newColor: string) => void;
}

export const TagPicker: React.FC<TagPickerProps> = ({
  tags,
  allTags,
  onAddNewTag,
  onRemoveTag,
  onChangeTagColor,
}) => {
  const [newTagName, setNewTagName] = useState("");
  const [selectedColor, setSelectedColor] = useState("#390099");
  const [newTagNameError, setNewTagNameError] = useState<string | null>(null);
  const [otherExistingTags, setOtherExistingTags] = useState<Tag[]>(
    allTags.filter(
      (tag) => !tags.some((existingTag) => existingTag.name === tag.name),
    ),
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

  function isValidHexColor(input: string): boolean {
    // Der reguläre Ausdruck prüft, ob der Input entweder ein 3-stelliger (#RGB) oder 6-stelliger (#RRGGBB) Hex-Code ist
    const hexRegex = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{4})$/;
    return hexRegex.test(input);
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

      // check if the new tag name is already in existing tags
      if (otherExistingTags.find((tag) => tag.name === newTagName)) {
        setNewTagNameError("Please add this tag with the button below");
        setNewTagName("");
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
            <Popover withArrow shadow="md" width={120} withinPortal={false}>
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
                    value={tag.color}
                    onChange={(color) => onChangeTagColor(tag.name, color)}
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

      {/* add already existing tags */}
      <Popover withArrow withinPortal={false}>
        <Popover.Target>
          <Badge
            color="#228be6"
            style={{ textTransform: "none", cursor: "pointer" }}
          >
            Add existing tags
          </Badge>
        </Popover.Target>
        <Popover.Dropdown style={{ padding: 8 }}>
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
                    onAddNewTag(tag.name, tag.color);
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
    </Stack>
  );
};
