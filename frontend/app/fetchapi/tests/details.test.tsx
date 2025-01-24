import { FETCH_API_BASE_URL } from "~/config";
import { MissionData, Tag, DetailViewData } from "~/data";
import { getDetailsByMission, getFormattedDetails, getTotalDuration, getTotalSize } from "../details";

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
          file: {
            file_path: "file1.mcap",
            duration: "60000",
            size: "1024",
            robot: "hihi",
          },
        },
        {
          file: {
            file_path: "file2.mcap",
            duration: "1200",
            size: "2621440",
            robot: "haha",
          },
        },
      ];

      const expectedResponse: DetailViewData = {
        files: ["file1.mcap", "file2.mcap"],
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
        }
      );
    });

    test("getFormattedDetails should fetch details of a mission and format them", async () => {
      const mockResponse = [
        {
          file: {
            file_path: "file1.mcap",
            duration: "60000",
            size: "1024",
            robot: "hihi",
          },
        },
        {
          file: {
            file_path: "file2.mcap",
            duration: "1200",
            size: "2621440",
            robot: "haha",
          },
        },
      ];

      const expectedResponse: DetailViewData = {
        files: ["file1.mcap", "file2.mcap"],
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
        }
      );
    });

    test("getTotalDuration should fetch total duration of all files of a mission and format them", async () => {
      const mockResponse = [
        {
          file: {
            file_path: "file1.mcap",
            duration: "60000",
            size: "1024",
          },
        },
        {
          file: {
            file_path: "file2.mcap",
            duration: "1200",
            size: "2621440",
          },
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
        }
      );
    });

    test("getTotalSize should fetch total size of all files of a mission and format them", async () => {
      const mockResponse = [
        {
          file: {
            file_path: "file1.mcap",
            duration: "60000",
            size: "1024",
          },
        },
        {
          file: {
            file_path: "file2.mcap",
            duration: "1200",
            size: "2621440",
          },
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
        }
      );
    });
  });
});
