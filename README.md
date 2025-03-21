# Sophos Automatic Login & Authentication

## Introduction

This Python script automates the login process for an internet web authentication portal. It ensures uninterrupted connectivity by relogging you in every 2 minutes to prevent automatic logout. The updated version now uses an SQLite database to store login credentials, providing a more secure and scalable approach. Additionally, the script can automatically switch between multiple IDs when a data limit is reached or if one ID fails to log in.

## Features

- **SQLite Integration**: Credentials are securely stored in an SQLite database.
- **Automatic ID Switching**: Automatically switches to the next available ID if the current one fails or reaches its data limit.
- **Command-Line Arguments**: Supports various system arguments for automation and management.
- **Credential Management**: Add, edit, delete, import, and export credentials.
- **Interactive Menu**: User-friendly menu for managing credentials and starting the auto-login process.
- **CSV Import/Export**: Easily import/export credentials to/from a CSV file.
- **Auto-Logout Handling**: Ensures seamless reconnection by automatically logging in when disconnected.
- **Cross-Platform Compatibility**: Works on both Windows and Unix-based systems.
- **Daemon Mode**: Run the auto-login process in the background (Unix-like systems only).

## Prerequisites

Before running the program, ensure you have the following libraries installed:

- `requests`
- `lxml`
- `sqlite3` (built into Python)
- `colorama`

You can install the required libraries using pip:

```shell
pip install -r requirements.txt
```

## Usage

### Command-Line Arguments

The script supports the following command-line arguments:

- `--start`: Start the auto-login process immediately.
- `--add`: Add new credentials to the database.
- `--edit`: Edit existing credentials.
- `--delete`: Delete credentials from the database.
- `--export [path]`: Export credentials to a CSV file (optional path).
- `--import [path]`: Import credentials from a CSV file.
- `--show`: Display all stored credentials.
- `--daemon`: Run the auto-login process in background mode (must be used with `--start`).

Example:

```shell
python autologin_script.py --start
```

To run in daemon mode (background process):

```shell
python autologin_script.py --start --daemon
```

### Daemon Mode

The daemon mode allows you to run the auto-login process in the background without keeping a terminal window open. This feature is only available on Unix-like systems (Linux, macOS) and requires the `--start` flag.

When running in daemon mode:

- The process detaches from the terminal and runs in the background
- All output is redirected to a log file in `~/.sophos-autologin/sophos-autologin.log`
- A PID file is created at `~/.sophos-autologin/sophos-autologin.pid`

To stop the daemon process, you can use the following command to find and kill the process:

```shell
kill $(cat ~/.sophos-autologin/sophos-autologin.pid)
```

### Interactive Menu

If no arguments are provided, the script launches an interactive menu where you can:

1. Add new credentials.
2. Start the auto-login process.
3. Edit existing credentials.
4. Delete credentials.
5. Export credentials to a CSV file.
6. Import credentials from a CSV file.
7. View stored credentials.
8. Exit the program.

### Importing Previous CSV Files

If you have previously used the CSV-based version of this script, you can directly import your existing CSV files into the SQLite database using the `--import` argument or the interactive menu. This allows you to seamlessly migrate your credentials to the new database format.

Example:

```shell
python autologin_script.py --import credentials.csv
```

### Automatic ID Switching

The script automatically switches to the next available ID in the database if:

- The current ID reaches its data limit.
- The current ID fails to log in.

This ensures uninterrupted connectivity.

## Running the Program

To run the program, execute the Python script using your preferred Python interpreter:

```shell
python autologin_script.py
```

OR

```shell
python3 autologin_script.py
```

## Creating an Executable

To create an executable from the Python script, follow these steps:

1. Clone the repository and navigate to the project directory:

```shell
git clone https://github.com/tashifkhan/sophos-auto-login.git
cd sophos-auto-login
```

2. Install the required dependencies:

```shell
pip install -r requirements.txt
```

3. Install PyInstaller:

```shell
pip install pyinstaller
```

4. Create the executable:

```shell
pyinstaller --onefile --add-data "db/credentials.db:." autologin_script.py # MacOS / Linux
pyinstaller --onefile --add-data "db/credentials.db;." autologin_script.py # Windows
```

This will create an executable file in the `dist` directory:

```shell
./dist/autologin_script
```

## Additional Notes

- The SQLite database is automatically created and managed by the script.
- Ensure you have valid credentials stored in the database before starting the auto-login process.
- The script handles interruptions (e.g., Ctrl+C) gracefully and logs out active sessions before exiting.
- When running in daemon mode, check the log file for status updates and error messages.
