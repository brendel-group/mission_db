import { LoaderFunctionArgs } from "@remix-run/node";
import {
  data,
  MetaFunction,
  redirect,
  useSearchParams,
} from "@remix-run/react";
import { CreateAppShell } from "~/layout/AppShell";
import { DatasetView } from "~/pages/dataset/DatasetView";
import { sessionStorage } from "~/utilities/LoginHandler";

export const meta: MetaFunction = () => {
  return [{ title: "Dataset" }];
};

export async function loader({ request }: LoaderFunctionArgs) {
  let session = await sessionStorage.getSession(request.headers.get("cookie"));
  let user = session.get("user");

  if (!user) throw redirect("/login");

  return data(null);
}

function Dataset() {
  const [searchParams] = useSearchParams();
  const fileName = searchParams.get("fileName");
  const duration = searchParams.get("duration");
  const size = searchParams.get("size");

  if (!fileName || !duration || !size)
    throw new Response(null, {
      status: 404,
      statusText: "Invalid file name, duration or size.",
    });

  return (
    <DatasetView file={fileName} duration={duration} size={size}></DatasetView>
  );
}

const App = () => {
  return (
    <CreateAppShell>
      <Dataset />
    </CreateAppShell>
  );
};

export default App;
