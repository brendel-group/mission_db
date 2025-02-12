import {
  Alert,
  Button,
  Paper,
  PasswordInput,
  TextInput,
  Title,
} from "@mantine/core";
import classes from "./LoginPage.module.css";
import { Form } from "@remix-run/react";
import { IconInfoCircle } from "@tabler/icons-react";

export function LoginView({ error }: { error?: string }) {

  const handleSubmit = (e: React.MouseEvent<HTMLButtonElement>) => {
    const button = e.currentTarget;
    button.innerHTML = 'Logging in&nbsp;.&nbsp;.&nbsp;.'; // Set the button text to "Logging in . . ." to indicate loading

    const delay = 300; // Change the dots every 300ms
    const numberOfDots = 3; // Number of dots to be shown
    let dots = 0;
    let spaces = numberOfDots;

    const interval = setInterval(() => {
      dots = (dots + 1) % (numberOfDots + 1);
      spaces = numberOfDots - dots;
      button.innerHTML = `Logging in${'&nbsp;.'.repeat(dots)}${'&nbsp;&nbsp;'.repeat(spaces)}`; // Animate the dots

      const isValid = button.closest('form')?.checkValidity();
      const alert = document.querySelector('.mantine-Alert-root');
      
      if (!isValid || (alert !== null) || error) { // End if the form is invalid or an alert or error is shown
        clearInterval(interval); // Stop the animation
        button.innerText = 'Log in'; // Reset the button text
      }

    }, delay);
  };

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
              className={classes.login_button}
              onClick={handleSubmit}
            >
              Log in
            </Button>
          </Paper>
        </div>
      </div>
    </Form>
  );
}
