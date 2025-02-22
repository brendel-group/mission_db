import { useState } from "react";
import { Tooltip, UnstyledButton, Stack, rem } from "@mantine/core";
import { Link } from "react-router-dom";
import { IconHome2, IconLogout, IconInfoCircle } from "@tabler/icons-react";
import classes from "./NavBar.module.css";

interface NavbarLinkProps {
  icon: typeof IconHome2;
  label: string;
  active?: boolean;
  onClick?(): void;
  to: string;
}

function NavbarLink({
  icon: Icon,
  label,
  active,
  onClick,
  to,
}: NavbarLinkProps) {
  return (
    <Tooltip label={label} position="right" transitionProps={{ duration: 0 }}>
      <Link to={to} style={{ textDecoration: "none" }}>
        <UnstyledButton
          onClick={onClick}
          className={classes.link}
          data-active={active || undefined}
        >
          <Icon style={{ width: rem(20), height: rem(20) }} stroke={1.5} />
        </UnstyledButton>
      </Link>
    </Tooltip>
  );
}

const entries = [
  { icon: IconHome2, label: "Missions", to: "/"},
  { icon: IconInfoCircle, label: "About", to: "/about" },
];

export function Navbar() {
  const [active, setActive] = useState(2);

  return (
    <nav className={classes.navbar}>
      <div className={classes.navbarMain}>
        <Stack justify="center" gap={0}>
          {entries.map((entry, index) => (
            <NavbarLink
              {...entry}
              key={entry.label}
              active={index === active}
              onClick={() => setActive(index)}
            />
          ))}
        </Stack>
      </div>

      <Stack justify="center" gap={0}>
        <NavbarLink icon={IconLogout} label="Logout" to="/logout" />
      </Stack>
    </nav>
  );
}
