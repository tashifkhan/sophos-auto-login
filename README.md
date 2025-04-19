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
- **Connection Check**: Periodically checks for internet connectivity and logs in if disconnected.
- **Scheduled Re-login**: Performs a scheduled re-login every 30 minutes to maintain connection.

## Usage

### Quick Start with Pre-built Executable

You can download the latest pre-built executable directly from the [Releases](https://github.com/tashifkhan/sophos-auto-login/releases) section without needing to install Python or any dependencies:

1. Go to the Releases section on GitHub
2. Download the executable for your operating system (Windows, macOS, or Linux)
3. Run the downloaded file:
   - **Windows**: Double-click the `autologin.exe` file
   - **macOS**:
     - Extract the downloaded autologin_script-mac.zip file
     - Option 1: Remove the quarantine attribute by opening Terminal, navigating to the extraction location, and running `xattr -d com.apple.quarantine autologin` before executing it
     - Option 2: Right-click on the extracted file, select "Open" from the context menu, then confirm the security dialog that appears. Alternatively, go to System Settings > Privacy & Security and click "Allow" for the blocked application
   - **Linux**:
     - Extract the downloaded autologin_script-linux.zip file
     - Open Terminal, navigate to the extraction location and run `./autologin_script`

The executable contains all necessary dependencies and doesn't require any additional installation steps.

### Command-Line Arguments

The script supports the following command-line arguments:

- `--start` or `-s`: Start the auto-login process immediately.
- `--add` or `-a`: Add new credentials to the database.
- `--edit` or `-e`: Edit existing credentials.
- `--delete` or `-del`: Delete credentials from the database.
- `--export [path]` or `-x [path]`: Export credentials to a CSV file (optional path). If no path is provided, it exports to a default `credentials.csv` file in the same directory as the database.
- `--import [path]` or `-i [path]`: Import credentials from a CSV file.
- `--show` or `-l`: Display all stored credentials.
- `--daemon` or `-d`: Run the auto-login process in background mode (must be used with `--start`).
- `--exit` or `-q`: Stop the daemon process and logout all credentials.
- `--logout` or `-lo`: Logout from all credentials without stopping the daemon process.
- `--speedtest` or `-t`: Run a speed test to measure your current internet connection performance.
- `--status` or `-st`: Display the current status of the daemon process.

Example:

```shell
python autologin.py --start
```

To run in daemon mode (background process):

```shell
python autologin.py --start --daemon
```

To stop the daemon process:

```shell
python autologin.py --exit
```

### Daemon Mode

The daemon mode allows you to run the auto-login process in the background without keeping a terminal window open. This feature is only available on Unix-like systems (Linux, macOS) and requires the `--start` flag.

When running in daemon mode:

- The process detaches from the terminal and runs in the background.
- All output is redirected to a log file in `~/.sophos-autologin/sophos-autologin.log`.
- A PID file is created at `~/.sophos-autologin/sophos-autologin.pid`.

To stop the daemon process, you can use the `--exit` or `-q` command-line argument:

```shell
python autologin.py --exit
```

Alternatively, you can use the following command to find and kill the process:

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
8. Run a speed test.
9. Logout from all credentials.
10. Check daemon status.
11. Exit the program.

### Importing Previous CSV Files

If you have previously used the CSV-based version of this script, you can directly import your existing CSV files into the SQLite database using the `--import` argument or the interactive menu. This allows you to seamlessly migrate your credentials to the new database format.

Example:

```shell
python autologin.py --import credentials.csv
```

### Automatic ID Switching

The script automatically switches to the next available ID in the database if:

- The current ID reaches its data limit.
- The current ID fails to log in.

This ensures uninterrupted connectivity.

### Internet Connection Check

The script periodically checks for internet connectivity every 90 seconds. If the internet connection is lost, the script will attempt to log in again using the stored credentials.

### Scheduled Re-login

To ensure continuous connectivity, the script performs a scheduled re-login every 30 minutes, even if the internet connection is active. This helps prevent unexpected disconnections due to session timeouts.

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

## Running the Program

To run the program, execute the Python script using your preferred Python interpreter:

```shell
python autologin.py
```

OR

```shell
python3 autologin.py
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
pyinstaller --onefile --add-data "db/credentials.db:." autologin.py # MacOS / Linux
pyinstaller --onefile --add-data "db/credentials.db;." autologin.py # Windows
```

This will create an executable file in the `dist` directory that you can run directly.

## Additional Notes

- The SQLite database is automatically created and managed by the script.
- Ensure you have valid credentials stored in the database before starting the auto-login process.
- The script handles interruptions (e.g., Ctrl+C) gracefully and logs out active sessions before exiting.
- When running in daemon mode, check the log file for status updates and error messages.
