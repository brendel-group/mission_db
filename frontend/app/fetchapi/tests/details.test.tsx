import { FETCH_API_BASE_URL } from "~/config";
import { DetailViewData, FileData } from "~/data";
import {
  getDetailsByMission,
  getFormattedDetails,
  getRobotNames,
  getTotalDuration,
  getTotalSize,
  getFileData,
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
          file_path: "file1.mcap",
          video_path: "file1.mp4",
          duration: "60000",
          size: "1024",
          robot: "hihi",
        },
        {
          file_path: "file2.mcap",
          video_path: "file2.mp4",
          duration: "1200",
          size: "2621440",
          robot: "haha",
        },
      ];

      const expectedResponse: DetailViewData = {
        files: ["file1.mcap", "file2.mcap"],
        videos: ["file1.mp4", "file2.mp4"],
        durations: ["60000", "1200"],
        sizes: ["1024", "2621440"],
        robots: ["hihi", "haha"],
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const details = await getDetailsByMission(1);
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

    test("getFormattedDetails should fetch details of a mission and format them", async () => {
      const mockResponse = [
        {
          file_path: "file1.mcap",
          video_path: "file1.mp4",
          duration: "60000",
          size: "1024",
          robot: "hihi",
        },
        {
          file_path: "file2.mcap",
          video_path: "file2.mp4",
          duration: "1200",
          size: "2621440",
          robot: "haha",
        },
      ];

      const expectedResponse: DetailViewData = {
        files: ["file1.mcap", "file2.mcap"],
        videos: ["file1.mp4", "file2.mp4"],
        durations: ["16:40:00", "00:20:00"],
        sizes: ["1.00 KB", "2.50 MB"],
        robots: ["hihi", "haha"],
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const details = await getFormattedDetails(1);
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

    test("getTotalDuration should fetch total duration of all files of a mission and format them", async () => {
      const mockResponse = [
        {
          file_path: "file1.mcap",
          duration: "60000",
          size: "1024",
        },
        {
          file_path: "file2.mcap",
          duration: "1200",
          size: "2621440",
        },
      ];

      const expectedResponse: string = "17:00:00";

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const details = await getTotalDuration(1);
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

    test("getTotalSize should fetch total size of all files of a mission and format them", async () => {
      const mockResponse = [
        {
          file_path: "file1.mcap",
          duration: "60000",
          size: "1024",
        },
        {
          file_path: "file2.mcap",
          duration: "1200",
          size: "2621440",
        },
      ];

      const expectedResponse: string = "2.50 MB";

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const details = await getTotalSize(1);
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

    test("getRobotNames", async () => {
      const mockResponse = [
        {
          file_path: "file1.mcap",
          robot: "hihi",
          duration: "60000",
          size: "1024",
        },
        {
          file_path: "file2.mcap",
          robot: "haha",
          duration: "1200",
          size: "2621440",
        },
      ];

      const expectedResponse: string[] = ["hihi", "haha"];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const details = await getRobotNames(1);
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
  });
});
