import { MetaFunction, useSearchParams } from "@remix-run/react";
import { useEffect, useState } from "react";
import DetailView from "~/pages/detail/DetailView";
import { fetchAndTransformMission } from "~/utilities/fetchapi";

export const meta: MetaFunction = () => {
  return [{ title: "Details" }];
};

function Details() {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");

  if (!id) return <h1>Invalid URL</h1>;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [missionData, setMissionData] = useState<any | null>(null);

  useEffect(() => {
    const fetchMission = async () => {
      try {
        const data = await fetchAndTransformMission(Number(id));
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

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!missionData) return <p>No data available</p>;

  return <DetailView missionData={missionData}></DetailView>;
}

const App = () => {
  return <Details />;
};

export default App;