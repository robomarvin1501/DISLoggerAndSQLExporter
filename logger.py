import subprocess
import os
import sys
import json
import threading
import lzma


def convert_to_json(target_input_file, target_output_file, logger_processing_dir):
    convert_to_json_instruction = ["powershell", "Start-Process",
                                   "-FilePath", r"'C:\Program Files\Wireshark\tshark.exe'",
                                   "-ArgumentList",
                                   rf"'-r {logger_processing_dir}\pcapngs\{target_input_file} -Tjson'",
                                   "-RedirectStandardOutput", f"{logger_processing_dir}\jsons\{target_output_file}",
                                   "-NoNewWindow"]
    subprocess.run(convert_to_json_instruction)


def process_json(json_dir, json_lock):
    processed_json_cache = set()
    while True:
        every_json_file = sorted(os.listdir(json_dir))
        unprocessed_json_files = [json_file for json_file in every_json_file if json_file not in processed_json_cache]
        for json_file in unprocessed_json_files:
            with open(fr"{json_dir}\{json_file}", 'r') as f:
                try:
                    current_file_contents = []
                    for packet in json.load(f):
                        try:
                            current_file_contents.append(packet["_source"]["layers"]["dis"])
                        except KeyError:
                            pass
                    processed_json_cache.add(json_file)
                    file_as_string = str(current_file_contents)[1:-1] + ','
                    file_as_bytes = file_as_string.encode("utf-8")
                    with json_lock:
                        compressed_bytes = lzc.compress(file_as_bytes)
                        output_file.write(compressed_bytes)
                except json.JSONDecodeError:
                    pass


logger_processing_dir = r"C:\Users\gidonr\LoggerFiles"
folders = os.listdir(logger_processing_dir)
if "jsons" not in folders:
    os.mkdir(f"{logger_processing_dir}/jsons")
if "pcapngs" not in folders:
    os.mkdir(f"{logger_processing_dir}/pcapngs")

subprocess.run(["powershell", "Start-Process", "-FilePath", r"'C:\Program Files\Wireshark\tshark.exe'", "-ArgumentList",
                rf"""'-i Ethernet -f "udp src port 3000 and udp dst port 3000" -b duration:2 -b files:5 -w {logger_processing_dir}\pcapngs\mult_output.pcapng'""",
                "-PassThru"])

json_lock = threading.Lock()
lzc = lzma.LZMACompressor()
output_filename = "log_0303_1408.lzma"
with open(fr"{logger_processing_dir}\{output_filename}", 'wb') as output_file:
    output_file.write(lzc.compress(b'['))

    threading.Thread(target=process_json, args=(fr"{logger_processing_dir}\jsons", json_lock), daemon=True).start()

    processed_pcap_cache = set()
    while True:
        try:
            every_cap = os.listdir(fr"{logger_processing_dir}\pcapngs")
            unprocessed_captures = [cap for cap in every_cap if cap not in processed_pcap_cache]
            for cap_file in unprocessed_captures:
                if cap_file != every_cap[-1]:
                    convert_to_json(cap_file, f"{cap_file[:-7]}.json", logger_processing_dir=logger_processing_dir)
                    processed_pcap_cache.add(cap_file)

                    jsons = os.listdir(f"{logger_processing_dir}/jsons")
                    if len(jsons) > 5:
                        subprocess.run(["del", fr"{logger_processing_dir}\jsons\{min(jsons)}"], shell=True)
        except KeyboardInterrupt:
            with json_lock:
                output_file.write(lzc.compress(b']'))
                output_file.write(lzc.flush())
            print("Program ended")
            break

sys.exit()
