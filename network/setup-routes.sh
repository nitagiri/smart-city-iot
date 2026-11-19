
#!/bin/sh
set -eu

echo "Configuring Smart City IoT network routes..."

# Sensors -> API and Spark
docker compose exec -T sensor-test \
  ip route replace 10.10.2.0/24 via 10.10.1.254

docker compose exec -T sensor-test \
  ip route replace 10.10.3.0/24 via 10.10.1.254

# API -> Sensors and Spark
docker compose exec -T api-test \
  ip route replace 10.10.1.0/24 via 10.10.2.254

docker compose exec -T api-test \
  ip route replace 10.10.3.0/24 via 10.10.2.254

# Spark -> Sensors and API
docker compose exec -T spark-test \
  ip route replace 10.10.1.0/24 via 10.10.3.254

docker compose exec -T spark-test \
  ip route replace 10.10.2.0/24 via 10.10.3.254

echo "All network routes configured successfully."
