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
      <div
        style={{
          backgroundImage: "url('/background.png')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          height: "100vh",
          width: "100vw",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            maxWidth: "420px", // Set a max width to prevent squashing
            width: "100%", // Ensure it remains responsive
            padding: "20px", // Add padding to prevent edges from cutting off
            boxSizing: "border-box", // Ensure padding doesn't affect size
          }}
        >
          <Paper withBorder shadow="md" p={30} radius="md">
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
            <Button
              type="submit"
              fullWidth
              mt="xl"
              variant="gradient"
              gradient={{ from: "yellow", to: "orange", deg: 269 }}
            >
              Sign in
            </Button>
          </Paper>
        </div>
      </div>
    </Form>
  );
}
