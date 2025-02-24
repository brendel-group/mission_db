import { Box, UnstyledButton } from "@mantine/core";
import {
  IconCaretLeftFilled,
  IconCaretRightFilled,
  IconPlayerPauseFilled,
  IconPlayerPlayFilled,
} from "@tabler/icons-react";
import { PlayerIcon } from "../VideoUtilities";

export function CenterControls({
  onLeftClick,
  onRightClick,
  handlePlayPause,
  isPlaying,
}: {
  onLeftClick?: () => void;
  onRightClick?: () => void;
  handlePlayPause: () => void;
  isPlaying: boolean;
}) {
  return (
    <Box
      style={{
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        display: "flex",
        gap: 5,
        alignItems: "center",
      }}
    >
      <UnstyledButton onClick={() => onLeftClick && onLeftClick()}>
        <PlayerIcon>
          <IconCaretLeftFilled color="white" />
        </PlayerIcon>
      </UnstyledButton>

      <UnstyledButton onClick={handlePlayPause}>
        <PlayerIcon>
          {isPlaying ? (
            <IconPlayerPauseFilled color="white" />
          ) : (
            <IconPlayerPlayFilled color="white" />
          )}
        </PlayerIcon>
      </UnstyledButton>

      <UnstyledButton onClick={() => onRightClick && onRightClick()}>
        <PlayerIcon>
          <IconCaretRightFilled color="white" />
        </PlayerIcon>
      </UnstyledButton>
    </Box>
  );
}
