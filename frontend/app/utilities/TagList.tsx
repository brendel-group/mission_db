import { Badge, Group, Menu } from "@mantine/core";
import { IconPencil } from "@tabler/icons-react";
import { Tag } from "~/data";
import { TagPicker } from "./TagPicker";
import {
  addTagToMission,
  changeTagColor,
  createTag,
  deleteTag,
  getMissionsByTag,
  removeTagFromMission,
} from "./fetchapi";
import { useState } from "react";

export function RenderTags({
  tags_,
  missionId,
}: {
  tags_: Tag[];
  missionId: number;
}) {
  const [tags, setTags] = useState<Tag[]>(tags_);

  return (
    <Group gap="xs">
      {tags.map((item) => (
        <Badge
          key={item.name}
          color={item.color}
          variant="light"
          style={{ textTransform: "none" }}
        >
          {item.name}
        </Badge>
      ))}
      {/*edit button*/}
      {
        <Menu>
          <Menu.Target>
            <Badge color="grey" variant="light" style={{ cursor: "pointer" }}>
              <IconPencil size={16} style={{ transform: "translateY(1px)" }} />
            </Badge>
          </Menu.Target>
          {/*Actions for the Tag Picker*/}
          <Menu.Dropdown style={{ padding: "10px" }}>
            <TagPicker
              tags={tags}
              onAddNewTag={(tagName, tagColor) => {
                //update tags in backend
                createTag(tagName, tagColor);
                addTagToMission(missionId, tagName);
                // update tags in frontend
                setTags([
                  ...tags,
                  { tagId: 0, name: tagName, color: tagColor },
                ]);
              }}
              onRemoveTag={async (tagName) => {
                // update tags in backend
                await removeTagFromMission(missionId, tagName);
                const missionsWithTag = await getMissionsByTag(tagName);
                if (missionsWithTag.length === 0) {
                  // delete tag from database if no missions are using it
                  deleteTag(tagName);
                }
                // update tags in frontend
                setTags(tags.filter((tag) => tag.name !== tagName));
              }}
              onChangeTagColor={(tagName, newColor) => {
                // update tag color in backend
                changeTagColor(tagName, newColor);

                // TODO update tags in frontend
                setTags((prev) =>
                  prev.map((tag) => {
                    if (tag.name === tagName) {
                      return { ...tag, color: newColor };
                    }
                    return tag;
                  }),
                );
              }}
            />
          </Menu.Dropdown>
        </Menu>
      }
    </Group>
  );
}
