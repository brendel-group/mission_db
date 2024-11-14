const colors = ["blue", "green", "red", "cyan", "pink"];

export function getRandomColor() {
  return colors[Math.floor(Math.random() * colors.length)];
}