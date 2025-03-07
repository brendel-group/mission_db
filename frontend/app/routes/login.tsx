import {
  ActionFunctionArgs,
  data,
  LoaderFunctionArgs,
  redirect,
  type MetaFunction,
} from "@remix-run/node";
import { useActionData } from "@remix-run/react";
import { LoginView } from "~/pages/login/LoginPage";
import { authenticator, sessionStorage } from "~/utilities/LoginHandler";

export const meta: MetaFunction = () => {
  return [{ title: "Login" }];
};

// Second, we need to export an action function, here we will use the
// `authenticator.authenticate method`
export async function action({ request }: ActionFunctionArgs) {
  let user = null;

  try {
    user = await authenticator.authenticate("user-pass", request);
  } catch (error) {
    console.error(error);
    return "Invalid username or password"; //This message is rendered on the front end
  }

  let session = await sessionStorage.getSession(request.headers.get("cookie"));
  session.set("user", user);

  let backendCookie: string[] = [];
  if (user.backendCookie) backendCookie = user.backendCookie;
  let headers = new Headers({
    "set-cookie": await sessionStorage.commitSession(session),
  });
  backendCookie.forEach((cookie: string) => {
    headers.append("set-cookie", cookie);
  });

  throw redirect("/missions", {
    headers: headers,
  });
}

// Finally, we need to export a loader function to check if the user is already
// authenticated and redirect them to the dashboard
export async function loader({ request }: LoaderFunctionArgs) {
  let session = await sessionStorage.getSession(request.headers.get("cookie"));
  let user = session.get("user");
  if (user) throw redirect("/missions");
  return data(null);
}

export default function Index() {
  const data = useActionData<typeof action>(); // Render error message

  return <LoginView error={data}></LoginView>;
}
