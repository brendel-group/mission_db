import {
  getMissions,
  createMission,
  getMission,
  updateMission,
  deleteMission,
  getTags,
  addTagToMission,
  removeTagFromMission,
  changeTagColor,
  createTag,
  deleteTag,
  getTagsByMission,
  getMissionsByTag,
} from "./fetchapi";
import { FETCH_API_BASE_URL } from "~/config";
import { MissionData, Tag } from "~/data";

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
      });
    });
  });

  // Tag-related Functions
  describe("Tag Management", () => {
    test("getTags should fetch all tags", async () => {
      const mockTags: Tag[] = [{ name: "Tag1", color: "#FF0000" }];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockTags),
      });

      const result = await getTags();
      expect(result).toEqual(mockTags);
      expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/tags/`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
    });

    test("addTagToMission should add a tag to a mission", async () => {
      const mockResponse = {
        mission_id: 1,
        tag_name: "Important",
      };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const result = await addTagToMission(1, "Important");
      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/mission-tags/create/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mission_id: 1, tag_name: "Important" }),
        }
      );
    });

    test("removeTagFromMission should remove a tag from a mission", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({ ok: true });

      await removeTagFromMission(1, "Important");
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/mission-tags/delete/1/Important`,
        {
          method: "DELETE",
        }
      );
    });

    test("changeTagColor should change the color of a tag by name", async () => {
      const mockResponse: Tag = {
        name: "ImportantTag",
        color: "#00FF00",
      };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce({
          //id: 1,
          name: "ImportantTag",
          color: "#00FF00",
        }),
      });

      const result = await changeTagColor("ImportantTag", "#00FF00");
      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/tags/ImportantTag`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: "ImportantTag", color: "#00FF00" }),
        }
      );
    });

    test("createTag should create a new tag", async () => {
      const newTag = { name: "NewTag", color: "#FF0000" };
      const mockResponse = { ...newTag };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const result = await createTag(newTag.name, newTag.color);
      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/tags/create/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTag),
      });
    });

    test("deleteTag should delete a tag by name", async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({ ok: true });

      await deleteTag("ImportantTag");
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/tags/ImportantTag`,
        {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
        }
      );
    });

    test("getTagsByMission should fetch tags for a mission", async () => {
      const mockResponse = [
        {
          name: "Tag1",
          color: "#FF0000",
        },
      ];
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const tags = await getTagsByMission(1);
      expect(tags).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/missions/tags/1`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }
      );
    });

    test("getMissionsByTag should fetch missions for a tag", async () => {
      const mockResponse = [
        {
          id: 1,
          name: "Mission1",
          location: "Location1",
        },
      ];
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce(mockResponse),
      });

      const missions = await getMissionsByTag("ImportantTag");
      expect(missions).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/tags/missions/ImportantTag`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }
      );
    });
  });
});
