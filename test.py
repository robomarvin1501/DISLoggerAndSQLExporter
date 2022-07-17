import socket

from opendis.PduFactory import createPdu


class DISReceiver:
    def __init__(self, port: int, exercise_id: int, msg_len: int = 4096, timeout: int = 15):
        """

        :param port: int : port on which dis is transmitted (usually 3000)
        :param exercise_id: int : The exercise id (experiments are usually 20, check wiki for further details)
        :param msg_len: int : The length of the message
        :param timeout: int : Amount of time to wait before giving up
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(timeout)
        self.sock.bind(("", port))

        self.msg_len = msg_len

        self.exercise_id = exercise_id

    def __iter__(self):
        return self

    def __next__(self):
        try:
            received_exercise_id = -1
            data, addr = "", ""
            while received_exercise_id != self.exercise_id:
                data, addr = self.sock.recvfrom(self.msg_len)
                received_pdu = createPdu(data)

                if received_pdu is not None:
                    received_exercise_id = received_pdu.exerciseID

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


with DISReceiver(3000, 97) as r:
    count = 0
    for (address, data) in r:
        print(f"Got packet from {address}: {data}")
        # Do stuff with data

        count += 1
        if count > 10:
            break
