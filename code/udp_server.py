# udp_server.py
from random import randint
import socket
import sys
from packet import *

def udpHelper(serverSocket, clientAddress, fileNames: list):
    #fileNames (list): List of file names to be sent to the client.
    for fileName in fileNames:
        sequenceNumber = 0
        windowSize = 120
        baseNumber = 0
        print(fileName)
        packet = Packet(fileName)
        packets = packet.splitPacket()
        sequenceNumberList = [False] * packet.packetNumber

        # Loop until all packets are successfully sent and acknowledged
        while sequenceNumberList.count(True) != packet.packetNumber:
            # Send packets within the window
            serverSocket.settimeout(None)
            while sequenceNumber < baseNumber + windowSize and sequenceNumber < packet.packetNumber:
                if not sequenceNumberList[sequenceNumber]:
                    data = packet.encodeUDP(fileName, packets[sequenceNumber], sequenceNumber, packet.packetNumber)
                    serverSocket.sendto(data, clientAddress)
                sequenceNumber += 1

            # Set timeout for acknowledgment reception
            serverSocket.settimeout(0.13)
            while True:
                try:
                    (receivedMessage, _) = serverSocket.recvfrom(2048)
                    receivedMessageDecoded = receivedMessage.decode()

                    # Process acknowledgment messages
                    if receivedMessageDecoded.startswith("ACK"):
                        if fileName[0] == receivedMessageDecoded[3]:
                            receivedSequenceNumber = int(receivedMessageDecoded[4:])
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
                    sequenceNumber = baseNumber
                    break

        # Set timeout for "exit" message
        serverSocket.settimeout(0.1)
        while True:
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

def udp(serverAddress: str, serverPort: int):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as serverSocket:
        serverSocket.bind((serverAddress, serverPort))
        print("Server Address UDP: ", serverAddress)
        print("Server Port UDP: ", serverPort)
        fileNames = []
        for i in range(0, 10):
            fileNames.append("large-" + str(i) + ".obj")
            fileNames.append("small-" + str(i) + ".obj")

        while True:
            try:
                # Receive an initial message from the client to initiate communication
                _, clientAddress = serverSocket.recvfrom(1024)
                if clientAddress:
                    serverSocket.sendto("Hello Client!".encode(), clientAddress)
                    serverSocket.settimeout(1)
            except socket.timeout as t:
                # Run the UDP helper function to handle file transfer
                udpHelper(serverSocket, clientAddress, fileNames)
                break

def main():
    # Get server Address
    serverPortUDP = int(sys.argv[1])

    # Get computer IP Address
    serverAddress = socket.gethostbyname(socket.gethostname())

    # Run the UDP server function
    udp(serverAddress, serverPortUDP)

if __name__ == "__main__":
    main()
    # Example usage: python3 udp_server.py 51
    # The script serves as a UDP server, handling file transfer with a client
