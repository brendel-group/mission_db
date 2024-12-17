import { Skeleton } from "@mantine/core";
import { LoaderFunctionArgs } from "@remix-run/node";
import {
  data,
  MetaFunction,
  redirect,
  useSearchParams,
} from "@remix-run/react";
import { useEffect, useState } from "react";
import { CreateAppShell } from "~/layout/AppShell";
import DetailsView from "~/pages/details/DetailsView";
import { fetchAndTransformMission } from "~/utilities/fetchapi";
import { sessionStorage } from "~/utilities/LoginHandler";

export const meta: MetaFunction = () => {
  return [{ title: "Details" }];
};

export async function loader({ request }: LoaderFunctionArgs) {
  let session = await sessionStorage.getSession(request.headers.get("cookie"));
  let user = session.get("user");

  if (!user) throw redirect("/login");

  return data(null);
}

function Detail() {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");

  if (!id) return <h1>Invalid URL</h1>;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [missionData, setMissionData] = useState<any | null>(null);

  const numberId = Number(id);

  if (isNaN(numberId)) return <h1>Invalid URL</h1>;

  useEffect(() => {
    const fetchMission = async () => {
      try {
        const data = await fetchAndTransformMission(numberId);
        setMissionData(data);
      } catch (e: any) {
        if (e instanceof Error) {
          setError(e.message);
        } else {
          setError("An unknown error occurred");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchMission();
  }, [id]);

  if (loading) return <Skeleton style={{ height: "30vh" }} />;
  if (error) return <p>Error: {error}</p>;
  if (!missionData) return <p>No data available</p>;

  return <DetailsView missionData={missionData}></DetailsView>;
}

const App = () => {
  return (
    <CreateAppShell>
      <Detail />
    </CreateAppShell>
  );
};

export default App;
