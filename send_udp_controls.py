import socket
server_address_port = ("127.0.0.1", 5299)
buffer_size = 1024

udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

msg = ""

while msg != "exit":
    msg = input("Command: ")
    bytes_to_send = str.encode(msg)

    udp_client_socket.sendto(bytes_to_send, server_address_port)
