import { redirect, type LoaderFunctionArgs } from "@remix-run/node";
import { sessionStorage } from "~/utilities/LoginHandler";

export async function loader({ request }: LoaderFunctionArgs) {
  let session = await sessionStorage.getSession(request.headers.get("cookie"));
  let user = session.get("user");

  if (user) throw redirect("/missions");
  if (!user) throw redirect("/login");
}
