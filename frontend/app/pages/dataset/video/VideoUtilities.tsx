import { ThemeIcon } from "@mantine/core";
import React from "react";

interface PlayerIconProps {
  children: React.ReactNode;
  size?: number;
}

export function PlayerIcon({ children, size = 60 }: PlayerIconProps) {
  return (
    <ThemeIcon
      variant="light"
      color="white"
      size={size}
      style={{
        backgroundColor: "transparent",
        border: "none",
        boxShadow: "none",
        padding: 0,
      }}
    >
      {children}
    </ThemeIcon>
  );
}
