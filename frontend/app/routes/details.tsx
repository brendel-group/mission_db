import { Skeleton } from "@mantine/core";
import { LoaderFunctionArgs } from "@remix-run/node";
import {
  data,
  MetaFunction,
  redirect,
  useSearchParams,
} from "@remix-run/react";
import { useEffect, useState } from "react";
import { MissionData, RenderedMission, Tag } from "~/data";
import { CreateAppShell } from "~/layout/AppShell";
import DetailsView from "~/pages/details/DetailsView";
import { getMission, getTagsByMission } from "~/utilities/fetchapi";
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
        const mission: MissionData = await getMission(numberId); // Fetch the mission using the REST API
        const tags: Tag[] = await getTagsByMission(numberId); //Fetch the tags for the mission
        tags.sort((a, b) => a.name.localeCompare(b.name));

        const transformedMission: RenderedMission = {
          id: mission.id,
          name: mission.name,
          location: mission.location,
          date: mission.date,
          notes: mission.notes,
          totalDuration: "00:00:00",
          totalSize: "0",
          robot: "?",
          tags: tags || [],
        };

        setMissionData(transformedMission);
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
