import { Badge, Group, Popover } from "@mantine/core";
import { IconPencil } from "@tabler/icons-react";
import { Tag } from "~/data";
import { TagPicker } from "./TagPicker";
import { setWasModified } from "~/fetchapi/missions";

import { useState } from "react";
import { addTagToMission, changeTagColor, changeTagName, createTag, deleteTag, getMissionsByTag, removeTagFromMission } from "~/fetchapi/tags";

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
              const newTag = { name: tagName, color: tagColor };
              setTags([...tags, newTag]);
              setAllTags([...allTags, newTag]);

              // notify backend that mission was modified
              await setWasModified(missionId, true);
            }}
            onAddExistingTag={async (tagName) => {
              // update tags in backend
              await addTagToMission(missionId, tagName);

              // update tags in frontend
              const tagColor =
                allTags.find((tag) => tag.name === tagName)?.color || "#000000";
              const existingTag = { name: tagName, color: tagColor };
              setTags([...tags, existingTag]);

              // notify backend that mission was modified
              await setWasModified(missionId, true);
            }}
            onRemoveTag={async (tagName) => {
              // update tags in backend
              await removeTagFromMission(missionId, tagName);
              const missionsWithTag = await getMissionsByTag(tagName);
              if (missionsWithTag.length === 0) {
                // delete tag from database if no missions are using it
                await deleteTag(tagName);
                setAllTags(allTags.filter((tag) => tag.name !== tagName));
              }
              // update tags in frontend
              setTags(tags.filter((tag) => tag.name !== tagName));

              // notify backend that mission was modified
              await setWasModified(missionId, true);
            }}
            onEditTag={async (tagName, newName, newColor) => {
              // update tag in backend
              await changeTagName(tagName, newName);
              await changeTagColor(newName, newColor);

              // update tags in frontend
              setTags((prev) =>
                prev.map((tag) =>
                  tag.name === tagName
                    ? { name: newName, color: newColor }
                    : tag,
                ),
              );
              setAllTags((prev) =>
                prev.map((tag) =>
                  tag.name === tagName
                    ? { name: newName, color: newColor }
                    : tag,
                ),
              );

              // notify backend that mission was modified
              await setWasModified(missionId, true);
            }}
            onDeleteAllTags={async () => {
              // update tags in backend
              for (let i = 0; i < tags.length; i++) {
                await removeTagFromMission(missionId, tags[i].name);
                const missionsWithTag = await getMissionsByTag(tags[i].name);
                if (missionsWithTag.length === 0) {
                  // delete tag from database if no missions are using it
                  await deleteTag(tags[i].name);
                  setAllTags(
                    allTags.filter((tag) => tag.name !== tags[i].name),
                  );
                }
              }

              // update tags in frontend
              setTags([]);

              // notify backend that mission was modified
              await setWasModified(missionId, true);
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
