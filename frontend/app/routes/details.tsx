import { Skeleton } from "@mantine/core";
import { LoaderFunctionArgs } from "@remix-run/node";
import { MetaFunction, redirect, useLoaderData } from "@remix-run/react";
import { useEffect, useState } from "react";
import { DetailViewData, MissionData, RenderedMission, Tag } from "~/data";
import { getFormattedDetails } from "~/fetchapi/details";
import { getMission } from "~/fetchapi/missions";
import { getTagsByMission, getTags } from "~/fetchapi/tags";
import { CreateAppShell } from "~/layout/AppShell";
import DetailsView from "~/pages/details/DetailsView";
import {
  transformDurations,
  transformFilePaths,
  transformSizes,
} from "~/utilities/FormatHandler";
import { sessionStorage } from "~/utilities/LoginHandler";

export const meta: MetaFunction = () => {
  return [{ title: "Details" }];
};

export async function loader({ request }: LoaderFunctionArgs) {
  let session = await sessionStorage.getSession(request.headers.get("cookie"));
  let user = session.get("user");

  if (!user) throw redirect("/login");

  let url = new URL(request.url);
  const id = url.searchParams.get("id");

  if (!id) {
    throw new Response(null, { status: 400, statusText: "Invalid URL" });
  }

  const numberId = Number(id);
  if (Number.isNaN(numberId)) {
    throw new Response(null, { status: 400, statusText: "Invalid URL" });
  }

  return {
    numberId,
  };
}

function Detail() {
  const { numberId: missionId } = useLoaderData<typeof loader>();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Mission
  const [missionData, setMissionData] = useState<any | null>(null);

  // Tags
  const [tags, setTags] = useState<Tag[]>([]);
  const [allTags, setAllTags] = useState<any | null>(null);

  // Detail View data
  const [detailViewData, setDetailViewData] = useState<DetailViewData>();
  const [basePath, setBasePath] = useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Create three independent async tasks:
        const fetchMission = async () => {
          const mission: MissionData = await getMission(missionId);
          const transformedMission: RenderedMission = {
            id: mission.id,
            name: mission.name,
            location: mission.location,
            date: mission.date,
            notes: mission.notes,
            totalDuration: transformDurations([mission.total_duration])[0],
            totalSize: transformSizes([mission.total_size])[0],
            robots: [],
            tags: [],
          };
          setMissionData(transformedMission);
        };
  
        const fetchTags = async () => {
          const tags: Tag[] = await getTagsByMission(missionId);
          const allTags: Tag[] = await getTags();
          tags.sort((a, b) => a.name.localeCompare(b.name));
          setAllTags(allTags);
          setTags(tags);
        };
  
        const fetchDetailView = async () => {
          const detailViewData = await getFormattedDetails(missionId);
          const { commonPath, files } = transformFilePaths(detailViewData.files);
          detailViewData.files = files;
          setBasePath(commonPath);
          setDetailViewData(detailViewData);
        };
  
        // Run all three tasks concurrently:
        await Promise.all([
          fetchMission(),
          fetchTags(),
          fetchDetailView(),
        ]);
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
  }, [missionId]);

  if (loading) return <Skeleton style={{ height: "30vh" }} />;
  if (error) return <p>Error: {error}</p>;
  if (!missionData) return <p>No data available</p>;

  return (
    <DetailsView
      missionData={missionData}
      detailViewData={detailViewData}
      tags={tags}
      allTags={allTags}
      basePath={basePath}
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
