import { Badge, Group, Menu } from "@mantine/core";
import { getRandomColor } from "~/utilities/ColorHelper";

export function RenderTags({ tags }: { tags: string[] }) {
  return (
    <Group gap="xs">
      {tags.slice(0, 6).map((item) => (
        <Badge key={item} color={getRandomColor()} variant="light">
          {item}
        </Badge>
      ))}
      {
        <Menu>
          <Menu.Target>
            <Badge color="red" variant="light" style={{ cursor: "pointer" }}>
              Edit tags
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
