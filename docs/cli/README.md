# Command-line Interface
## usage

```bash
cli.py --help
```
to display help information\
`--help` can be called on every command and subcommand

### `cli.py mission`

command to make changes to missions

### `cli.py mission add`
adds a new Mission to the Database

Arguments:
- `--name` mission name
- `--date` mission date in format YYYY-MM-DD
- `--location` (optional) the location where the mission took place
- `--other` (optional) additional information

Example:
```
./cli.py mission add --name "Missionname" --date "2024-11-29" --location "location" --other "other"
```
### `cli.py mission remove`
removes a Mission from the Database
#### Attention: doesn't ask for confirmation

Arguments:
- `--id` delete mission using the id

Example:
```
./cli.py mission remove --id 1
```

### `cli.py mission list`
List all missions in a table

Example:
```bash
./cli.py mission list
```

### `cli.py addfolder`
adds a mission using the filepath

Arguments:
- `--path` path to mission folder of format `YYYY.MM.DD_mission_name` without trailing /
- `--location` (optional) the location where the mission took place
- `--other` (optional) additional information

Example:
```
./cli.py addfolder --path "your/path/name_date" --location "location(optional)" --other "other(optional)"
```