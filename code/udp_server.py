from random import randint
import socket
import sys
from packet import *

# Function to assist UDP server in handling file transfer with Selective Repeat mechanism
def udpHelper(serverSocket, clientAddress, fileNames: list, timeoutOptimal: float):
    # Loop through each file name to be sent to the client
    for fileName in fileNames:
        sequenceNumber = 0
        windowSize = 120    # Set window size for Selective Repeat
        baseNumber = 0      # Set base number for Selective Repeat
        print(fileName)
        
        # Create a packet object for the current file
        packet = Packet(fileName)
        
        # Split the packet into smaller packets and store them in a list
        packets = packet.splitPacket()  

        # Create a list to keep track of received ACKs for each packet
        sequenceNumberList = [False] * packet.packetNumber  

        # Loop until all packets are successfully sent and acknowledged
        while sequenceNumberList.count(True) != packet.packetNumber:
            serverSocket.settimeout(None)
            
            # Send all the packets within the window and check if they are ACKed
            while sequenceNumber < baseNumber + windowSize and sequenceNumber < packet.packetNumber:
                if not sequenceNumberList[sequenceNumber]:
                    # Encode the contents and send the packet
                    data = packet.encodeUDP(fileName, packets[sequenceNumber], sequenceNumber, packet.packetNumber)
                    serverSocket.sendto(data, clientAddress)
                sequenceNumber += 1

            # Set a timeout for acknowledgment reception
            serverSocket.settimeout(timeoutOptimal)
            
            while True:
                try:
                    # Start receiving ACKs
                    (receivedMessage, _) = serverSocket.recvfrom(2048)
                    receivedMessageDecoded = receivedMessage.decode()

                    # Process acknowledgment messages
                    if receivedMessageDecoded.startswith("ACK"):
                        if fileName[0] == receivedMessageDecoded[3]:
                            receivedSequenceNumber = int(receivedMessageDecoded[4:])
                            # Mark the received packet as ACKed
                            if not sequenceNumberList[receivedSequenceNumber]:
                                sequenceNumberList[receivedSequenceNumber] = True

                    # Move the base number to the next unacknowledged packet
                    while sequenceNumberList[baseNumber]:
                        baseNumber += 1
                        if baseNumber == packet.packetNumber:
                            break

                    # Break from the loop if all packets are acknowledged
                    if sequenceNumberList.count(True) == packet.packetNumber:
                        break

                except socket.timeout as t:
                    # If timeout occurs, set the current sequence number to the base number and resend unACKed packets
                    sequenceNumber = baseNumber
                    break

        # Set a timeout for the "exit" message
        serverSocket.settimeout(0.1)
        
        while True:
            # Send an exit message to the client to finish receiving the current object
            serverSocket.sendto("exit".encode(), clientAddress)
            try:
                (receivedMessage, _) = serverSocket.recvfrom(2048)
                if receivedMessage.decode() == "exit":
                    break

            except socket.timeout as t:
                # Break the loop if the last file is processed
                if fileName == fileNames[-1]:
                    serverSocket.sendto("exit".encode(), clientAddress)
                    break
                continue

# UDP server function
def udp(serverAddress: str, serverPort: int, timeoutOptimal: float):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as serverSocket:
        # Bind the server socket to the specified address and port
        serverSocket.bind((serverAddress, serverPort))
        print("Server Address UDP: ", serverAddress)
        print("Server Port UDP: ", serverPort)
        
        # List of file names to be sent to the client
        fileNames = []
        for i in range(0, 10):
            fileNames.append("large-" + str(i) + ".obj")
            fileNames.append("small-" + str(i) + ".obj")

        while True:
            try:
                # Receive an initial message from the client to initiate communication
                _, clientAddress = serverSocket.recvfrom(1024)
                if clientAddress:
                    # Send a greeting message to the client
                    serverSocket.sendto("Hello Client!".encode(), clientAddress)
                    serverSocket.settimeout(1)
            except socket.timeout as t:
                # Run the UDP helper function to handle file transfer
                udpHelper(serverSocket, clientAddress, fileNames, timeoutOptimal)
                break

# Main function to execute the UDP server
def main():
    # Get the UDP server port from the command line arguments
    serverPortUDP = int(sys.argv[1])
    
    # Timeout should be set to an optimal value for different test cases
    timeoutOptimal = float(sys.argv[2])

    # Get the computer's IP address
    serverAddress = socket.gethostbyname(socket.gethostname())

    # Run the UDP server function
    udp(serverAddress, serverPortUDP, timeoutOptimal)

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
    # Example usage: python3 udp_server.py 51
    # The script serves as a UDP server, handling file transfer with a client
