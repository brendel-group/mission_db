import { sessionStorage } from "~/utilities/LoginHandler";
import { LoaderFunctionArgs, redirect } from "@remix-run/node";
import { attemptLogout } from "~/utilities/fetchapi";

export async function loader({ request }: LoaderFunctionArgs) {
  const cookieHeader = request.headers.get("cookie");
  let session = await sessionStorage.getSession(cookieHeader);
  let user = session.get("user");

  const cookies = Object.fromEntries(
    cookieHeader?.split(";").map((cookie) => cookie.trim().split("=")) || []
  );

  attemptLogout(cookies["csrftoken"], cookies["sessionid"]);

  let backendCookie: string[] = [];
  if (user.backendCookie) {
    backendCookie = user.backendCookie;
  }
  let headers = new Headers({
    "set-cookie": await sessionStorage.destroySession(session),
  });
  backendCookie.forEach((cookie: string) => {
    let name = cookie.split("=", 1)[0];
    cookie = cookie.replace(/(sessionid|csrftoken)=[a-zA-Z0-9]*;/, `${name}=;`);
    cookie = cookie.replace(
      /[Ee]xpires=[a-zA-Z0-9 ,:]*;/,
      "Expires=Thu, 01 Jan 1970 00:00:00 GMT;"
    );
    cookie = cookie.replace(/[Mm]ax-[Aa]ge=[0-9]*;/, "Max-Age=0;");
    headers.append("set-cookie", cookie);
  });

  return redirect("/login", {
    headers: headers,
  });
}
