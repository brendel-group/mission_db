import { Text } from "@mantine/core";

export function VideoComponent({ videoUrl }: { videoUrl: URL | null }) {
  return videoUrl ? (
    <iframe
      width="320"
      height="320"
      src={String(videoUrl)}
      allowFullScreen
    ></iframe>
  ) : (
    <div
      style={{
        width: "320px",
        height: "320px",
        backgroundColor: "#e0e0e0",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Text size="lg" color="gray">
        Not available
      </Text>
    </div>
  );
}
