import { Skeleton } from "@mantine/core";
import { LoaderFunctionArgs } from "@remix-run/node";
import { MetaFunction, redirect, useLoaderData } from "@remix-run/react";
import { useEffect, useState } from "react";
import { FileData, Topic } from "~/data";
import { getFileData } from "~/fetchapi/details";
import { getTopicsByFile } from "~/fetchapi/topics";
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
  const [fileTopics, setFileTopics] = useState<Topic[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [file, topics] = await Promise.all([
          getFileData(fileName),
          getTopicsByFile(fileName),
        ]);
        setFileData(file);
        setFileTopics(topics);
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
  if (!fileTopics) return <p>No topics available</p>;

  return <DatasetView data={fileData} topics={fileTopics}></DatasetView>;
}

const App = () => {
  return (
    <CreateAppShell>
      <Dataset />
    </CreateAppShell>
  );
};

export default App;
