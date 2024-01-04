import socket
import sys
from packet import *  # Importing necessary modules

def tcp(serverAddress: str, serverPort: int):
    print("Server Address TCP: ", serverAddress)
    print("Server Port TCP: ", serverPort)
    
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocketTCP:
        # Bind the socket to the specified address and port
        serverSocketTCP.bind((serverAddress, serverPort))
        
        # Listen for incoming connections
        serverSocketTCP.listen()
        
        # Accept a connection from a client
        (clientSocketTCP, clientAddressTCP) = serverSocketTCP.accept()
        
        # Handle the connection with the client
        with clientSocketTCP:
            print(f"Connected by {clientAddressTCP}")
            print("TCP Packet Sending started.")
            
            # Receive the file name from the client
            while True:
                fileName = clientSocketTCP.recv(2048).decode()
                #print(fileName)
                
                # Check if a valid file name is received
                if fileName:
                    # Create a Packet object with the file name
                    packet = Packet(fileName)
                    
                    # Split the packet into smaller packets
                    packets = packet.splitPacket()
                    
                    # Send each smaller packet to the client
                    for i in range(packet.packetNumber):
                        clientSocketTCP.send(packets[i])
                else:
                    print('TCP Packet Sending has finished.')
                    break

def main():
    # Get Port Number
    serverPortTCP = int(sys.argv[1])
    
    # Get Computer IP Address
    serverAddress = socket.gethostbyname(socket.gethostname())
    
    # Run the TCP server function
    tcp(serverAddress, serverPortTCP)

if __name__ == "__main__":
    main()
    # Example usage: python3 tcp_server.py 50
    # The script binds to the specified port, listens for incoming connections, and sends file packets to connected clients
