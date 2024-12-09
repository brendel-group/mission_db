import {
  Button,
  Checkbox,
  Container,
  Paper,
  PasswordInput,
  TextInput,
  Title,
} from "@mantine/core";
import classes from "./LoginPage.module.css";

export function LoginView() {
  return (
    <Container size={420} my={40}>
      <Title ta="center" className={classes.title}>
        Login
      </Title>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <TextInput label="Username" placeholder="robot enjoyer" required />
        <PasswordInput
          label="Password"
          placeholder="i like robots"
          required
          mt="md"
        />
        <Checkbox label="Remember me" mt="lg" />
        <Button fullWidth mt="xl">
          Sign in
        </Button>
      </Paper>
    </Container>
  );
}
