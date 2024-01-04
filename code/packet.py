import math
import os
from hashlib import sha256
from sys import stderr
from time import time

"""
    Parameters:
        fileName (str): The name of the file to be processed.

    Attributes:
        filePath (str): The full path to the file.
        data (bytes): The binary data read from the file.
        packetLength (int): The maximum length of each packet.
        totalObjectLength (int): The total length of the binary data.
        packetNumber (int): The total number of packets required.
        objectsDirectory (str): The directory containing the objects.
"""

class Packet:
    filePath=""
    data= None
    packetLength = 1024
    totalObjectLength = 0
    packetNumber =0
    sequenceNumberList =[]
    separator  = "[5151-5151]"
    objectsDirectory = "../objects/"

    def __init__(self, fileName:str):
        try:
            # Construct the full file path
            filePath = os.path.join(self.objectsDirectory, fileName)
            self.filePath = filePath

            # Read the binary data from the file
            self.data = open(filePath, "rb").read()

            # Calculate the total length of the binary data
            self.totalObjectLength = len(self.data)

            # Calculate the total number of packets required
            self.packetNumber = math.ceil(self.totalObjectLength / self.packetLength)

        except Exception as err:
            # Handle file reading errors and print an error message
            print(f"Cannot read file: {filePath}. Error: {err}", file=stderr)

    def splitPacket(self):
        # Split the data into packets of specified length
        packets = []
        for i in range(self.packetNumber):
            startIndex = i * self.packetLength
            endIndex = (i + 1) * self.packetLength
            packetData = self.data[startIndex:endIndex]
            packets.append(packetData)
        return packets

    def encodeUDP(self, fileName: str, data: bytes, sequenceNumber: int, packetSize: int):
        # Encode packet information into a byte stream
        head = (fileName + self.separator + str(sequenceNumber) + self.separator + str(packetSize) + self.separator).encode()
        return head + data

    def decodeUDP(data: bytes):
        try:
            # Decode the UDP packet information from the byte stream
            argList = data.split(Packet.separator.encode())
            fileName = argList[0].decode()
            sequenceNumber = int(argList[1].decode())
            packetSize = int(argList[2].decode())
            data = argList[3]
            return fileName, sequenceNumber, packetSize, data
        except Exception as e:
            # Handle decoding errors and return False
            return False
