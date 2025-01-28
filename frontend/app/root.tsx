import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";

import { MantineProvider, ColorSchemeScript } from "@mantine/core";
import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useRouteError,
} from "@remix-run/react";
import { ServerError } from "./pages/error/ErrorPage";
import { Notifications } from "@mantine/notifications";

export function ErrorBoundary() {
  const error = useRouteError();

  const statusCode = isRouteErrorResponse(error)
    ? `${error.status}`
    : "Unknown";
  const errorMessage = isRouteErrorResponse(error)
    ? error.statusText
    : error instanceof Error
    ? error.message
    : "Unknown Error";

  return <ServerError statusCode={statusCode} errorMessage={errorMessage} />;
}

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
        <ColorSchemeScript />
        <link rel="icon" href="/favicon.ico" type="image/x-icon" />
      </head>
      <body>
        <MantineProvider>
          <Notifications />
          {children}
        </MantineProvider>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}
