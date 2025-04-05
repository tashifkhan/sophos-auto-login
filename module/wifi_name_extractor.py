import subprocess
import platform

def get_wifi_name():
    os_name = platform.system()  
    
    try:
        if os_name == "Windows":
            # Windows: Use 'netsh' command
            result = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"], encoding="utf-8"
            )
            for line in result.split("\n"):
                if "SSID" in line and "BSSID" not in line:
                    wifi_name = line.split(":")[1].strip()
                    return wifi_name

        elif os_name == "Darwin": 
            # macOS: Use 'airport' command
            result = subprocess.check_output(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                encoding="utf-8"
            )
            for line in result.split("\n"):
                if "SSID" in line:
                    wifi_name = line.split(":")[1].strip()
                    return wifi_name

        elif os_name == "Linux":
            # Linux: Use 'nmcli' command
            result = subprocess.check_output(
                ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], encoding="utf-8"
            )
            for line in result.split("\n"):
                if line.startswith("yes:"):
                    wifi_name = line.split(":")[1].strip()
                    return wifi_name

        else:
            print(f"Unsupported operating system: {os_name}")
            return None

    except FileNotFoundError:
        print(f"Required command not found for {os_name}.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error while fetching Wi-Fi name: {e}")
        return None


if __name__ == "__main__":
    print("Fetching Wi-Fi name...")
    wifi_name = get_wifi_name()
    if wifi_name:
        print(f"Connected Wi-Fi name: {wifi_name}")
    else:
        print("Not connected to any Wi-Fi network or unable to retrieve Wi-Fi name.")
