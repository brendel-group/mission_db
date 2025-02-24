import { Button, Group } from "@mantine/core";
import { useClipboard } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { IconClipboard, IconDownload } from "@tabler/icons-react";

export function ActionButtons({
  fileUrl,
  filePath,
  displayFile,
}: {
  fileUrl: URL | null;
  filePath: string;
  displayFile: string;
}) {
  if (fileUrl === null) return <div />;

  const clipboard = useClipboard({ timeout: 500 });

  return (
    <Group>
      {filePath.length > 0 && (
        <Button
          onClick={(e) => {
            e.stopPropagation();
            clipboard.copy(filePath);

            notifications.clean();

            notifications.show({
              title: "Copied to clipboard!",
              message: filePath,
              color: "orange",
              radius: "md",
            });
          }}
          variant="light"
          color="orange"
          leftSection={<IconClipboard stroke={2} size={14} color="#fd7e14" />}
        >
          Copy to clipboard
        </Button>
      )}

      <Button
        onClick={(e) => {
          e.stopPropagation();

          const link = document.createElement("a");
          link.href = fileUrl.toString();
          link.download = displayFile;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }}
        variant="light"
        color="orange"
        leftSection={<IconDownload stroke={2} size={14} color="#fd7e14" />}
      >
        Download
      </Button>

      <Button
        onClick={(e) => {
          e.stopPropagation();

          const link = document.createElement("a");
          link.href =
            "foxglove://open?ds=remote-file&ds.url=" + fileUrl.toString();
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }}
        variant="light"
        color="orange"
        leftSection={
          <img
            src="/fox_glove.svg"
            alt="Fox Glove Icon"
            style={{ width: "14px", height: "14px" }}
          />
        }
      >
        Open in Foxglove
      </Button>
    </Group>
  );
}
