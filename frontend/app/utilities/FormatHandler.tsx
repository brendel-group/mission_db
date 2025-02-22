// Helper function to transform durations from seconds to hh:mm:ss
export function transformDurations(
  durations: string[],
  short_format: boolean = false
): string[] {
  return durations.map((duration) => {
    const totalSeconds = parseInt(duration, 10);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    if (short_format && hours === 0) {
      return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(
        2,
        "0"
      )}`;
    }

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

// Transforms file paths and removes the common path prefix. It returns the transformed file name list, but also the global
// path prefix.
// ["/home/simon/Desktop/Teamproject/polybot_mission_db/backend/media/2025.11.11_hiho/train_recording1.mcap",
// "/home/simon/Desktop/Teamproject/polybot_mission_db/backend/media/2025.11.11_hiho/train_recording2.mcap"]
// => common path: "/home/simon/Desktop/Teamproject/polybot_mission_db/backend/media/2025.11.11_hiho/"
// => files: ["train_recording1.mcap", "train_recording2.mcap"]
function convertSlash(path: string, usesBackslashes: boolean): string {
  return usesBackslashes ? path.replace(/\//g, "\\") : path;
}

export function transformFilePaths(filePaths: string[]): {
  commonPath: string;
  files: string[];
} {
  if (filePaths.length === 0) {
    return { commonPath: "", files: [] };
  }

  const firstPath = filePaths[0];
  const usesBackslashes = firstPath.includes("\\");

  const normalizedPaths = filePaths.map((p) => p.replace(/\\/g, "/"));

  if (normalizedPaths.length === 1) {
    const single = normalizedPaths[0];
    const segments = single.split("/");
    const fileName = segments.pop() ?? "";
    let commonPath = segments.join("/");
    if (commonPath) {
      commonPath += "/";
    }
    return {
      commonPath: convertSlash(commonPath, usesBackslashes),
      files: [convertSlash(fileName, usesBackslashes)],
    };
  }

  const splitPaths = normalizedPaths.map((p) => p.split("/"));
  const minSegmentsLength = Math.min(
    ...splitPaths.map((segments) => segments.length)
  );

  let commonSegmentCount = 0;
  for (let i = 0; i < minSegmentsLength; i++) {
    const segment = splitPaths[0][i];
    if (splitPaths.every((s) => s[i] === segment)) {
      commonSegmentCount++;
    } else {
      break;
    }
  }

  let commonPath = splitPaths[0].slice(0, commonSegmentCount).join("/");
  if (commonPath && !commonPath.endsWith("/")) {
    commonPath += "/";
  }

  const files = normalizedPaths.map((fullPath) => {
    if (commonPath && fullPath.startsWith(commonPath)) {
      return fullPath.slice(commonPath.length);
    }

    const segs = fullPath.split("/");
    return segs.pop() ?? "";
  });

  return {
    commonPath: convertSlash(commonPath, usesBackslashes),
    files: files.map((f) => convertSlash(f, usesBackslashes)),
  };
}
