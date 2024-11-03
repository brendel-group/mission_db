import type { MetaFunction } from "@remix-run/node";
import { CreateAppShell } from "~/layout/AppShell";
import MissionsPage from "~/pages/MissionsPage";

export const meta: MetaFunction = () => {
  return [
    { title: "Mission overview" },
    { name: "description", content: "Mission overview" },
  ];
};

export default function Index() {
  return (
    <CreateAppShell>
      <div>
        <MissionsPage />
      </div>
    </CreateAppShell>
  );
}