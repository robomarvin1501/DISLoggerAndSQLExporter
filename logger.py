import subprocess
import os
import sys
import json
from utils.json_decoder import JSON_decoder
import threading
import lzma


def convert_to_json(target_input_file, target_output_file, logger_processing_dir):
    """
    Creates a silent tshark subprocess to convert a pcapng file in the pcapng sub-folder,
    to a json file in the json sub-folder

    :param target_input_file: str - Name of input file
    :param target_output_file: str - Name of output file
    :param logger_processing_dir: str - Complete path to the directory where the logs are being stored
    :return: None
    """
    convert_to_json_instruction = ["powershell", "Start-Process",
                                   "-FilePath", r"'C:\Program Files\Wireshark\tshark.exe'",
                                   "-ArgumentList",
                                   rf"'-r {logger_processing_dir}\pcapngs\{target_input_file} -Tjson'",
                                   "-RedirectStandardOutput", f"{logger_processing_dir}\jsons\{target_output_file}",
                                   "-NoNewWindow"]
    subprocess.run(convert_to_json_instruction)


def process_json(json_dir, exercise_id, json_lock):
    """
    This function is called within a separate thread to process any unprocessed, complete json file.
    This is achieved by reading, compressing, and then outputting to the compressed output file.

    :param json_dir: str - Complete path to json sub-folder
    :param exercise_id: integer id, 20 is simulations, etc
    :param json_lock: Lock - The threading Lock object within the program
    :return: None
    """
    processed_json_cache = set()
    exercise_id = str(exercise_id)  # In the packet it's a str, not int
    while True:
        every_json_file = sorted(os.listdir(json_dir))[:-1]
        unprocessed_json_files = [json_file for json_file in every_json_file if json_file not in processed_json_cache]

        for json_file in unprocessed_json_files:
            with open(fr"{json_dir}\{json_file}", 'r') as f:
                try:  # Only completed files
                    current_file_contents = []
                    for packet in JSON_decoder.decode(f.read()):
                        try:  # Only the files WITH DIS data, and that is of the correct ExerciseId
                            if packet["_source"]["layers"]["dis"]["Header"]["dis.exer_id"] == exercise_id:
                                current_packet = {}
                                current_packet.update(packet["_source"]["layers"]["dis"])
                                current_packet.update({
                                    "frame": {
                                        "WorldTime": packet["_source"]["layers"]["frame"]["frame.time_epoch"],
                                        "PacketTime": packet["_source"]["layers"]["frame"]["frame.time_relative"]
                                    }
                                })
                                current_file_contents.append(current_packet)
                        except KeyError:
                            pass
                    # Add the file to the cache of filenames, convert to bytes without [],
                    # and add a trailing comma because this is a list of JSON
                    processed_json_cache.add(json_file)
                    if len(current_file_contents) > 0:
                        file_as_string = json.dumps(current_file_contents)[1:-1] + ','
                        # JSON must have double quotes, this is for ease of reading
                        # file_as_string = file_as_string.replace("'", '"')
                        file_as_bytes = file_as_string.encode("utf-8")
                        with json_lock:  # Lock the objects (race conditions), compress the data, and write it
                            compressed_bytes = lzc.compress(file_as_bytes)
                            output_file.write(compressed_bytes)
                except json.JSONDecodeError:
                    print("JSONDecodeError")


logger_processing_dir = r"C:\Users\gidonr\LoggerFiles"
# Either replace the temp folders, or create them if necessary
folders = os.listdir(logger_processing_dir)
if "jsons" not in folders:
    os.mkdir(f"{logger_processing_dir}/jsons")
else:
    os.rmdir(f"{logger_processing_dir}/jsons")
if "pcapngs" not in folders:
    os.mkdir(f"{logger_processing_dir}/pcapngs")
else:
    os.rmdir(f"{logger_processing_dir}/pcapngs")

# Start recording pcapngs to the pcapng temporary folder
subprocess.run(["powershell", "Start-Process", "-FilePath", r"'C:\Program Files\Wireshark\tshark.exe'", "-ArgumentList",
                rf"""'-i Ethernet -f "udp src port 3000 and udp dst port 3000" -b duration:2 -b files:5 -w {logger_processing_dir}\pcapngs\mult_output.pcapng'""",
                "-PassThru"])

json_lock = threading.Lock()
lzc = lzma.LZMACompressor()
exercise_id = 97
output_filename = "integration_2402.lzma"
with open(fr"{logger_processing_dir}\{output_filename}", 'wb') as output_file:
    output_file.write(lzc.compress(b'['))  # Write the opening of the JSON list

    # Start processing any JSON output files
    threading.Thread(target=process_json, args=(fr"{logger_processing_dir}\jsons", exercise_id, json_lock),
                     daemon=True).start()

    """
    This processes every pcapng file, aside from the last one, since that one is probably incomplete at the time 
    of running. Every processed pcapng is added to the filename cache, to ensure the same file is not processed twice.
    Excess jsons are also removed here to preserve space, since they will never be touched again.
    
    I chose 5 for the number of pcapngs, and jsons, for personal security. In theory, 2 or 3 would work, but 5
    won't be particularly difficult either, and it ensures things should definitely be fine.
    """
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
            # On exiting the program, write the closer to the json, in the compressed file, flush the
            # LZMACompressor, and exit
            with json_lock:
                output_file.write(lzc.compress(b']'))
                output_file.write(lzc.flush())
            print("Program ended")
            break

sys.exit()
