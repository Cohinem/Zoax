import socket
import time
import random
import subprocess
import json

# Settings
server = "irc.chat.twitch.tv"
port = 6667
nickname = "-"  
token = "oauth:--"   
channel = "#zoax697_"
streamer = channel[1:]  
#messages = ["1", "2", "3", "4"] 
messages = ["ioops7Hmmmmmmm", "zoax69Chips", "zoax69Hmmm"]

def is_stream_online(username):
    """Check if the streamer is online using streamlink."""
    try:
        result = subprocess.run(
            ["streamlink", f"https://twitch.tv/{username}", "--json"],
            capture_output=True,
            text=True
        )

        output = json.loads(result.stdout)

        return output.get("streams") is not None
    except (subprocess.SubprocessError, json.JSONDecodeError):
        return False

def send_message(irc_socket, message):
    irc_socket.sendall(f"PRIVMSG {channel} :{message}\r\n".encode("utf-8"))

def connect_to_irc():
    irc = socket.socket()
    irc.connect((server, port))

    # Authenticate
    irc.sendall(f"PASS {token}\r\n".encode("utf-8"))
    irc.sendall(f"NICK {nickname}\r\n".encode("utf-8"))
    irc.sendall(f"JOIN {channel}\r\n".encode("utf-8"))

    return irc

def main():
    irc = connect_to_irc()
    print(f"Connected to channel {channel}")

    last_online_check = 0
    check_interval = 60  # 
    last_message_time = 0
    message_interval = 300  # Sends message every 5 minutes
    try:
        while True:
            current_time = time.time()

            # checking stream
            if current_time - last_online_check >= check_interval:
                is_online = is_stream_online(streamer)
                last_online_check = current_time

                if is_online:
                    print(f"{streamer} is online")
                else:
                    print(f"{streamer} is offline")

            # If online and enough time has passed, send a message
            if is_online and current_time - last_message_time >= message_interval:
                random_message = random.choice(messages)
                send_message(irc, random_message)
                print(f"Sent: {random_message}")
                last_message_time = current_time

            # Keep connection
            try:
                irc.settimeout(1)
                response = irc.recv(2048).decode("utf-8")
                if response.startswith("PING"):
                    irc.sendall(f"PONG {response.split()[1]}\r\n".encode("utf-8"))
            except socket.timeout:
                pass
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
        irc.close()
    except Exception as e:
        print(f"Error occurred: {e}")
        irc.close()

if __name__ == "__main__":
    main()
