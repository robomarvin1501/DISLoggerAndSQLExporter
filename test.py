import socket


class DISReceiver:
    def __init__(self, port: int, msg_len=4096, timeout=15):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(timeout)
        self.sock.bind(("", port))

        self.msg_len = msg_len

    def __iter__(self):
        return self

    def __next__(self):
        try:
            data, addr = self.sock.recvfrom(self.msg_len)
            return addr, data
        except Exception as e:
            print(f"Got exception trying to receive {e}")
            raise StopIteration

    def __del__(self):
        print("Socket deleted")
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Socket exited")
        self.sock.close()


with DISReceiver(3000) as r:

    count = 0
    for (address, data) in r:
        print(f"Got packet from {address}: {data}")
        # Do stuff with data

        count += 1
        if count > 10:
            break
