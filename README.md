# Smart City IoT Monitoring System

This project monitors sensor data using Docker, FastAPI, MongoDB, Apache Spark, and Streamlit.

## Features

- Sensor data collection
- MongoDB database
- FastAPI backend
- Apache Spark data analysis
- Streamlit dashboard
- Docker networking
- HTTPS and API key security
- Container health monitoring

## Requirements

- Docker Desktop or Docker Engine
- Docker Compose
- Git
- OpenSSL
- Python 3

## How to Run

1. Clone the repository:

    git clone https://github.com/nitagiri/smart-city-iot.git
    cd smart-city-iot

2. Create your environment file:

    cp .env.example .env

Edit .env and replace the example password and API key with your own values.

3. Generate development certificates:

    ./security/generate-certs.sh

4. Start the containers:

    docker compose up -d --build

5. Open the applications:

- Streamlit: http://localhost:8501
- Spark: http://localhost:8080
- API health: https://localhost:8000/health

## Important

Do not upload your .env file or private keys to GitHub.

The HTTPS certificate is self-signed.

This project uses custom Docker networking. Additional routing setup may be required after starting the containers.

The setup should be tested on a fresh computer before being considered fully reproducible.

## Project Folders

- api - FastAPI backend
- dashboard - Streamlit dashboard
- sensor - Sensor scripts
- spark - Spark analysis
- network - Docker network configuration
- security - Certificate generation

## Author

Nita Giri
