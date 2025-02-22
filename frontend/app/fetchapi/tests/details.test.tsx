import { FETCH_API_BASE_URL } from "~/config";
import { FileData } from "~/data";
import {
  GetFilesByMission,
  getFileData,
  updateRobotField,
} from "../details";

/*
How to run the tests:
- cd to frontend directory
- run `npm test`
*/

// Mock fetch and global objects
global.fetch = jest.fn();
global.console = { ...console, error: jest.fn() };

describe("Fetch API Functions", () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
    (console.error as jest.Mock).mockClear();
  });

  // Detail Fetch Functions
  describe("Detail Fetching", () => {
    test("getDetailsByMission should fetch details of a mission", async () => {
      const mockResponse = [
        {
          file_url: "http://example.com/file/download/file1.mcap",
          video_path: "file1.mp4",
          video_url: "http://example.com/file/stream/file1.mcap",
          file_path: "file1.mcap",
          duration: "3600",
          size: "1024",
          robot: "hihi",
          type: "train",
        },
        {
          file_url: "http://example.com/file/download/file2.mcap",
          video_path: "file2.mp4",
          video_url: "http://example.com/file/stream/file2.mcap",
          file_path: "file2.mcap",
          duration: "1200",
          size: "2621440",
          robot: "haha",
          type: "test",
        },
      ];

      const expectedResponse: FileData[] = [
        {
          filePath: "file1.mcap",
          fileUrl: new URL("http://example.com/file/download/file1.mcap"),
          videoPath: "file1.mp4",
          videoUrl: new URL("http://example.com/file/stream/file1.mcap"),
          duration: "01:00:00",
          size: "1.00 KB",
          robot: "hihi",
          type: "train",
        },
        {
          filePath: "file2.mcap",
          fileUrl: new URL("http://example.com/file/download/file2.mcap"),
          videoPath: "file2.mp4",
          videoUrl: new URL("http://example.com/file/stream/file2.mcap"),
          duration: "00:20:00",
          size: "2.50 MB",
          robot: "haha",
          type: "test",
        },
      ];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const details = await GetFilesByMission(1);
      expect(details).toEqual(expectedResponse);
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/missions/1/files/`,
        {
          method: "GET",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        },
      );
    });

    test("getFileData should fetch data of a file", async () => {
      const mockResponse = {
        file_path: "file1.mcap",
        file_url: "http://example.com/file/download/file1.mcap",
        video_path: "file1.mp4",
        video_url: "http://example.com/file/stream/file1.mcap",
        duration: "60",
        size: "1024",
        robot: "hihi",
        type: "test",
      };

      const expectedResponse: FileData = {
        filePath: "file1.mcap",
        fileUrl: new URL("http://example.com/file/download/file1.mcap"),
        videoPath: "file1.mp4",
        videoUrl: new URL("http://example.com/file/stream/file1.mcap"),
        duration: "00:01:00",
        size: "1.00 KB",
        robot: "hihi",
        type: "test",
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const details = await getFileData("file1.mcap");
      expect(details).toEqual(expectedResponse);
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/file/file1.mcap`,
        {
          method: "GET",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        },
      );
    });

    test("updateRobotField should update robot field of a file", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
      });

      await updateRobotField("file1.mcap", "newRobot");
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/file/file1.mcap/update-robot/`,
        {
          method: "PUT",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ robot: "newRobot" }),
        },
      );
    });
  });
});
