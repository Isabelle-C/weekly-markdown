# weekly-markdown

Creates weekly markdown template! Might be a helpful template for fellow Obsidian users:)

TODO:
- [ ] More organized system of tags
  - [ ] Hidding tags

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
```
year
quarter
start_date
start_week_number
total_number_of_weeks
save_path
```

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
