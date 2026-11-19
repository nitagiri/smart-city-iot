import sys
import ssl
import urllib.request

url = "https://127.0.0.1:8000/health"

try:
    context = ssl._create_unverified_context()

    with urllib.request.urlopen(
        url, context=context, timeout=5
    ) as response:
        if response.status == 200:
            print("API healthy")
            sys.exit(0)

except Exception as error:
    print(f"API unhealthy: {error}")

sys.exit(1)
