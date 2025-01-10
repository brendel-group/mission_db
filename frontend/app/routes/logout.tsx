import { sessionStorage } from "~/utilities/LoginHandler";
import { LoaderFunctionArgs, redirect } from "@remix-run/node";
import { attemptLogout } from "~/utilities/fetchapi";

export async function loader({ request }: LoaderFunctionArgs) {
  const cookieHeader = request.headers.get("cookie");
  let session = await sessionStorage.getSession(cookieHeader);
  let user = session.get("user");

  const cookies = Object.fromEntries(
    cookieHeader
      ?.split(";")
      .map((cookie) => cookie.trim().split("=")) || []
  );

  attemptLogout(cookies["csrftoken"], cookies["sessionid"]);

  let secure = "";
  if (user?.backendCookie?.toLowerCase().includes("secure;"))
    secure = " Secure;";

  return redirect("/login", {
    headers: {
      "Set-Cookie":
        (await sessionStorage.destroySession(session)) +
        ", csrftoken=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly;" +
        secure +
        " SameSite=Lax, " +
        " sessionid=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly;" +
        secure +
        " SameSite=Lax",
    },
  });
}
