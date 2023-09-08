# weekly-markdown

Creates weekly markdown template! Might be a helpful template for fellow Obsidian users:)

# How it works
For instance, for week 7 in summer quarter of 2023 which starts on Monday 7/24, we would produce markdown file `23-SM-07 (07-24).md` with the following headings:

```
# Mon 07-24

# Tue 07-25

# Wed 07-26

# Thu 07-27

# Fri 07-28

# Sat 07-29

# Sun 07-30
```

# Edit the config file
Step 1: In the config file, you can specify the following parameters:
```
year
quarter
start_date
start_week_number
total_number_of_weeks
save_path
action
```

Step 2: Depending what you would like to do the markdown file, you can specify the following actions:
- `create`: create new markdown files
- `append`: append to an existing markdown files (TODO as of 9/8/2023)
- `archive`: move existing markdown files to a new folder outside of obsidian vault

Step 3: In the `/configs` folder, you need to specify some file paths.
- `create.yaml`: Enter `save_path` which is /path/to/save/all/your/markdown/files
- `append.yaml`: Enter `append_path` which is /path/to/all/your/markdown/files
- `archive.yaml`: Enter 
    - `original_path` which is /current/path/to/all/your/markdown/files
    - `new_path` which is /path/to/move/all/your/markdown/files

# To run the code
1. Clone the repo and open the repo folder in terminal.

2. Activate the environment.

```bash
$ poetry shell
```

3. Install dependencies.

```bash
$ poetry install
```
4. Run main.py
```
python ./main.py
```
