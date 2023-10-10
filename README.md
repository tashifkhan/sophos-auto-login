# Sophos Automatic Login & Authentication

## Introdction

This is a Python Script that enables you to to login into your internet web authentication portal automatically. It relogs you in every 28 mins to mitigate the issue of auto logout after a certain time period

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

#### Option 01 

1. Open the Python file `version01.py` in a text editor.
2. Fill in your login credentials:
    - Update `username` and `password` with your primary login credentials.
    - Update `username1` and `password1` with your secondary login credentials.
3. Save the file.

**OR**

#### Option 02

1. Open the Python file `version02.py` in a text editor
2. Fill all your login credentials
	- Update the `credential` list
	- Update the dictionary in the list from the placeholders
	- Change `username1`, `password1`, etc with your credentials
	- If you have more Login ID's available append those to the list as dictionaries 
	- Similarly remove the unwanted amount of IDs
3. Save the file

## Running the Program

To run the program, simply execute the Python script using your preferred Python interpreter:

```shell
python version02.py
```

OR

```shell
python3 version02.py
```

## Creating an Executable

To create an executable from the Python script, you can use tools like PyInstaller. PyInstaller bundles the Python script and its dependencies into a standalone executable.

### Install PyInstaller

```shell
pip install pyinstaller
```

```shell
pyinstaller --onefile version02.py
```

This will create an executable file in the dist directory.

```shell
./dist/login_script
```

**Note:** Before creating the executable, make sure you have entered your correct login credentials in the Python script.
