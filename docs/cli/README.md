# Command-line Interface
## usage

```bash
./cli.py --help
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
### `cli.py mission tag`
command to make changes to tags of one mission

### `cli.py mission tag list`
List all Tags of one Mission in a table

Arguments:
- `--id` Mission id

Example:
```bash
./cli.py mission tag list --id 1
```

### `cli.py mission tag add`
Add Tag to Mission.\
A Tag can be added using the id or the name.\
If the name is used and there is no Tag with that name a new Tag is created.

Arguments:
- `--id` Mission id
- `--tag-id` (optional) Tag id
- `--tag-name` (optional) Tag name

Example:
```bash
./cli.py mission tag add --id 1 --name "TestTag"
```

### `cli.py mission tag remove`
Remove Tag from Mission.\
A Tag can be removed using the id or the name, but at least one of them must be used.

Arguments:
- `--id` Mission id
- `--tag-id` (optional) Tag id
- `--tag-name` (optional) Tag name

Example:
```bash
./cli.py mission tag remove --id 1 --name "TestTag"
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

### `cli.py tag`
command to make changes to tags

### `cli.py tag add`
adds a new tag to the database

Arguments:
- `--name` tag name
- `--color` (optional) tag color in hex format defaults to the default value of the ColorField

Example:
```bash
./cli.py tag add --name "Tag" --color "#FF0000"
```

### `cli.py tag remove`
remove a tag from the database

Arguments:
- `--id` remove tag by id
- `--name` remove tag by name

Either `--id` or `--name` must be given. If both are given the id will be used and the name is ignored. \
Doesn't ask for verification.

Example
```bash
./cli.py tag remove --name "Tag"
```

### `cli.py tag list`
list all tags

Example:
```bash
./cli.py tag list
```

### `cli.py tag change`
make changes to a tag

Arguments:
- `--id` select tag by id
- `--name` select tag by name or change name
- `--color` new color of the tag

Either `--id` or `--name` must be given. If both are given the id will be used to select the tag
and the name will be the new name of the tag.\
All arguments are optional, so you can change the name without changing the color and vice versa.

Example:
```bash
./cli.py tag change --id 1 --name "NewName" --color "#00FF00"
```

### `cli.py tag mission list`
List all missions with the same tag.\
The Tag can be selected by id or name.

Arguments:
- `--id` (optional) Tag id
- `--name` (optional) Tag name

Example:
```bash
./cli.py tag mission list --id 1
```

## Troubleshooting

- ### `Error adding mission: duplicate key value violates unique constraint "restapi_mission_pkey"`
  If you encounter this issue it is likely you have old missions in your database that where added before
  the id field was changed to an `AutoField`, so postgresql didn't track the id's and can't assign new id's correctly.\
  To remove everything from the database and reset the `..._id_seq` tables you can run
  ```bash
  ./manage.py flush
  ```