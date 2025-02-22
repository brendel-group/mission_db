import { useEffect, useRef, useState } from "react";
import { Box, Skeleton, Text } from "@mantine/core";
import { transformDurations } from "~/utilities/FormatHandler";
import { BottomControls } from "./controls/BottomControls";
import { CenterControls } from "./controls/CenterControls";

interface VideoComponentProps {
  videoUrl: URL | null;
  onLeftClick?: () => void;
  onRightClick?: () => void;
}

export function VideoComponent({
  videoUrl,
  onLeftClick,
  onRightClick,
}: VideoComponentProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);

  const [isHovered, setIsHovered] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  // Fetch the video as a blob and create an object URL
  useEffect(() => {
    if (!videoUrl) return;
    const controller = new AbortController();

    fetch(String(videoUrl), { signal: controller.signal })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.blob();
      })
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        setBlobUrl(url);
      })
      .catch((error) => {
        //console.error("Failed to load video blob:", error);
      });

    return () => {
      controller.abort();
      if (blobUrl) {
        URL.revokeObjectURL(blobUrl);
        setBlobUrl(null);
      }
    };
  }, [videoUrl]);

  // Play/pause handler
  const handlePlayPause = () => {
    if (!videoRef.current) return;

    if (videoRef.current.paused) {
      const playPromise = videoRef.current.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => setIsPlaying(true))
          .catch((error) => {
            console.error("Video play was interrupted or failed:", error);
            setIsPlaying(false);
          });
      }
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  // Seek handler
  const handleSeek = (value: number) => {
    if (!videoRef.current) return;
    videoRef.current.currentTime = value;
    setCurrentTime(value);
  };

  // Fullscreen handler
  const handleFullscreen = () => {
    if (!videoRef.current) return;
    if (!document.fullscreenElement) {
      videoRef.current
        .requestFullscreen()
        .catch((err) => console.error("Fullscreen request failed:", err));
    } else {
      document.exitFullscreen();
    }
  };

  // If no video is available, show a placeholder
  if (!videoUrl) {
    return (
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

  if (!blobUrl) {
    return (
      <Box style={{ width: 320, height: 320 }}>
        <Skeleton height={320} width={320} />
      </Box>
    );
  }

  return (
    <Box
      style={{
        position: "relative",
        width: 320,
        height: 320,
        backgroundColor: "#000",
        overflow: "hidden",
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <video
        ref={videoRef}
        src={blobUrl}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
        }}
        onTimeUpdate={() => {
          if (!videoRef.current) return;
          setCurrentTime(videoRef.current.currentTime);
        }}
        onLoadedMetadata={() => {
          if (!videoRef.current) return;
          setDuration(videoRef.current.duration);
        }}
        onEnded={() => {
          setIsPlaying(false);
        }}
        controls={false}
      />

      {isHovered && (
        <CenterControls
          isPlaying={isPlaying}
          onLeftClick={onLeftClick}
          onRightClick={onRightClick}
          handlePlayPause={handlePlayPause}
        />
      )}

      {isHovered && (
        <Box
          style={{
            position: "absolute",
            bottom: 0,
            width: "100%",
            padding: "8px",
            backgroundColor: "rgba(0,0,0,0.6)",
          }}
        >
          <BottomControls
            handlePlayPause={handlePlayPause}
            handleFullscreen={handleFullscreen}
            handleSeek={handleSeek}
            currentTime={currentTime}
            duration={duration}
            isPlaying={isPlaying}
          />
          <Box
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              color: "#fff",
            }}
          >
            <Text size="xs">File name</Text>
            <Text size="xs">
              {transformDurations([currentTime.toString()])[0]} /{" "}
              {transformDurations([duration.toString()])[0]}
            </Text>
          </Box>
        </Box>
      )}
    </Box>
  );
}
