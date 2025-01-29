import { Skeleton } from "@mantine/core";
import { LoaderFunctionArgs } from "@remix-run/node";
import {
  data,
  MetaFunction,
  redirect,
  useLoaderData,
  useSearchParams,
} from "@remix-run/react";
import { stringify } from "postcss";
import { useEffect, useState } from "react";
import { FileData } from "~/data";
import { getFileData } from "~/fetchapi/details";
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

  if (!fileName)
    throw new Response(null, {
      status: 400,
      statusText: "Invalid URL",
    });

  return {
    fileName,
  };
}

function Dataset() {
  const { fileName } = useLoaderData<typeof loader>();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // File
  const [fileData, setFileData] = useState<FileData>();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const file: FileData = await getFileData(fileName);
        setFileData(file);
      } catch (e: any) {
        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError("An unknown error occurred during mission fetching");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [fileName]);

  if (loading) return <Skeleton style={{ height: "30vh" }} />;
  if (error) return <p>Error: {error}</p>;
  if (!fileData) return <p>No data available</p>;

  return (
    <DatasetView
      file={fileData.filePath}
      fileUrl={fileData.fileUrl}
      video={fileData.videoPath}
      videoUrl={fileData.videoUrl}
      duration={fileData.duration}
      size={fileData.size}
      robot={fileData.robot}
    ></DatasetView>
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
