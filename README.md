# weekly-tasks

As of 12/27/2023, Documentation in process

## Introduction

This project is a web application designed to provide users with a relaxing and intuitive interface for managing their tasks. It is built with HTML, CSS, and JavaScript.

## Getting Started

### Prerequisites

To run this project, you will need:

- A modern web browser (like Chrome, Firefox, Safari, or Edge)
- A text editor to modify the code (like Visual Studio Code)

### Installation

1. Clone the repository to your local machine.
2. 
```bash
poetry shell
```
3. 
```bash
python app.py
```


## Usage

To use this application, simply enter your tasks in the input field and click the "Add" button. Your tasks will be displayed in a table below. You can delete tasks by clicking the "Delete" button next to each task.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## Testing

This project does not currently have any automated tests. Contributions to add testing are welcome.

## Deployment

To deploy this project, simply upload the files to your web server. Make sure to maintain the directory structure.

## Notes
To create new database, consider using sqlite3 python package. Alternatively, use IDEs like SQLiteStudio.

1. Activate sqlite3 env and create the databse file.
```bash
sqlite3 db_name.db
```

2. Write the SQL query.
```bash
CREATE TABLE todo (
    id INTEGER PRIMARY KEY,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    task_name TEXT NOT NULL,
    tag TEXT,
    due_date DATETIME,
    priority INTEGER,
    done BOOLEAN DEFAULT 0,
    done_timestamp DATETIME,
    frequency TEXT
);
```

```bash
CREATE TABLE lit(
    id INTEGER PRIMARY KEY,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    task_name TEXT NOT NULL,
    tag TEXT,
    original_pdf TEXT,
    notes TEXT
);
```

3. Quit.
```bash
.quit
```