import sys
import urllib.request
import socket

def check_internet_connection(method="http", timeout=3):
    """ Checks for internet connectivity using either HTTP requests or socket connection. """
    if method == "http":
        try:
            urls = [
                "https://www.google.com",
                "https://www.cloudflare.com"
            ]
            
            for url in urls:
                try:
                    urllib.request.urlopen(url, timeout=timeout)
                    return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            print(f"HTTP connection attempt failed: {e}", file=sys.stderr)
            return False
    else:
        try:
            socket.setdefaulttimeout(timeout)
            hosts = [
                ("8.8.8.8", 53),        # Google DNS
                ("1.1.1.1", 53),        # Cloudflare DNS
                ("208.67.222.222", 53)  # OpenDNS
            ]
            
            for host, port in hosts:
                try:
                    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
                    return True
                except socket.error:
                    continue
            
            return False
            
        except Exception as e:
            print(f"Socket connection attempt failed: {e}", file=sys.stderr)
            return False

if __name__ == "__main__":
    print("Checking internet connection...")
    
    # Try HTTP method first (more likely to work through proxies)
    print("Trying HTTP method...")
    if check_internet_connection(method="http"):
        print("Status: Connected (HTTP)")
    else:
        print("HTTP method failed. Trying socket method...")
        if check_internet_connection(method="socket"):
            print("Status: Connected (Socket)")
        else:
            print("Status: Not Connected")
