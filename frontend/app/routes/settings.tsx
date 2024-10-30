import type { MetaFunction } from "@remix-run/node";
import { CreateAppShell } from "~/layout/AppShell";
import SettingsPage from "~/pages/SettingsPage";
export const meta: MetaFunction = () => {
  return [
    { title: "Missions" },
    { name: "description", content: "Mission overview" },
  ];
};

export default function Index() {
  return (
    <CreateAppShell>
      <div>
        <SettingsPage />
      </div>
    </CreateAppShell>
  );
}
