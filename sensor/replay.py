
import csv
import json
import os
import ssl
import time
import urllib.request
import urllib.error
import http.client
import urllib.parse
from pathlib import Path

DATA_FILE = Path("data/cleaned_sensor_data.csv")
CERT_FILE = Path("security/certs/server.crt")
API_URL = "https://smart-city-api:8000/readings"

API_KEY = os.environ["SENSOR_API_KEY"]

MAX_READINGS = 1000
INTERVAL_SECONDS = 0.1

ssl_context = ssl.create_default_context(
    cafile=str(CERT_FILE)
)

class LocalHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host, **kwargs):
        super().__init__(host, **kwargs)

    def connect(self):
        self.sock = self._context.wrap_socket(
            __import__("socket").create_connection(
                ("127.0.0.1", self.port),
                self.timeout
            ),
            server_hostname=self.host
        )


class LocalHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(
            LocalHTTPSConnection,
            req,
            context=ssl_context
        )


opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),
    LocalHTTPSHandler()
)

def main():
    successful = 0
    failed = 0

    with DATA_FILE.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if successful + failed >= MAX_READINGS:
                break

            reading = {
                "timestamp": row["timestamp"],
                "epoch": int(row["epoch"]),
                "sensor_id": int(row["sensor_id"]),
                "temperature": float(row["temperature"]),
                "humidity": float(row["humidity"]),
                "light": float(row["light"]),
                "voltage": float(row["voltage"]),
            }

            request = urllib.request.Request(
                API_URL,
                data=json.dumps(reading).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": API_KEY,
                },
                method="POST",
            )

            try:
                with opener.open(
                    request,
                    timeout=10,
                ) as response:
                    print(
                        f"HTTP {response.status} | "
                        f"Sensor {reading['sensor_id']}"
                    )
                    successful += 1

            except urllib.error.HTTPError as error:
                print(f"HTTP error: {error.code}")
                failed += 1

            except (urllib.error.URLError, TimeoutError) as error:
                print(f"Connection error: {error}")
                failed += 1

            time.sleep(INTERVAL_SECONDS)

    print("\nSecure replay completed!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
