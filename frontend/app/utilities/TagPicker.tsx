import React, { useState } from "react";
import { Badge, Button, Group, Menu, TextInput, Stack } from "@mantine/core";
import { IconTrash, IconPlus } from "@tabler/icons-react";
import { getRandomColor } from "~/utilities/ColorHelper";
import { Tag } from "~/data";

interface TagPickerProps {
  tags: Tag[];
  onAddTag: (newTag: Tag) => void;
  onRemoveTag: (tagName: string) => void;
}

export const TagPicker: React.FC<TagPickerProps> = ({
  tags,
  onAddTag,
  onRemoveTag,
}) => {
  const [newTagName, setNewTagName] = useState("");

  const handleAddTag = () => {
    if (newTagName) {
      onAddTag({ name: newTagName, color: getRandomColor() });
      setNewTagName("");
    }
  };

  return (
    <Menu.Dropdown>
      <Stack gap={4}>
        <TextInput
          value={newTagName}
          onChange={(e) => setNewTagName(e.target.value)}
          placeholder="add a new tag"
        />
        <Button onClick={handleAddTag} fullWidth>
          <IconPlus size={16} />
        </Button>
        {tags.map((tag) => (
          <Group key={tag.name} gap="apart">
            <Badge
              color={tag.color}
              variant="light"
              style={{ textTransform: "none" }}
            >
              {tag.name}
            </Badge>
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
        ))}
      </Stack>
    </Menu.Dropdown>
  );
};
