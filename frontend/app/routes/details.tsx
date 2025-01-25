import { Skeleton } from "@mantine/core";
import { LoaderFunctionArgs } from "@remix-run/node";
import {
  data,
  MetaFunction,
  redirect,
  useSearchParams,
} from "@remix-run/react";
import { useEffect, useState } from "react";
import { DetailViewData, MissionData, RenderedMission, Tag } from "~/data";
import {
  getFormattedDetails,
  getTotalDuration,
  getTotalSize,
} from "~/fetchapi/details";
import { getMission } from "~/fetchapi/missions";
import { getTagsByMission } from "~/fetchapi/tags";
import { CreateAppShell } from "~/layout/AppShell";
import DetailsView from "~/pages/details/DetailsView";
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

  // Mission
  const [missionData, setMissionData] = useState<any | null>(null);

  // Tags
  const [allTags, setAllTags] = useState<any | null>(null);

  // Detail View data
  const [detailViewData, setDetailViewData] = useState<DetailViewData>();
  const [totalSize, setTotalSize] = useState<string>("0 GB");
  const [totalDuration, setTotalDuration] = useState<string>("00:00:00");

  const numberId = Number(id);

  if (isNaN(numberId))
    throw new Response(null, {
      status: 404,
      statusText: "Invalid ID.",
    });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const mission: MissionData = await getMission(numberId); // Fetch mission
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
        setAllTags(tags);

        // data for the detail view
        setDetailViewData(await getFormattedDetails(mission.id));

        // data for the information view (size)
        setTotalSize(await getTotalSize(mission.id));

        // data for the information view (duration)
        setTotalDuration(await getTotalDuration(mission.id));
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
  }, [id]);

  if (loading) return <Skeleton style={{ height: "30vh" }} />;
  if (error) return <p>Error: {error}</p>;
  if (!missionData) return <p>No data available</p>;

  return (
    <DetailsView
      missionData={missionData}
      detailViewData={detailViewData}
      totalSize={totalSize}
      totalDuration={totalDuration}
      allTags={allTags}
    ></DetailsView>
  );
}

const App = () => {
  return (
    <CreateAppShell>
      <Detail />
    </CreateAppShell>
  );
};

export default App;
