import {
  data,
  redirect,
  type LoaderFunctionArgs,
  type MetaFunction,
} from "@remix-run/node";
import { CreateAppShell } from "~/layout/AppShell";
import SettingsPage from "~/pages/SettingsPage";
import { sessionStorage } from "~/utilities/LoginHandler";

export const meta: MetaFunction = () => {
  return [{ title: "Settings" }];
};

export async function loader({ request }: LoaderFunctionArgs) {
  let session = await sessionStorage.getSession(request.headers.get("cookie"));
  let user = session.get("user");

  if (!user) throw redirect("/login");

  return data(null);
}

export default function Index() {
  return (
    <CreateAppShell>
      <div>
        <SettingsPage />
      </div>
    </CreateAppShell>
  );
}
