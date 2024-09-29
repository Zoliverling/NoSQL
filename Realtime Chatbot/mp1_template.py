import redis
import json
import random

class Chatbot:
    def __init__(self, host='redis', port=6379):
        self.client = redis.StrictRedis(host=host, port=port)
        self.pubsub = self.client.pubsub()
        self.username = None

    def introduce(self):
        # Provide an introduction and list of commands
        intro = """
        Welcome to Chatbot!
        !help: List of commands
        !weather <city>: Weather update
        !fact: Random fun fact
        !whoami: Your user information
        """
        print(intro)

    def identify(self, username, age, gender, location):
        user_key = f"user:{username}"
        self.client.hset(user_key, mapping={
            "username": username,
            "age": age,
            "gender": gender,
            "location": location
        })
        self.username = username

    def join_channel(self, channel):
        # Join a channel
        self.pubsub.subscribe(channel)
        print(f"Subscribed to channel: {channel}")
        

    def leave_channel(self, channel):
        # Leave a channel
        self.pubsub.unsubscribe(channel)
        print(f"Unsubscribed from channel: {channel}") 
        

    def send_message(self, channel, message):
        # Send a message to a channel
        print(f"Sending message to channel: {channel} ...")
        message_obj = {
            "from": self.username,
            "message": message
        }
        self.client.publish(channel, json.dumps(message_obj))

    def read_message(self, channel):
        # Read messages from a channel
        print(f"Reading messages from channel: {channel} ...")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                msg_data = json.loads(message['data'])
                print(f"[{channel}] {msg_data['from']}: {msg_data['message']}")
    
    def help(self):
        self.introduce()

    def weather(self, city):
        weather_data = self.client.get(f"weather:{city}")
        if weather_data:
            print(f"Weather in {city}: {weather_data}")
        else:
            print(f"No weather data available for {city}")

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


    def direct_message(self, message):
        # Send a direct message to the chatbot
        if not self.username: # If the username does not exist, return a message
            print("You are not identified yet.")
            return
        
        message_obj = {
            "from": self.username,
            "message": message
        }

        self.client.publish("chatbot", json.dumps(message_obj)) # Publish the message to the chatbot
        print("Message sent to chatbot!")

if __name__ == "__main__":
    bot = Chatbot()
    bot.introduce()
    # Main interaction loop here

    while True:
        print("\nOptions:")
        print("1. Identify yourself")
        print("2. Join a channel")
        print("3. Leave a channel")
        print("4. Send a message to a channel")
        print("5. Send a direct message to the chatbot")
        print("6. Special commands")
        print("7. Exit")

        choice = input("Enter the option number you want: ")

        if choice == "1":
            username = input("Enter your username: ")
            age = input("Enter your age: ")
            gender = input("Enter your gender: ")
            location = input("Enter your location: ")
            bot.identify(username, age, gender, location)
        elif choice == "2":
            channel = input("Enter the channel name you want to join: ")
            bot.join_channel(channel)
        elif choice == "3":
            channel = input("Enter the channel name you want to leave: ")
            bot.leave_channel(channel)
        elif choice == "4":
            channel = input("Enter the channel name you want to send a message to: ")
            message = input("Enter your message: ")
            bot.send_message(channel, message)
        elif choice == "5":
            message = input("Enter your message to the chatbot: ")
            bot.direct_message(message)
        elif choice == "6":
            message = input("Enter your special command: ")
            bot.process_commands(message)
        elif choice == "7":
            break
        




    
