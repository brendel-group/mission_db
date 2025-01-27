// Helper function to transform durations from seconds to hh:mm:ss
export function transformDurations(durations: string[]): string[] {
  return durations.map((duration) => {
    const totalSeconds = parseInt(duration, 10);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(
      2,
      "0"
    )}:${String(seconds).padStart(2, "0")}`;
  });
}

// Helper function to transform sizes from bytes to megabytes
export function transformSizes(sizes: string[]): string[] {
  return sizes.map((size) => {
    const bytes = parseInt(size, 10);
    const kilobytes = bytes / 1024;
    const megabytes = kilobytes / 1024;
    const gigabytes = megabytes / 1024;

    let value = bytes;
    let unit = "B";

    if (megabytes < 1) {
      value = kilobytes;
      unit = "KB";
    } else if (gigabytes < 1) {
      value = megabytes;
      unit = "MB";
    } else {
      value = gigabytes;
      unit = "GB";
    }

    return `${value.toFixed(2)} ${unit}`;
  });
}

// This functions returns the robot names in the format x, y and z.
// For duplicate robot names, only the first occurance is used, e.g. x, y, x -> x and y and the camel case is ignored,
// meaning x, y, X -> x and y.
export function formatRobotNames(
  robotNames: string[] | undefined | null,
  and_separated: boolean = true
): string {
  if (!robotNames) {
    return "";
  }

  // Create a Set to track normalized names and filter duplicates
  const seen = new Set<string>();
  const uniqueRobots = robotNames.filter((name) => {
    if (!name) {
      return false;
    }
    const normalizedName = name.toLowerCase();
    if (seen.has(normalizedName)) {
      return false;
    }
    seen.add(normalizedName);
    return true;
  });

  if (uniqueRobots.length === 0) {
    return "";
  } else if (uniqueRobots.length === 1) {
    return uniqueRobots[0];
  } else if (and_separated) {
    const lastRobot = uniqueRobots.pop();
    return `${uniqueRobots.join(", ")} and ${lastRobot}`;
  } else {
    return uniqueRobots.join(", ");
  }
}
