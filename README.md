# Real-time Chatbot with Redis

## Introduction

This is a simple real-time chatbot application built using Python and Redis. THe chabot allows users to identify themselves, siwtch between different user identities, join/leave channels, send/read message to channels. It also provides a set of fun commands such as retrieve the weather information and some fun facts.

## Features

Identify Users: Users can identify themselves with their name, age, gender, and location.
Switch Users: Easily switch between differnt users identificaitons.
Channel Communication: Users can join channels, send messages, and read messages from the channels they are subscribed to.
Chat History: The bot stores chat history for each user and allows you to retrieve it later.
Fun Commands: Provides weather updates for cities, random facts, and user info retrieval.

## Technology Used

To run the project, you need to have:
    Python 3.x installed
    Redis server installed and running locally or accessible remotely
    Docker containers installed and running locally

## Installation

1. Clone the repository

2. Modify the volume in .yml file to match your local file path.

3. Using Docker-compose up to mont the required python and redis packages.

4. Open a new tab, run docker exec -it {your redis name in .yml file} redis-cli;

5. Open a new tab, run docker exec -it {your python name in .yml file} bash;

6. Python mp1_template.py
