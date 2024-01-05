import socket
import sys
from time import time
from packet import *

def udp(serverAddress: str, serverPort: int, fileNames: list):
    # Lists to store timestamps for small and large files
    timestampListSmall = []
    timestampListLarge = []

    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as clientSocketUDP:
        # Initial handshake with the server
        while True:
            try:
                # Send a "Hello, server!" message to initiate communication
                clientSocketUDP.sendto("Hello, server!".encode(), (serverAddress, serverPort))
                clientSocketUDP.settimeout(0.05)
                (receivedMessage, _) = clientSocketUDP.recvfrom(2048)

                # If a response is received, break from the loop
                if receivedMessage:
                    break
            except socket.timeout as t:
                continue

        # Reset timeout to None for subsequent communications
        clientSocketUDP.settimeout(None)

        i = 0  # Index to iterate through the list of file names
        # Loop until all files are successfully received
        while i < len(fileNames):
            fileName = ""
            timestamp = [0.0, 0.0]
            sequenceNumberList = []
            dataList = []
            packetNumber = 0

            # Loop for receiving file packets
            while True:
                try:
                    # Receive a packet from the server
                    (receivedMessage, _) = clientSocketUDP.recvfrom(2048)

                    # If a packet is received, decode its contents
                    if receivedMessage:
                        decodedMessage = Packet.decodeUDP(receivedMessage)

                        # If decoding is successful and the file name matches the expected one
                        if decodedMessage != False and fileNames[i] == decodedMessage[0]:
                            receivedFileName, sequenceNumber, fileSize, data = decodedMessage

                            # Initialize variables on the first packet
                            if fileName == "":
                                fileName = receivedFileName
                                dataList = [-1] * fileSize
                                sequenceNumberList = [False] * fileSize
                                # Set starting timestamp
                                timestamp[0] = time()
                                packetNumber = fileSize

                            # Update data based on the received sequence number
                            if not sequenceNumberList[sequenceNumber]:
                                sequenceNumberList[sequenceNumber] = True
                                dataList[sequenceNumber] = data
                            
                            # Set last timestamp for last receiving message time 
                            timestamp[1] = time()

                            # Send an acknowledgment to the server
                            ackMsg = "ACK" + fileName[0] + str(sequenceNumber)
                            clientSocketUDP.sendto(ackMsg.encode(), (serverAddress, serverPort))

                        # If an "exit" message is received, check if all packets are received and break
                        if receivedMessage.decode() == "exit":
                            if sequenceNumberList.count(True) == packetNumber and packetNumber != 0:
                                if fileName != "":
                                    # Update timestamp lists based on file type
                                    if str(fileName).startswith("small"):
                                        timestampListSmall.append((timestamp[1] - timestamp[0]) * 1000)
                                    if str(fileName).startswith("large"):
                                        timestampListLarge.append((timestamp[1] - timestamp[0]) * 1000)

                                    # Reconstruct the file from received data and write to disk
                                    file = b""
                                    for data in dataList:
                                        file += data
                                    open(fileName, "wb").write(file)

                                    i += 1  # Move to the next file
                                    break
                            # Send "exit" to indicate that the client is ready for the next file
                            clientSocketUDP.sendto("exit".encode(), (serverAddress, serverPort))
                        else:
                            continue
                    else:
                        break
                except Exception as e:
                    # Handle exceptions during packet reception
                    continue

        # Print the final timestamp lists
        print(timestampListSmall)
        print(timestampListLarge)

def main():
    # Get Server Address
    serverAddress = sys.argv[1]

    # Get input Server Port Number
    serverPortUDP = int(sys.argv[2])

    fileNames = []

    # Generate file names for both small and large files
    for i in range(0, 10):
        fileNames.append("large-" + str(i) + ".obj")
        fileNames.append("small-" + str(i) + ".obj")

    with open('output_udp.txt', 'a') as output:
        # Redirect stdout to the file
        sys.stdout = output

        # Run the UDP client function
        udp(serverAddress, serverPortUDP, fileNames)

if __name__ == "__main__":
    main()
    # Example usage: python3 udp_client.py 192.168.56.1 51
    # The script sends files to a server using UDP and measures transfer times
