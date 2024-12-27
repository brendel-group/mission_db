import { ReactNode } from "react";
import { AppShell, Burger, Group } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Navbar } from "~/layout/NavBar/NavBar";
import { Link } from "@remix-run/react";

interface BasicAppShellProps {
  children: ReactNode;
}

export function CreateAppShell({ children }: BasicAppShellProps) {
  const [opened, { toggle }] = useDisclosure();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 70, breakpoint: "sm", collapsed: { mobile: !opened } }}
      padding="xs"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <Link to="/" style={{ display: "flex", alignItems: "center" }}>
            <img
              src="/favicon.ico"
              alt="Custom Icon"
              style={{ width: 30, height: 30 }}
            />
          </Link>
          <span style={{ fontSize: "1.5rem" }}>Mission Explorer</span>
        </Group>
      </AppShell.Header>
      <AppShell.Navbar>
        <Navbar />
      </AppShell.Navbar>
      <AppShell.Main>
        <div style={{ paddingRight: "20px", paddingLeft: "20px" }}>
          {children}
        </div>
      </AppShell.Main>
    </AppShell>
  );
}
