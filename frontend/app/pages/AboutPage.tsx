import { Grid, Card, Avatar, Title, Text, Anchor, Group } from '@mantine/core';
import { IconBrandGithub } from '@tabler/icons-react';
import AbstractPage from "./AbstractPage";

const developers = [
  { name: 'Felix Mycka', github: 'https://github.com/sh1negg' },
  { name: 'Oliver Heckel', github: 'https://github.com/KageKrito' },
  { name: 'Pascal Kuppler', github: 'https://github.com/pascal260303' },
  { name: 'Samuel Hempelmann', github: 'https://github.com/SamuABC' },
  { name: 'Simon Rappenecker', github: 'https://github.com/DerSimi' },
  { name: 'Simon Rappold', github: 'https://github.com/s-rappold' },
];

export default function AboutPage() {
  return (
    <AbstractPage headline="About">
      <Text size="lg" mb="xl" mx="auto" maw={800}>
        Our Mission Explorer website was built as part of a team project course at the University of Tübingen during the winter term of 2024/25.
        Below you'll find profiles of the six developers who contributed to this project.
      </Text>

      <Grid gutter="xl" justify="center">
        {developers.map((dev) => {
          const username = dev.github.split('/').filter(part => part !== '').pop();
          
          return (
            <Grid.Col key={dev.name} span={{ xs: 12, sm: 6, md: 4 }}>
              <Card withBorder p="xl" radius="md" h="100%">
                <Group justify="center" gap="xs" style={{ flexDirection: 'column' }}>
                  <Avatar 
                    size={120}
                    radius={60}
                    src={`https://unavatar.io/github/${username}`}
                    alt={dev.name}
                    mb="sm"
                  />
                  
                  <Title order={3} ta="center">
                    {dev.name}
                  </Title>

                  <Anchor 
                    href={dev.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    inline
                  >
                    <Group gap={4}>
                      <IconBrandGithub size={18} />
                      <Text>GitHub Profile</Text>
                    </Group>
                  </Anchor>
                </Group>
              </Card>
            </Grid.Col>
          );
        })}
      </Grid>
    </AbstractPage>
  );
}