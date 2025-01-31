import { getTopicsByFile, getAllowedTopics, createAllowedTopic, deleteAllowedTopic } from '../topics';
import { FETCH_API_BASE_URL } from '~/config';
import { getHeaders } from '../headers';

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

    describe("Topics Fetch Functions", () => {
        test("getTopicsByFile should fetch topics of a file successfully", async () => {
            const mockResponse = [{ id: 1, name: 'Topic 1' }];
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: jest.fn().mockResolvedValueOnce(mockResponse),
            });

            const result = await getTopicsByFile('file_path');
            expect(result).toEqual(mockResponse);
            expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/topics/file_path`, {
                method: 'GET',
                credentials: 'include',
                headers: getHeaders(),
            });
        });

        test("getTopicsByFile should throw an error if fetching topics fails", async () => {
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 404,
            });

            await expect(getTopicsByFile('file_path')).rejects.toThrow('Error 404: Failed to fetch topics of file file_path');
        });

        test("getAllowedTopics should fetch allowed topics successfully", async () => {
            const mockResponse = [{ id: 1, name: 'Allowed Topic 1' }];
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: jest.fn().mockResolvedValueOnce(mockResponse),
            });

            const result = await getAllowedTopics();
            expect(result).toEqual(mockResponse);
            expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/topics-names`, {
                method: 'GET',
                credentials: 'include',
                headers: getHeaders(),
            });
        });

        test("getAllowedTopics should throw an error if fetching allowed topics fails", async () => {
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 404,
            });

            await expect(getAllowedTopics()).rejects.toThrow('Error 404: Failed to fetch allowed topics');
        });

        test("createAllowedTopic should create a new allowed topic successfully", async () => {
            const mockResponse = { id: 1, name: 'New Topic' };
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: jest.fn().mockResolvedValueOnce(mockResponse),
            });

            const result = await createAllowedTopic('New Topic');
            expect(result).toEqual(mockResponse);
            expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/topics-names/create`, {
                method: 'POST',
                credentials: 'include',
                headers: getHeaders(),
                body: JSON.stringify({ topic_name: 'New Topic' }),
            });
        });

        test("createAllowedTopic should throw an error if creating a new topic fails", async () => {
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 400,
            });

            await expect(createAllowedTopic('New Topic')).rejects.toThrow('Error 400: Failed to create topic New Topic');
        });

        test("deleteAllowedTopic should delete an allowed topic successfully", async () => {
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
            });

            const result = await deleteAllowedTopic('Topic to Delete');
            expect(result).toBe('Topic Topic to Delete successfully deleted from allowed topics');
            expect(fetch).toHaveBeenCalledWith(`${FETCH_API_BASE_URL}/topics-names/Topic to Delete`, {
                method: 'DELETE',
                credentials: 'include',
                headers: getHeaders(),
            });
        });

        test("deleteAllowedTopic should throw an error if deleting a topic fails", async () => {
            (fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 404,
            });

            await expect(deleteAllowedTopic('Topic to Delete')).rejects.toThrow('Error 404: Failed to delete topic Topic to Delete');
        });
    });
});
