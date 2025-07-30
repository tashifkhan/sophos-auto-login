import subprocess
import platform
import os
import re


def get_wifi_name():
    os_name = platform.system()
    debug_mode = False  # Set to False by default now that we have it working

    def debug(msg):
        if debug_mode:
            print(f"DEBUG: {msg}")

    try:
        debug(f"Detected OS: {os_name}")

        if os_name == "Windows":
            result = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                encoding="utf-8",
            )
            for line in result.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":", 1)[1].strip()

        elif os_name == "Darwin":  # macOS
            debug("Using macOS detection methods")

            # Try modern methods first
            try:
                # Method 2: Check if WiFi is active using ifconfig
                debug("Checking if WiFi is active via ifconfig...")
                try:
                    cmd = "ifconfig en0 | grep status"
                    result = subprocess.check_output(
                        cmd, shell=True, encoding="utf-8"
                    ).strip()
                    if "active" in result:
                        debug("WiFi is active, trying advanced detection methods")

                        # Method 2.1: Try networksetup with special handling
                        try:
                            cmd = "networksetup -getairportnetwork en0"
                            result = subprocess.check_output(
                                cmd, shell=True, encoding="utf-8"
                            ).strip()
                            debug(f"networksetup output: {result}")

                            # Check for any network name in the output
                            if ":" in result and "not associated" not in result.lower():
                                ssid = result.split(":", 1)[1].strip()
                                if ssid:
                                    debug(f"Found network name: {ssid}")
                                    return ssid
                        except Exception as e:
                            debug(f"Advanced networksetup failed: {e}")

                        # WiFi is active but we can't get the name - return placeholder
                        # Use a constant string that indicates WiFi is active
                        # Your Sophos login script can check for this special value
                        debug("WiFi is active but name couldn't be determined")
                        return "ACTIVE_WIFI_CONNECTION"
                except Exception as e:
                    debug(f"WiFi active check failed: {e}")

                # Try other methods as fallbacks
                try:
                    airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport"
                    if os.path.exists(airport_path):
                        result = subprocess.check_output(
                            [airport_path, "-I"], encoding="utf-8"
                        )
                        debug(f"Airport command output: {result}")
                        for line in result.splitlines():
                            if " SSID:" in line:
                                ssid = line.split(":", 1)[1].strip()
                                debug(f"Found SSID via airport: {ssid}")
                                return ssid
                except Exception as e:
                    debug(f"Airport direct parsing failed: {e}")

                try:
                    result = subprocess.check_output(
                        ["system_profiler", "SPNetworkDataType"], encoding="utf-8"
                    )

                    wifi_section = False
                    for line in result.splitlines():
                        if "Wi-Fi" in line:
                            wifi_section = True
                        if wifi_section and "SSID:" in line:
                            ssid = line.split(":", 1)[1].strip()
                            debug(
                                f"Found SSID via system_profiler direct parsing: {ssid}"
                            )
                            return ssid
                except Exception as e:
                    debug(f"System_profiler direct parsing failed: {e}")

                try:
                    debug("Trying to find Wi-Fi interface...")
                    out = subprocess.check_output(
                        ["networksetup", "-listallhardwareports"],
                        encoding="utf-8",
                    )
                    iface = None
                    lines = out.splitlines()
                    for i, ln in enumerate(lines):
                        if "Wi-Fi" in ln or "AirPort" in ln:
                            for j in range(i + 1, min(i + 5, len(lines))):
                                if lines[j].startswith("Device:"):
                                    iface = lines[j].split(":", 1)[1].strip()
                                    debug(f"Found Wi-Fi interface: {iface}")
                                    break
                            if iface:
                                break

                    if not iface:
                        debug("No Wi-Fi interface found")

                    if iface:
                        debug(f"Trying networksetup with interface {iface}")
                        try:
                            net_out = subprocess.check_output(
                                ["networksetup", "-getairportnetwork", iface],
                                encoding="utf-8",
                            ).strip()
                            debug(f"networksetup output: {net_out}")

                            if "Current Wi-Fi Network:" in net_out:
                                ssid = net_out.split(":", 1)[1].strip()
                                debug(f"Found SSID via networksetup: {ssid}")
                                return ssid
                            if "not associated" in net_out.lower():
                                debug("Not associated with any network")
                                return None
                        except subprocess.CalledProcessError as e:
                            debug(f"networksetup error: {e}")
                except Exception as e:
                    debug(f"Error finding Wi-Fi interface: {e}")

            except Exception as e:
                debug(f"General error in macOS detection: {e}")

            debug("All macOS detection methods failed")
            return None

        elif os_name == "Linux":
            result = subprocess.check_output(
                ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
                encoding="utf-8",
            )
            for line in result.splitlines():
                if line.startswith("yes:"):
                    return line.split(":", 1)[1].strip()

        else:
            debug(f"Unsupported OS: {os_name}")
            print(f"Unsupported OS: {os_name}")
            return None

    except FileNotFoundError as e:
        debug(f"Command not found: {e}")
        print(f"Required command not found on {os_name}.")
        return None
    except subprocess.CalledProcessError as e:
        debug(f"Command error: {e}")
        print(f"Error fetching Wi‑Fi name: {e}")
        return None


if __name__ == "__main__":
    print("Fetching Wi‑Fi name…")

    if platform.system() == "Darwin":
        try:
            print("Trying advanced macOS methods to get the actual WiFi name...")

            # Try scutil approach - this sometimes works on newer macOS
            try:
                print("Method 1: Using scutil and preferences...")
                cmd = "scutil --dns | grep -i nameserver | head -n1"
                result = subprocess.check_output(
                    cmd, shell=True, encoding="utf-8"
                ).strip()
                print(f"DNS nameserver: {result}")

                # Try using the new NetworkManager framework approach
                print("Method 2: Using newer macOS APIs...")
                try:
                    # Check if WiFi is active first
                    cmd = "ifconfig en0 | grep status"
                    status = subprocess.check_output(
                        cmd, shell=True, encoding="utf-8"
                    ).strip()
                    print(f"WiFi interface status: {status}")

                    if "active" in status:
                        # Try plist from system configurations
                        print("Method 3: Checking configurations...")
                        try:
                            cmd = "defaults read /Library/Preferences/SystemConfiguration/preferences.plist | grep -A 20 'Wi-Fi'"
                            result = subprocess.check_output(
                                cmd, shell=True, encoding="utf-8"
                            ).strip()
                            print("Found WiFi config in preferences:")
                            print(result)
                        except Exception as e:
                            print(f"preferences.plist check failed: {e}")

                        # Manually run the airport command to see full output
                        try:
                            print("\nDirect airport command output (may have SSID):")
                            airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport"
                            if os.path.exists(airport_path):
                                result = subprocess.check_output(
                                    [airport_path, "-I"], encoding="utf-8"
                                )
                                print(result)
                        except Exception as e:
                            print(f"Direct airport command failed: {e}")

                        print(
                            "\nNOTE: If you're seeing 'You are not associated with an AirPort network' but WiFi is active,"
                        )
                        print(
                            "this is due to macOS privacy protections. You may need to:"
                        )
                        print(
                            "1. Add Terminal/Python to Full Disk Access in System Preferences > Privacy"
                        )
                        print("2. Run this script with sudo privileges")
                        print("3. Create an app with Automation permissions")
                except Exception as e:
                    print(f"WiFi active check failed: {e}")
            except Exception as e:
                print(f"scutil check failed: {e}")

            # Standard approach as fallback
            try:
                cmd = "ifconfig en0 | grep status"
                status = subprocess.check_output(
                    cmd, shell=True, encoding="utf-8"
                ).strip()
                print(f"WiFi interface status: {status}")

                if "active" in status:
                    try:
                        cmd = "networksetup -getairportnetwork en0"
                        result = subprocess.check_output(
                            cmd, shell=True, encoding="utf-8"
                        ).strip()
                        if ":" in result and "not associated" not in result.lower():
                            ssid = result.split(":", 1)[1].strip()
                            if ssid:
                                print(f"Connected SSID: {ssid}")
                                exit(0)
                    except Exception:
                        pass

                    print("WiFi is active, but SSID detection methods failed.")
                    print(
                        "This may be due to system privacy protections in newer macOS versions."
                    )
                    print("Using 'ACTIVE_WIFI_CONNECTION' as a placeholder.")
                    exit(0)
            except Exception as e:
                print(f"WiFi status check failed: {e}")

        except Exception as e:
            print(f"macOS detection error: {e}")

    ssid = get_wifi_name()
    if ssid == "ACTIVE_WIFI_CONNECTION":
        print("Connected to an active WiFi network (name unavailable)")
    elif ssid:
        print(f"Connected SSID: {ssid}")
    else:
        print("Not connected or unable to retrieve SSID.")
