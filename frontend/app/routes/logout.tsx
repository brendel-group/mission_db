import { sessionStorage } from "~/utilities/LoginHandler";
import {
  LoaderFunctionArgs,
  redirect,
} from "@remix-run/node";
import { attemptLogout } from "~/utilities/fetchapi";

export async function loader({ request }: LoaderFunctionArgs) {
  let session = await sessionStorage.getSession(request.headers.get("cookie"));
  let crsf_token = session.get("csrftoken");

  attemptLogout(crsf_token);
  
  return redirect("/login", {
    headers: { "Set-Cookie": await sessionStorage.destroySession(session) },
  });
}
