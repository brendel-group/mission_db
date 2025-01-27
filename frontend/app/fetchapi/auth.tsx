import { FETCH_API_BASE_URL } from "~/config";
import { getHeaders } from "./headers";

// Login system
export const attemptLogin = async (
  username: string,
  password: string
): Promise<{ success: boolean; cookies?: string[] }> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/auth/login/`, {
    method: "POST",
    credentials: "include",
    headers: getHeaders(),
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) return { success: false };
  let cookies: string[] = [];
  response.headers.forEach((value: string, key: string) => {
    if (key.startsWith("set-cookie")) {
      cookies.push(value);
    }
  });

  return { success: true, cookies };
};

export const attemptLogout = async (
  csrfToken: string,
  sessionId: string
): Promise<void> => {
  let headers = getHeaders();

  headers["X-CSRFToken"] = csrfToken;
  headers["Cookie"] = "sessionid=" + sessionId + "; csrftoken=" + csrfToken;

  const response = await fetch(`${FETCH_API_BASE_URL}/auth/logout/`, {
    method: "POST",
    credentials: "include",
    headers: headers,
  });

  if (!response.ok) throw new Error("Failed to logout");
};
