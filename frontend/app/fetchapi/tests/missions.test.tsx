import { FETCH_API_BASE_URL } from "~/config";
import { MissionData } from "~/data";
import {
  createMission,
  deleteMission,
  getMission,
  getMissions,
  updateMission,
  setWasModified,
} from "../missions";

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

  // Missions Fetch Functions
  describe("Mission Fetching", () => {
    test("getMissions should fetch all missions", async () => {
      const mockMissions: MissionData[] = [
        {
          id: 1,
          name: "Test Mission",
          location: "Test Location",
          date: "2023-01-01",
          notes: "Test remarks",
        },
      ];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockMissions),
      });

      const result = await getMissions();
      expect(result).toEqual(mockMissions);
      expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/missions/`, {
        method: "GET",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });
    });

    test("createMission should create a new mission", async () => {
      const newMission: Omit<MissionData, "id"> = {
        name: "New Mission",
        location: "New Location",
        date: "2023-02-01",
        notes: "New remarks",
      };

      const mockResponse: MissionData = {
        id: 1,
        name: "New Mission",
        location: "New Location",
        date: "2023-02-01",
        notes: "New remarks",
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const result = await createMission(newMission);
      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/missions/create`,
        {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newMission),
        }
      );
    });

    test("getMission should fetch a single mission by ID", async () => {
      const mockMission: MissionData = {
        id: 1,
        name: "Single Mission",
        location: "Single Location",
        date: "2023-03-01",
        notes: "Single remarks",
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockMission),
      });

      const result = await getMission(1);
      expect(result).toEqual(mockMission);
      expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/missions/1`, {
        method: "GET",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });
    });

    test("updateMission should update an existing mission", async () => {
      const updatedMission: MissionData = {
        id: 1,
        name: "Updated Mission",
        location: "Updated Location",
        date: "2023-04-01",
        notes: "Updated remarks",
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(updatedMission),
      });

      const result = await updateMission(updatedMission);
      expect(result).toEqual(updatedMission);
      expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/missions/1`, {
        method: "PUT",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedMission),
      });
    });

    test("deleteMission should delete a mission by ID", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({ ok: true });

      await deleteMission(1);
      expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/missions/1`, {
        method: "DELETE",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });
    });

    test("setWasModified should set the was_modified flag for a mission", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({ ok: true });

      await setWasModified(1, true);
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/missions/1/was_modified`,
        {
          method: "PUT",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ was_modified: true }),
        }
      );
    });
  });
});
