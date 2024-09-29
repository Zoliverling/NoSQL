import redis
import json
import random
import time

class Chatbot:
    def __init__(self, host='redis', port=6379):
        self.client = redis.StrictRedis(host=host, port=port)
        self.pubsub = self.client.pubsub()
        self.username = None
        self.subscribed_channels = []

    def introduce(self):
        # Provide an introduction and list of commands
        intro = """
        Welcome to Chatbot! This is a simple chatbot that can let you interact with it in real-time.
        Idntify yourself before you want to start sending messages to the chatbot or join a channel.
        If you want to modify the personal information, you can identify yourself again.
        You can interact with the chatbot using the following commands:
        !help: List of commands
        !weather <city>: Weather update
        !fact: Random fun fact
        !whoami: Your user information
        """
        print(intro)

    def identify(self, username, age, gender, location):
        # Identify the user with the provided information
        user_key = f"user:{username}"
        self.client.hset(user_key, mapping={
            "username": username,
            "age": age, 
            "gender": gender,
            "location": location
        })
        self.username = username

        self.client.sadd("identified_users", username) # Add the username to the set of identified users
        print("User identified successfully.")
    
    def get_identified_users(self):
        # Get the list of identified users
        identified_users = self.client.smembers("identified_users") # Get the set of identified users from Redis
        if identified_users: # If identified users are found, print the list of identified users
            print("Identified users:")
            for user in identified_users:
                print(user)
        else:
            print("No identified users found.")

    def switch_user(self, username):
        # Switch the user to the specified username
        user_key = f"user:{username}"
        user_info = self.client.hgetall(user_key) # Get the user information from Redis
        if not user_info: # If the user information is not found, return a message
            print(f"User {username} not found. Please identify yourself first.")
            return
        
        if self.username: # If the user is already identified, switch the user
            print(f"Switching from {self.username} to {username}.")
        else:
            print(f"Switching to {username}.")
        
        self.username = username # Set the username to the new username
        print(f"User switched to {username} successfully.")

    # Join and Leave Channel Operation
    def join_channel(self, channel):
        # If the channel is not already subscribed, subscribe to the channel
        if channel not in self.subscribed_channels:
            self.pubsub.subscribe(channel) # Subscribe to the channel
            self.subscribed_channels.append(channel) # Add the channel to the list of subscribed channels
            print(f"Subscribed to channel: {channel}")
        else: # If the channel is already subscribed, return a message
            print(f"Already subscribed to channel: {channel}")
        
    def leave_channel(self, channel):
        # If the channel is subscribed, unsubscribe from the channel
        if channel in self.subscribed_channels:
            self.pubsub.unsubscribe(channel) # Unsubscribe from the channel
            self.subscribed_channels.remove(channel) # Remove the channel from the list of subscribed channels
            print(f"Unsubscribed from channel: {channel}") 
        else: # If the channel is not subscribed, return a message
            print(f"Not subscribed to channel: {channel}")

    # Store and Get Chat History
    def store_chat_history(self, username, message):
        # Store the chat history for the specified user
        chat_key = f"chat_history:{username}"
        self.client.lpush(chat_key, message) # Store the message in the chat history list in Redis
        print("Chat history stored successfully.")
    
    def get_chat_history(self, username):
        # Get the chat history for the specified user
        chat_key = f"chat_history:{username}"
        chat_history = self.client.lrange(chat_key, 0, -1) # Get the chat history list from Redis
        if chat_history:
            print(f"Chat history for {username}:")
            for idx, message in enumerate(chat_history, 1):
                print(f"{idx}. {message}")
        else:
            print(f"No chat history found for {username}.")

    # Send and Read Message, Store the Chat History        
    def send_message(self, channel, message):
        # Send a message to a channel
        print(f"Sending message to channel: {channel} ...")
        message_obj = {
            "from": self.username,
            "message": message
        }
        self.client.publish(channel, json.dumps(message_obj)) # Publish the message to the channel using Redis

        self.store_chat_history(self.username, message) # Store the chat history for the user after sending the message in Redis

    def read_message(self, channel):
        # Read messages from a channel
        print(f"Reading messages from channel: {channel} ...")
        time_out = 30 # Set a timeout of 30 seconds
        start_time = time.time() 
        if channel not in self.subscribed_channels:
            print(f"Channel {channel} not subscribed. Please join the channel first.")
            return

        while True:
            message = self.pubsub.get_message()
            if message:
                if message['type'] == 'message':
                    msg_data = json.loads(message['data'])
                    channel = message['channel'].decode('utf-8')
                    print(f"[{channel}] {msg_data['from']}: {msg_data['message']}")
            
            if time.time() - start_time > time_out: #If there is no message for 30 seconds, break the loop
                break

            time.sleep(0.001) # Sleep for 1ms before checking for the next message

        return
    
    # Special Commands
    def help(self):
        self.introduce() # Display the list of commands

    def store_weather(self, city):
        # Store the weather data for the specified city in Redis
        weather_descriptions = ["Sunny", "Cloudy", "Rainy", "Stormy", "Snowy", "Windy", "Foggy"]
        description = random.choice(weather_descriptions)
        weather_info = {
        "temperature": random.randint(-10, 40),  # Temperature range between -10°C to 40°C
        "humidity": random.randint(30, 100),     # Humidity range between 30% and 100%
        "description": description               # Randomly selected weather description
        }
         
        self.client.set(f"weather:{city}", json.dumps(weather_info))  # Store the weather data in Redis 
        print(f"Weather information for {city} stored successfully.")

    def weather(self, city):
        # Get the weather data for the specified city from Redis
        weather_data = self.client.get(f"weather:{city}") 
        if weather_data:
            print(f"Weather in {city}: {weather_data}")
        
        else: # If the weather data is not found, store the weather data and get the weather information based on the given city
            self.store_weather(city)
            self.weather(city)

    def store_fun_fact(self, fact):
        # Store the fun fact in the Redis DB before sending it to the chatbot
        facts = [
            "The sky is blue.",
            "The earth is round.",
            "The sun rises in the east."
        ]
        for fact in facts:
            self.client.spush("facts", fact)
        print("Fun fact stored!")
    
    def get_fun_fact(self):
        # Get a random fun fact from the Redis DB
        fact = self.client.spop("facts")
        print(fact)

    def whoami(self):
        # Get user information based on the username
        if not self.username: #If username does not exist, return a message
            print("You are not identified yet.")
            return
        
        user_info = self.client.hgetall(f"user:{self.username}")
        if user_info: # If the user information is stored, return the user information
            print(user_info)
        else: # If the user information is not stored, return a message
            print("User information not found.")

    def process_commands(self, message):
        # Handle special chatbot commands
        parts = message.split() # Split the message into parts to check for commands

        if len(parts) == 0: # If the message is empty, return
            return
        
        command = parts[0]  

        if command == "!help":
            self.help()
        elif command == "!weather" and len(parts) > 1: # If the command is !weather and the city is provided
            self.weather(parts[1])
        elif command == "!fact":
            self.store_fun_fact()
            self.get_fun_fact()
        elif command == "!whoami":
            self.whoami()




if __name__ == "__main__":
    bot = Chatbot()
    bot.introduce()
    # Main interaction loop here

    while True:
        print("\nOptions:")
        print("1. Identify yourself")
        print("2. Switch user")
        print("3. Send a message to a channel")
        print("4. Read messages from subscribed channels")
        print("5. Join a channel")
        print("6. List subscribed channels")
        print("7. Leave a channel")
        print("8. Get the chat history for a user")
        print("9. Get the list of identified users")
        print("10. Special commands")
        print("11. Exit")


        choice = input("Enter the option number you want: ")

        if choice == "1":
            username = input("Enter your username: ")
            age = input("Enter your age: ")
            gender = input("Enter your gender: ")
            location = input("Enter your location: ")
            bot.identify(username, age, gender, location)
        elif choice == "2":
            username = input("Enter the username you want to switch to: ")
            bot.switch_user(username)
        elif choice == "3":
            channel = input("Enter the channel name you want to send a message to: ")
            message = input("Enter your message: ")
            bot.send_message(channel, message)
        elif choice == "4":
            channel = input("Enter the channel name you want to read messages from: ")
            bot.read_message(channel)
        elif choice == "5":
            channel = input("Enter the channel name you want to join: ")
            bot.join_channel(channel)
        elif choice == "6":
            print("Subscribed channels: ", ', '.join(bot.subscribed_channels))
        elif choice == "7":
            channel = input("Enter the channel name you want to leave: ")
            bot.leave_channel(channel)
        elif choice == "8":
            username = input("Enter the username to get the chat history: ")
            bot.get_chat_history(username)
        elif choice == "9":
            bot.get_identified_users()
        elif choice == "10":
            message = input("Enter your special command: ")
            bot.process_commands(message)
        elif choice == "11":
            break




    
