import classes from "./ErrorPage.module.css";
import { Button, Container, Group, Text, Title } from "@mantine/core";
import { Link } from "@remix-run/react";

interface ServerErrorProps {
  statusCode: string;
  errorMessage: string;
}

export function ServerError({ statusCode, errorMessage }: ServerErrorProps) {
  return (
    <Container className={classes.root}>
      <div className={classes.code}>{statusCode}</div>
      <Title className={classes.message}>{errorMessage}</Title>
      <Text c="dimmed" size="lg" ta="center" className={classes.description}>
        You might have entered the address
        incorrectly, or the page may have been moved to a different location.
      </Text>
      <Group justify="center">
        <Button
          variant="gradient"
          gradient={{ from: "yellow", to: "orange", deg: 269 }}
          size="md"
          component="a"
          href="/"
        >
          Take me to the main page
        </Button>
      </Group>
    </Container>
  );
}
