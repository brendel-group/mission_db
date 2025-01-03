# Command-line Interface

When listing for example Missions the output is a table that uses unicode characters for nice formatting,\
but if your terminal doesn't support unicode you can disable this by setting the envirment variable `USE_UNICODE` to `False` in the .env file.\
The table will then be printed using ASCII characters.

## Interactive mode:
Executing `cli.py` without any arguments will start an interactive shell mode.\
Every argument is available as a command in the shell.\
It supports tab completion and history.
The history is stored in the file `.polybot_mission_db_cli.py_hist` in the home directory or if the home directory is not found it is stored in the current working directory!

To use tab completion start typing a command and hit tab to complete it or show available completions.\
Example: `mis` will be completed to `mission`.

To use the history you can navigate with the arrow up and down keys through your last typed commands and execute them when hitting enter.

Two commands are available in interactive mode that are not available as normal arguments: `exit` and `help`\
`exit` terminantes the shell.\
`help` shows the normal `--help` and adds the commands `exit` and `help` to it.

Example usage:
```bash
./cli.py
cli.py interactive mode
  type 'help' for help or 'exit' to exit
>>> mission add --name "Example for interactive shell" --date "2024-12-10" 
INFO:root:'Example for interactive shell' added.
>>> mission list
id │ name                          │ date       │ location │ notes
───┼───────────────────────────────┼────────────┼──────────┼──────
1  │ Example for interactive shell │ 2024-12-10 │ None     │ None 
>>> exit
```

It's possible to input multiple lines when using quotes.
Example:
```bash
./cli.py
cli.py interactive mode
  type 'help' for help or 'exit' to exit
>>> mission add --name "Multi
... line
... example" --date "2024-12-26"
INFO:root:'Multi
line
example' added.
>>> exit
```
Strings with linebreaks are also supported when listing something in a table.

## Argument mode:

Instead of using the interactive mode you can directly call the CLI with the arguments.

Use
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
- `--notes` (optional) additional information

Example:
```
./cli.py mission add --name "Missionname" --date "2024-11-29" --location "location" --notes "notes"
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
List all missions in a table\
Sorted ascending by id

Example:
```bash
./cli.py mission list
```
### `cli.py mission tag`
command to make changes to tags of one mission

### `cli.py mission tag list`
List all Tags of one Mission in a table\
Sorted ascending by id

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
- `--notes` (optional) additional information

### `cli.py syncfolder`
adds all missions from a folder not currently in the database

Arguments:
- `--path` path to mission folder containing the missionfolders 
- `--location` (optional) the location where the mission took place
- `--notes` (optional) additional information

Example:
```
./cli.py syncfolder --path "your/path/name" --location "location(optional)" --notes "notes(optional)"
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
remove a tag from the database\
Asks for verification if there are any Missions with this Tag and prints the number of Missions it is used in.

Arguments:
- `--id` remove tag by id
- `--name` remove tag by name

Either `--id` or `--name` must be given. If both are given the id will be used and the name is ignored. \

Example
```bash
./cli.py tag remove --name "Tag"
```

### `cli.py tag list`
list all tags\
Sorted ascending by id

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
The Tag can be selected by id or name.\
Sorted ascending by id

Arguments:
- `--id` (optional) Tag id
- `--name` (optional) Tag name

Example:
```bash
./cli.py tag mission list --id 1
```

### `cli.py api-key`
command to make changes to API KEYs

### `cli.py api-key add`
Create a new API KEY\
This is the only time the key itself is visible.

Argumemts:
- `--name` Name of the API KEY
- `--expiry-date` (optional) Expiration Date of the API KEY\
format: `YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]`

### `cli.py api-key remove`
Remove an API KEY\
The API KEY can be selected using the name or prefix.\
The prefix can be found when listing all keys.\
If the name is used and there are multiple keys with that name, all of them will be removed.

Arguments:
- `--name` (optional) Name of the API KEY
- `--prefix` (optional) Prefix of an API KEY

### `cli.py api-key list`
List all API KEYs\
This will not display the keys itself.\
It will display all information as stored in the database.\
The keys itself are stored as hash values.

## Troubleshooting

- ### `Error adding mission: duplicate key value violates unique constraint "restapi_mission_pkey"`
  If you encounter this issue it is likely you have old missions in your database that where added before
  the id field was changed to an `AutoField`, so postgresql didn't track the id's and can't assign new id's correctly.\
  To remove everything from the database and reset the `..._id_seq` tables you can run
  ```bash
  ./manage.py flush
  ```
