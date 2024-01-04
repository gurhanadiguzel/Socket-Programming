# TCP and UDP File Transfer Benchmark

This project demonstrates both TCP and UDP-based file transfer benchmarks between a client and a server. The server sends files to the client, and the transfer times are measured and logged.

## File Descriptions

### `packet.py`

This module provides a Packet class that helps with encoding and decoding packets for UDP communication. It splits large files into smaller packets and includes packet information such as file name, sequence number, and packet size.

### `tcp_client.py` and `tcp_server.py`

These files implement a simple TCP-based file transfer benchmark. The client sends a list of file names to the server, and the server responds by sending the corresponding files. Transfer times for small and large files are measured and printed.

#### Running the TCP Server and the TCP Client:

```bash
python3 tcp_server.py <SERVER_PORT>
python3 tcp_client.py <SERVER_ADDRESS> <SERVER_PORT>
```

### `udp_client.py`  and `udp_server.py`

These files implement a simple UDP-based file transfer benchmark. The server sends files to the client, and the transfer times are measured and printed. The project uses a custom packet.py module to handle encoding and decoding packets for UDP communication.

#### Running the UDP Server and the UDP Client:

```bash
python3 udp_server.py <SERVER_PORT>
python3 udp_client.py <SERVER_ADDRESS> <SERVER_PORT>
```