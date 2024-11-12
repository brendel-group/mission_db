# Command-line Interface
## usage
### add
adds a new Mission to the Database

Example:
```
python cli.py add --id "missionid" --name "Missionname" --datetime "YYYY-MM-DD HH:MM:SS" --location "location" --other "other"
```
### remove
removes a Mission from the Database

Example:
```
python cli.py remove --id id

```
### addfolder
adds a mission using the filepath

Example:
```
python cli.py addfolder --id "missionid" --path "C:/your/path" --location "loation(optional)" --other "other(optional)"
```