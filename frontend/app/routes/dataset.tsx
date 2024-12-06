import { MetaFunction, useSearchParams } from "@remix-run/react";
import { CreateAppShell } from "~/layout/AppShell";
import { DatasetView } from "~/pages/dataset/DatasetView";

export const meta: MetaFunction = () => {
  return [{ title: "Dataset" }];
};

function Dataset() {
  const [searchParams] = useSearchParams();
  const fileName = searchParams.get("fileName");
  const duration = searchParams.get("duration");
  const size = searchParams.get("size");

  if (!fileName || !duration || !size) return <h1>Invalid URL</h1>;

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
