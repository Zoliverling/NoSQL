# Real-time Chatbot with Redis

## Introduction

This is a simple real-time chatbot application built using Python and Redis. THe chabot allows users to identify themselves, siwtch between different user identities, join/leave channels, send/read message to channels. It also provides a set of fun commands such as retrieve the weather information and some fun facts.

## Features

**Identify Users**: Users can identify themselves with their name, age, gender, and location.

**Switch Users**: Easily switch between differnt users identificaitons.

**Channel Communication**: Users can join channels, send messages, and read messages from the channels they are subscribed to.

**Chat History**: The bot stores chat history for each user and allows you to retrieve it later.

**Special Commands**: Provides weather updates for cities, random facts, and user info retrieval.

## Technology Used

To run the project, you need to have:
    *Python* 3.x installed
    *Redis* server installed and running locally or accessible remotely
    *Docker* installed and running locally

## Installation

1. Clone the repository
```sh
git clone https://github.com/your-username/realtime-chatbot.git
```

2. Modify the volume in .yml file to match your local file path.
```sh
:/usr/ds5760
```

3. Ensure you Docker is running locally. Using Docker-compose up to mont the required python and redis packages.
```sh
docker-compose up
```

4. Open a new tab, run following command to access to redis-cli and monitor the activies while chatting.
```sh
docker exec -it {your redis name in .yml file} redis-cli
monitor
```

5. Open a new tab, run following command to access to python and run the .py file.
```sh
docker exec -it {your python name in .yml file} bash
python chatbot.py
```
