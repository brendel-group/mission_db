# Command-line Interface
## usage
### add
adds a new Mission to the Database

Example:
```
python cli.py add --id "missionid" --name "Missionname" --date "YYYY-MM-DD HH:MM:SS" --location "location" --other "other"
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
python cli.py addfolder --id "missionid" --path "C:/your/path/name_date" --location "location(optional)" --other "other(optional)"
```