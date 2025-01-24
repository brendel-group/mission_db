import { FETCH_API_BASE_URL } from "~/config";
import { Tag } from "~/data";
import {
  addTagToMission,
  changeTagColor,
  changeTagName,
  createTag,
  deleteTag,
  getMissionsByTag,
  getTags,
  getTagsByMission,
  removeTagFromMission,
} from "../tags";

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
        credentials: "include",
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
          credentials: "include",
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
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        }
      );
    });

    test("changeTagName should change the name of a tag by name", async () => {
      const mockResponse: Tag = {
        name: "ImportantTag",
        color: "#FF0000",
      };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce({
          //id: 1,
          name: "ImportantTag",
          color: "#FF0000",
        }),
      });
      const result = await changeTagName("ImportantTag", "NewTag");
      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(
        `${FETCH_API_BASE_URL}/tags/ImportantTag`,
        {
          method: "PUT",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: "NewTag" }),
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
          credentials: "include",
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
        credentials: "include",
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
          credentials: "include",
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
          credentials: "include",
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
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        }
      );
    });
  });
});
