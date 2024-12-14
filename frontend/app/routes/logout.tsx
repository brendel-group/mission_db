import { sessionStorage } from "~/utilities/LoginHandler";
import {
  LoaderFunctionArgs,
  redirect,
} from "@remix-run/node";

export async function loader({ request }: LoaderFunctionArgs) {
  let session = await sessionStorage.getSession(request.headers.get("cookie"));
  return redirect("/login", {
    headers: { "Set-Cookie": await sessionStorage.destroySession(session) },
  });
}
