import { Badge, Group, Menu } from "@mantine/core";
import { getRandomColor } from "~/utilities/ColorHelper";
import { IconPencil } from "@tabler/icons-react";

export function RenderTagsDetailsView({ tags }: { tags: string[] }) {
  return (
    <Group gap="xs">
      {tags.map((item) => (
        <Badge key={item} color={getRandomColor()} variant="light">
          {item}
        </Badge>
      ))}
      {
        <Menu>
          <Menu.Target>
            <Badge color="grey" variant="light" style={{ cursor: "pointer" }}>
              <IconPencil size={16} style={{ transform: "translateY(1px)" }} />
            </Badge>
          </Menu.Target>
          <Menu.Dropdown>
            <h3>Tag Picker</h3>
          </Menu.Dropdown>
        </Menu>
      }
    </Group>
  );
}

export function RenderTagsOverview({ tags }: { tags: string[] }) {
  return (
    <Group gap="xs">
      {tags.map((item) => (
        <Badge key={item} color={getRandomColor()} variant="light">
          {item}
        </Badge>
      ))}
    </Group>
  );
}
