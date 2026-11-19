#!/bin/sh
set -eu

mkdir -p security/certs

openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout security/certs/server.key \
  -out security/certs/server.crt \
  -days 365 \
  -subj "/CN=smart-city-api" \
  -addext "subjectAltName=DNS:smart-city-api,IP:10.10.2.2,IP:127.0.0.1"

chmod 600 security/certs/server.key

echo "Development HTTPS certificate generated."
