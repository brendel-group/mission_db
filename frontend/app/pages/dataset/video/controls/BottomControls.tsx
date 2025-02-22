import { Box, Slider, UnstyledButton } from "@mantine/core";
import {
  IconCaretLeftFilled,
  IconCaretRightFilled,
  IconMaximize,
  IconPlayerPauseFilled,
  IconPlayerPlayFilled,
} from "@tabler/icons-react";
import { PlayerIcon } from "../VideoUtilities";

export function BottomControls({
  handleSeek,
  handlePlayPause,
  handleFullscreen,
  isPlaying,
  currentTime,
  duration,
}: {
  handleSeek: (value: number) => void;
  handlePlayPause: () => void;
  handleFullscreen: () => void;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
}) {
  return (
    <Box style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <UnstyledButton onClick={handlePlayPause}>
        <PlayerIcon>
          {isPlaying ? (
            <IconPlayerPauseFilled color="white" />
          ) : (
            <IconPlayerPlayFilled color="white" />
          )}
        </PlayerIcon>
      </UnstyledButton>

      <Slider
        color="orange"
        value={currentTime}
        min={0}
        max={duration || 0}
        step={0.1}
        onChange={handleSeek}
        style={{ flexGrow: 1 }}
        styles={{
          thumb: {
            display: "none",
          },
        }}
      />

      <UnstyledButton onClick={handleFullscreen}>
        <PlayerIcon>
          <IconMaximize stroke={2} />
        </PlayerIcon>
      </UnstyledButton>
    </Box>
  );
}
