import { MetaFunction, useSearchParams } from "@remix-run/react";
import { useEffect, useState } from "react";
import { DatasetView } from "~/pages/dataset/DatasetView";
import { fetchAndTransformMission } from "~/utilities/fetchapi";

export const meta: MetaFunction = () => {
  return [{ title: "Dataset" }];
};

function Dataset() {
  const [searchParams] = useSearchParams();
  const fileName = searchParams.get("fileName");
  const duration = searchParams.get("duration");
  const size = searchParams.get("size");

  if (!fileName || !duration || !size) return <h1>Invalid URL</h1>;

  return <DatasetView file={fileName} duration={duration} size={size}></DatasetView>;
}

const App = () => {
  return <Dataset />;
};

export default App;
