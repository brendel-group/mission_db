import { Badge, Group, Popover } from "@mantine/core";
import { IconPencil } from "@tabler/icons-react";
import { Tag } from "~/data";
import { TagPicker, isValidHexColor } from "./TagPicker";

import {
  addTagToMission,
  changeTagColor,
  createTag,
  deleteTag,
  getMissionsByTag,
  removeTagFromMission,
} from "./fetchapi";
import { useState } from "react";

export function RenderTagsDetailView({
  tags_,
  allTags_,
  missionId,
}: {
  tags_: Tag[];
  allTags_: Tag[];
  missionId: number;
}) {
  const [tags, setTags] = useState<Tag[]>(tags_);
  const [allTags, setAllTags] = useState<Tag[]>(allTags_);

  return (
    <Group gap="xs">
      {/*edit button*/}
      <Popover>
        <Popover.Target>
          <Badge color="grey" variant="light" style={{ cursor: "pointer" }}>
            <IconPencil size={16} style={{ transform: "translateY(2px)" }} />
          </Badge>
        </Popover.Target>
        {/*Actions for the Tag Picker*/}
        <Popover.Dropdown
          style={{ padding: "10px", marginLeft: "75px", width: "300px" }}
        >
          <TagPicker
            tags={tags}
            allTags={allTags}
            onAddNewTag={async (tagName, tagColor) => {
              //update tags in backend
              await createTag(tagName, tagColor);
              await addTagToMission(missionId, tagName);
              // update tags in frontend
              setTags([...tags, { name: tagName, color: tagColor }]);
            }}
            onAddExistingTag={async (tagName) => {
              // update tags in backend
              await addTagToMission(missionId, tagName);
              // update tags in frontend
              setTags([
                ...tags,
                {
                  name: tagName,
                  color:
                    allTags.find((tag) => tag.name === tagName)?.color ||
                    "#000000",
                },
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
              isValidHexColor(newColor)
                ? changeTagColor(tagName, newColor)
                : null;

              // update tags in frontend
              setTags((prev) =>
                prev.map((tag) => {
                  if (tag.name === tagName) {
                    return { ...tag, color: newColor };
                  }
                  return tag;
                })
              );
            }}
          />
        </Popover.Dropdown>
      </Popover>
      {/*list of tags*/}
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
    </Group>
  );
}

export function RenderTagsOverview({
  tags,
  onTagClick,
}: {
  tags: Tag[];
  onTagClick: (tagName: string) => void;
}) {
  return (
    <Group gap="xs">
      {tags.map((item) => (
        <Badge
          key={item.name}
          color={item.color}
          variant="light"
          style={{ textTransform: "none" }}
          onClick={() => onTagClick(item.name)}
        >
          {item.name}
        </Badge>
      ))}
    </Group>
  );
}
