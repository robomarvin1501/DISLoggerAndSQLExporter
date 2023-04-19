"""
This is an API for the PlaybackLoggerFile class. This is so that a GUI can be created in other languages that
are incompatible with python (eg C#, Unity, etc).
"""
import re
import socket
import sys

from logger_jumping import PlaybackLoggerFile

# region udpsockets
local_ip = "127.0.0.1"
local_port = 5299
buffersize = 1024

udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

udp_server_socket.bind((local_ip, local_port))
# endregion udpsockets

plg = PlaybackLoggerFile("exp_1_2102_2.lzma", int(sys.argv[1]))

while True:
    bytes_address_pair = udp_server_socket.recvfrom(buffersize)
    message = bytes_address_pair[0].decode()
    if message == "exit":
        print("+++ PROGRAM ENDED +++")
        break
    elif message == "play":
        plg.play()
    elif message == "stop":
        plg.stop()
    elif message[:4] == "move" and len(ms := message.split(' ')) == 2 and re.match(
            r"^(?=.)([+-]?([0-9]*)(\.([0-9]+))?)$", ms[1]) is not None:
        plg.move(float(ms[1]))
    elif message[:8] == "playback" and len(ms := message.split(' ')) == 2 and re.match(
            r"^(?=.)([+-]?([0-9]*)(\.([0-9]+))?)$", ms[1]) is not None:
        plg.set_playback_speed(float(ms[1]))
    elif message[:15] == "set_exercise_id" and len(ms := message.split(' ')) == 2 and re.match(r"^[0-9]*$",
                                                                                               ms[1]) is not None:
        plg.set_exercise_id(int(ms[1]))
    elif message == "show":
        print(plg.status())

    print(message)
