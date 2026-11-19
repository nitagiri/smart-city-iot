
#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

echo "Starting Smart City IoT network..."
docker compose up -d --build

echo "Waiting for containers..."
sleep 5

echo "Restoring network routes..."
./network/setup-routes.sh

echo "Configuring FastAPI return route..."

docker compose exec -T api ip route replace \
  10.10.1.0/24 via 10.10.2.254

echo "Configuring firewall..."
./network/setup-firewall.sh

echo "Testing allowed communication..."
docker compose exec -T sensor-test \
  ping -c 4 -W 2 10.10.2.10

docker compose exec -T api-test \
  ping -c 4 -W 2 10.10.3.10

echo "Testing blocked communication..."
if docker compose exec -T sensor-test \
  ping -c 2 -W 2 10.10.3.10; then
  echo "ERROR: Unauthorized Sensors-to-Spark traffic is allowed!"
  exit 1
else
  echo "PASS: Direct Sensors-to-Spark traffic is blocked."
fi

echo "Smart City IoT network is ready!"
