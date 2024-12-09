import type { MetaFunction } from "@remix-run/node";
import { LoginView } from "~/pages/login/LoginPage";

export const meta: MetaFunction = () => {
  return [{ title: "Login" }];
};

export default function Index() {
  return <LoginView></LoginView>;
}
