import subprocess
import os
import sys
import xml.etree.ElementTree as ET
import threading
import lzma


def convert_to_xml(target_input_file, target_output_file, logger_processing_dir):
    """
    Creates a silent tshark subprocess to convert a pcapng file in the pcapng sub-folder,
    to an xml file in the xml sub-folder

    :param target_input_file: str - Name of input file
    :param target_output_file: str - Name of output file
    :param logger_processing_dir: str - Complete path to the directory where the logs are being stored
    :return: None
    """
    convert_to_xml_instruction = ["powershell", "Start-Process",
                                  "-FilePath", r"'C:\Program Files\Wireshark\tshark.exe'",
                                  "-ArgumentList",
                                  rf"""'-J "dis" -r {logger_processing_dir}\pcapngs\{target_input_file} -Tpdml'""",
                                  "-RedirectStandardOutput", fr"{logger_processing_dir}\xmls\{target_output_file}",
                                  "-NoNewWindow"]
    subprocess.run(convert_to_xml_instruction)


def process_xml(xml_dir, xml_lock):
    """
    This function is called within a separate thread to process any unprocessed, complete xml file.
    This is achieved by reading, compressing, and then outputting to the compressed output file.

    :param xml_dir: str - Complete path to xml sub-folder
    :param xml_lock: Lock - The threading Lock object within the program
    :return: None
    """
    processed_xml_cache = set()
    while True:
        # All but the last file to keep it from trying to read an incomplete file
        every_xml_file = sorted(os.listdir(xml_dir))[:-1]
        unprocessed_xml_files = [xml_file for xml_file in every_xml_file if xml_file not in processed_xml_cache]

        for xml_file in unprocessed_xml_files:
            tree = ET.parse(fr"{xml_dir}\{xml_file}")
            root = tree.getroot()

            current_file_contents = []

            for packet in root:
                for proto in packet:
                    if proto.attrib["name"] == "dis":
                        # Extract only the necessary data
                        current_file_contents.append(ET.tostring(proto))

            processed_xml_cache.add(xml_file)
            file_as_bytes = b"".join(current_file_contents)
            with xml_lock:  # Lock the objects (race conditions), compress the data, and write it
                compressed_bytes = lzc.compress(file_as_bytes)
                output_file.write(compressed_bytes)



logger_processing_dir = r"C:\Users\gidonr\LoggerFiles"
# Either replace the temp folders, or create them if necessary
folders = os.listdir(logger_processing_dir)
if "xmls" not in folders:
    os.mkdir(f"{logger_processing_dir}/xmls")
else:
    os.rmdir(f"{logger_processing_dir}/xmls")
if "pcapngs" not in folders:
    os.mkdir(f"{logger_processing_dir}/pcapngs")
else:
    os.rmdir(f"{logger_processing_dir}/pcapngs")

# Start recording pcapngs to the pcapng temporary folder
subprocess.run(["powershell", "Start-Process", "-FilePath", r"'C:\Program Files\Wireshark\tshark.exe'", "-ArgumentList",
                rf"""'-i Ethernet -f "udp src port 3000 and udp dst port 3000" -b duration:2 -b files:5 -w {logger_processing_dir}\pcapngs\mult_output.pcapng'""",
                "-PassThru"])

xml_lock = threading.Lock()
lzc = lzma.LZMACompressor()
output_filename = "log_0303_1408.lzma"
with open(fr"{logger_processing_dir}\{output_filename}", 'wb') as output_file:
    output_file.write(lzc.compress(b"""<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet type="text/xsl" href="pdml2html.xsl"?>
<pdml version="0" creator="wireshark/3.6.2" time="Mon Mar  7 15:43:25 2022" capture_file="C:\Users\gidonr\LoggerFiles\pcapngs\mult_output_00001_20220307154322.pcapng">
"""))  # Write the opening of the xml file

    # Start processing any xml output files
    threading.Thread(target=process_xml, args=(fr"{logger_processing_dir}\xmls", xml_lock), daemon=True).start()

    """
    This processes every pcapng file, aside from the last one, since that one is probably incomplete at the time 
    of running. Every processed pcapng is added to the filename cache, to ensure the same file is not processed twice.
    Excess xmls are also removed here to preserve space, since they will never be touched again.
    
    I chose 5 for the number of pcapngs, and xmls, for personal security. In theory, 2 or 3 would work, but 5
    won't be particularly difficult either, and it ensures things should definitely be fine.
    """
    processed_pcap_cache = set()
    while True:
        try:
            every_cap = os.listdir(fr"{logger_processing_dir}\pcapngs")
            unprocessed_captures = [cap for cap in every_cap if cap not in processed_pcap_cache]

            for cap_file in unprocessed_captures:
                if cap_file != every_cap[-1]:
                    convert_to_xml(cap_file, f"{cap_file[:-7]}.pdml", logger_processing_dir=logger_processing_dir)
                    processed_pcap_cache.add(cap_file)

                    xmls = os.listdir(f"{logger_processing_dir}/xmls")
                    if len(xmls) > 5:
                        subprocess.run(["del", fr"{logger_processing_dir}\xmls\{min(xmls)}"], shell=True)
        except KeyboardInterrupt:
            # On exiting the program, write the closer to the xml, in the compressed file, flush the
            # LZMACompressor, and exit
            with xml_lock:
                output_file.write(lzc.compress(b"</pdml>"))
                output_file.write(lzc.flush())
            print("Program ended")
            break

sys.exit()
