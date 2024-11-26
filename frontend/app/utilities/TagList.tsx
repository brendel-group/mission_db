import { Badge, Group, Menu } from "@mantine/core";
import { getRandomColor } from "~/utilities/ColorHelper";
import { IconPencil } from "@tabler/icons-react";
import { Tag } from "~/data";

export function RenderTagsDetailView({ tags }: { tags: Tag[] }) {
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
          <Menu.Dropdown>
            {/*TODO: Implement tag picker*/}
            <h3>Tag Picker</h3>
          </Menu.Dropdown>
        </Menu>
      }
    </Group>
  );
}

export function RenderTagsOverview({ tags }: { tags: Tag[] }) {
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
    </Group>
  );
}
