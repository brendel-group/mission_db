import { LoaderFunctionArgs } from "@remix-run/node";
import {
  data,
  MetaFunction,
  redirect,
  useLoaderData,
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

  let url = new URL(request.url);
  const fileName = url.searchParams.get("fileName");
  const duration = url.searchParams.get("duration");
  const size = url.searchParams.get("size");

  if (!fileName || !duration || !size)
    throw new Response(null, {
      status: 400,
      statusText: "Invalid URL",
    });

  return {
    fileName,
    duration,
    size,
  };
}

function Dataset() {
  const { fileName, duration, size } = useLoaderData<typeof loader>();

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
