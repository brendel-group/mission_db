import {
  Alert,
  Button,
  Checkbox,
  Container,
  Paper,
  PasswordInput,
  TextInput,
  Title,
} from "@mantine/core";
import classes from "./LoginPage.module.css";
import { Form } from "@remix-run/react";
import { IconInfoCircle } from "@tabler/icons-react";

export function LoginView({ error }: { error?: string }) {
  return (
    <Form method="post">
      <Container size={420} my={40}>
        <Title ta="center" className={classes.title}>
          Login
        </Title>

        {error && (
          <Alert
            variant="light"
            mt="lg"
            color="red"
            title="Login error"
            icon={<IconInfoCircle />}
          >
            {error}
          </Alert>
        )}

        <Paper withBorder shadow="md" p={30} mt={30} radius="md">
          <TextInput
            name="username"
            label="Username"
            placeholder="robot enjoyer"
            required
          />
          <PasswordInput
            name="password"
            label="Password"
            placeholder="i like robots"
            required
            mt="md"
          />
          <Button type="submit" fullWidth mt="xl">
            Sign in
          </Button>
        </Paper>
      </Container>
    </Form>
  );
}
