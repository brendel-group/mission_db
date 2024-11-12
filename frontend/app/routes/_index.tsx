import type { MetaFunction } from "@remix-run/node";
import { CreateAppShell } from "~/layout/AppShell";
import MissionsPage from "~/pages/missions/MissionsPage";

export const meta: MetaFunction = () => {
  return [{ title: "Missions" }];
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
