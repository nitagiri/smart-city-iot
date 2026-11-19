
#!/bin/sh
set -eu

echo "Configuring Smart City IoT firewall..."

# Create a dedicated chain for project forwarding rules.
docker compose exec -T router sh -c '
set -eu

iptables -N SMART_CITY_FORWARD 2>/dev/null || true
iptables -F SMART_CITY_FORWARD

# Allow replies to established connections.
iptables -A SMART_CITY_FORWARD \
  -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow sensor traffic to the API test container.
iptables -A SMART_CITY_FORWARD \
  -s 10.10.1.0/24 -d 10.10.2.10/32 -j ACCEPT

# Allow API traffic to the Spark test container.
iptables -A SMART_CITY_FORWARD \
  -s 10.10.2.0/24 -d 10.10.3.10/32 -j ACCEPT

# Block all other forwarded traffic.
iptables -A SMART_CITY_FORWARD docker compose exec -T router iptables -A SMART_CITY_FORWARD \
  -s 10.10.1.0/24 \
  -d 10.10.2.2 \
  -p tcp --dport 8000 \
  -j ACCEPT -j DROP

# Send forwarded traffic through our chain.
iptables -C FORWARD -j SMART_CITY_FORWARD 2>/dev/null ||
  iptables -I FORWARD 1 -j SMART_CITY_FORWARD
'

echo "Firewall rules configured successfully."
