import socket
import sys
from time import time
from packet import *  # Importing necessary modules

def tcp(serverAddress: str, serverPort: int, fileNames: list):
    timestampListSmall = []  # List to store timestamps for small files
    timestampListLarge = []  # List to store timestamps for large files
    
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocketTCP:
        # Connect to the server
        clientSocketTCP.connect((serverAddress, serverPort))
        
        # Iterate through the list of file names
        for name in fileNames:
            file = b""  # Variable to store file content
            fileName = name
            timestamp = [0, 0]  # List to store timestamps
            clientSocketTCP.send(name.encode())  # Send the file name to the server
            timestamp[0] = time()  # Record the start time
            
            # Receive file data in chunks until the end marker is received
            while True:
                data = clientSocketTCP.recv(2048)
                file += data
                if file.endswith(b"\n"):
                    timestamp[1] = time()  # Record the end time
                    break

            # Write the received file content to a local file
            open(fileName, "wb").write(file)
            
            # Update timestamp lists based on file type
            if fileName.startswith("small"):
                timestampListSmall.append((timestamp[1] - timestamp[0]) * 1000)
            if fileName.startswith("large"):
                timestampListLarge.append((timestamp[1] - timestamp[0]) * 1000)
            
        print(timestampListSmall)
        print(timestampListLarge)

def main():
    # Get Server Address
    serverAddress = sys.argv[1]
    
    # Get Server Port Number
    serverPortTCP = int(sys.argv[2])
    
    fileNames = []
    
    # Generate file names for both small and large files
    for i in range(0, 10):
        fileNames.append("large-" + str(i) + ".obj")
        fileNames.append("small-" + str(i) + ".obj")
    
    with open('output_tcp.txt', 'a') as output:
        # Redirect stdout to the file
        sys.stdout = output
        
        # Run the TCP function to send files to the server and measure timestamps
        tcp(serverAddress, serverPortTCP, fileNames)

if __name__ == "__main__":
    main()
    # Example usage: python3 tcp_client.py 192.168.56.1 50
    # The script connects to a server at the specified address and port, sends files, and measures transfer times
