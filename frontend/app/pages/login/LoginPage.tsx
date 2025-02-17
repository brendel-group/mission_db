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
import { useState } from "react";

export function LoginView({ error }: { error?: string }) {

  const [buttonClickable, setButtonClickable] = useState(true); // State to control button clickability
  const [buttonText, setButtonText] = useState("Log in"); // State to control button text
  const [dots, setDots] = useState(0); // State to control the number of dots
  const numberOfDots = 3; // Number of dots to be shown

  const handleSubmit = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault(); // Prevent the form from submitting immediately
    setButtonClickable(false); // Disable the button to prevent multiple submissions
    document.querySelector('.mantine-Alert-root')?.remove(); // Remove any existing alerts
    setButtonText("Logging in"); // Change the button text to "Logging in"

    const button = e.currentTarget; // Get the button that was clicked
    const form = button.closest('form');
    form?.submit(); // Submit the form

    const delay = 300; // Change the dots every 300ms

    const interval = setInterval(() => {
      setDots((dot) => (dot + 1) % (numberOfDots + 1)); // Animate the dots

      const isValid = form?.checkValidity();
      const alert = document.querySelector('.mantine-Alert-root');
      
      if (!isValid || (alert !== null)) { // End if the form is invalid or an alert is shown
        clearInterval(interval); // Stop the animation
        setButtonText("Log in"); // Reset the button text
        setButtonClickable(true); // Enable the button
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
              disabled={!buttonClickable}
            >
              <span style={{ marginLeft: "1.3em" }}>{buttonText} </span>
              {/* Add space to center the text */}
              <span style={{ display: "inline-block", textAlign: "left", marginLeft: "0.3em", width: "1.3em" }}>
                {". ".repeat(dots)}
              </span>
              {/* Add space to separate the text from the dots */}
            </Button>
          </Paper>
        </div>
      </div>
    </Form>
  );
}
