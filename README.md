# Sophos Automatic Login & Authentication

## Introduction

This Python script automates the login process for an internet web authentication portal, relogging you in every 2 minutes to prevent automatic logout. The updated version now stores the login credentials in a CSV file, providing a more organized and scalable approach. But the legacy version with dicsionary implementation is also uploaded (as login-dict.py).

It is basically a _**Program to Login to a Server**_

## Prerequisites

Before running the program, ensure you have the following libraries installed:

- `requests`
- `lxml`

You can install them using pip:

```shell
pip install requests lxml
```

## Usage

1. Open the Python file (e.g., auto-login.py) in a text editor.

2. Create a CSV file (e.g., credentials.csv) with a header of "username" followed by "password" and fill in your login credentials.

3. Update the `file_path` variable in the Python script with the correct path to your CSV file.

4. Save the file.

## Running the Program

To run the program, simply execute the Python script using your preferred Python interpreter:

```shell
python auto-login.py
```

OR

```shell
python3 auto-login.py
```

## Creating an Executable

To create an executable from the Python script, you can use tools like PyInstaller. PyInstaller bundles the Python script and its dependencies into a standalone executable.

### Install PyInstaller

```shell
pip install pyinstaller
```

```shell
pyinstaller --onefile auto-login-csv.py
```

This will create an executable file in the dist directory.

```shell
./dist/auto-login-csv
```

**Note:** Before creating the executable, make sure you have entered your correct login credentials in the Python script.
