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

When the output is too wide or long for the terminal and is a table, a pager will be used to display the table.\
The pager can be set usin the  `PAGER` or `MANPAGER` environmental variables.\
On Debian systems the default pager is `less` in most cases. With `less` the option `-S` can be used to disable folding of long lines to correctly display the table.

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
- `id` delete mission using the id

Example:
```
./cli.py mission remove 1
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
- `id` Mission id

Example:
```bash
./cli.py mission tag list 1
```

### `cli.py mission tag add`
Add Tag to Mission.\
A Tag can be added using the id or the name.\
If the name is used and there is no Tag with that name a new Tag is created.

Arguments:
- `--id` Mission id
- `--tag-id` (optional) Tag id
- `--tag-name` (optional) Tag name

`--tag-id` and `--tag-name` are mutually exclusive, so at least one is required but both are not allowed.

Example:
```bash
./cli.py mission tag add --id 1 --name "TestTag"
```

### `cli.py mission tag remove`
Remove Tag from Mission.\
A Tag can be removed using the id or the name.

Arguments:
- `--id` Mission id
- `--tag-id` (optional) Tag id
- `--tag-name` (optional) Tag name

`--tag-id` and `--tag-name` are mutually exclusive, so at least one is required but both are not allowed.

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

### `cli.py deletefolder`
delets a folder from the database

Arguments:
- `--path` path to mission folder of format `YYYY.MM.DD_mission_name` without trailing /

### `cli.py sync`
adds all missions from a folder not currently in the database and deletes all missions from the database that are not in the folder\
The folder that is searched for mission folders is the root of the Default Storage as configured in [settings.py](../../backend/backend/settings.py)

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

`--id` and `--name` are mutually exclusive, so at least one is required but both are not allowed.

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

`--id` and `--name` are mutually exclusive, so at least one is required but both are not allowed.

Example:
```bash
./cli.py tag mission list --id 1
```

### `cli.py user`
Make changes to Users

### `cli.py user add`
Add a user

Arguments:
- `--name` username of new user
- `--email` (optional) email-address of new user

The password can not be given as an argument and must be entered interactively after the command.\
For rules for a password refer to the [password policies](../password_policy/README.md)

Example:
```bash
./cli.py user add --name test
```
will then ask for a password:
```bash
Password: 
```
and to verify the password:
```bash
Verify Password: 
```

### `cli.py user remove`
Delete/remove a User.

Arguments:
- `--name` username of user to remove

### `cli.py user change-password`
Change the password of a User. Doesn't ask for the old password, just the new password.

Arguments:
- `--name` username of User which wants to change the password

The password rules can be found [here](../password_policy/README.md)

### `cli.py user list`
Show all users.\
Lists the Users with the data stored in the database.\
The password is not stored in clear-text but as a hash value.

## Troubleshooting

- ### `Error adding mission: duplicate key value violates unique constraint "restapi_mission_pkey"`
  If you encounter this issue it is likely you have old missions in your database that where added before
  the id field was changed to an `AutoField`, so postgresql didn't track the id's and can't assign new id's correctly.\
  To remove everything from the database and reset the `..._id_seq` tables you can run
  ```bash
  ./manage.py flush
  ```

## Notes for Developers:

All commands are implemented in the folder cli_commands.\
To add a new command import the abstract class `Command` from `Command.py`
and make a new class that inherits from this abstract class and implements all abstract methods and properties.

All .py files in the cli_commands folder are imported by cli.py except files that start with `test` and the file `__init__.py`\
Like this all classes inheriting from the `Command` class are found and added as a command and no changes of cli.py are required to add a new command.

There is one abstract property: `name`

And 2 abstract methods: 
- `parser_setup(self, subparser: argparse._SubParsersAction)`
- `command(self, args: argparse.Namespace)`

For information on what they do check `backend/cli_commands/Command.py`

Example implementation:
```python
from .Command import Command

class Example(Command):

  name = "example"

  def parser_setup(self, subparser):
    self.parser = subparser.add_parser(self.name,help="example")
    # add more arguments

  def command(self, args):
    pass # (remove this)
    # do something
```