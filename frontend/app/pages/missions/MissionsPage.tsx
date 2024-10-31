import AbstractPage from "../AbstractPage";
import { Overview } from "./Overview";

export default function MissionsPage() {
  return (
    <AbstractPage headline="Missions">
      <div>
        <Overview />
      </div>
    </AbstractPage>
  );
}
