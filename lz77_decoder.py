from argparse import ArgumentParser
import os.path

def main():
    # Parse input parameters
    parser = ArgumentParser(description='A tool decoding files encoded with lz77 algorithm (especially with encoder delivered with this tool)')
    parser.add_argument("encoded_file_path", nargs=1, help='path to file encoded with lz77 algorithm')
    parser.add_argument("output_file_path", nargs=1, help='path to store decoded data')
    parser.add_argument('-v', '--verbose', action='store_true', help='an optional argument to show each step of encoding and additional info')
    args = parser.parse_args()
    if args.verbose:
        print(f"Input args: \n\t \
        Encoded file: {args.encoded_file_path}\n\t \
        Output file: {args.output_file_path}\n\t")

    # check if output file exists
    if os.path.isfile(args.output_file_path[0]):
        askForOverwrite(args.output_file_path[0])

    # get encoded data
    with open(args.encoded_file_path[0], 'rb') as input_file:
        input_data = input_file.read()
    bin_data = bytesToBinaryString(input_data)

    # init decoded data store
    decoded_data = []

    # start decoding
    for i in range(0, len(bin_data), 20):
        # get one lz77 code data chunk
        data_chunk = bin_data[i:i+20]
        offset = int(data_chunk[0:8], 2)
        length = int(data_chunk[8:12], 2)
        next_char = int(data_chunk[12:20], 2)

        if args.verbose:
            print(f"<{offset}, {length}, {next_char}>")


        for j in range(length):
            decoded_data.append(decoded_data[-offset - 1]) # append substring from search buffer
        decoded_data.append(next_char) # append encoded character

    out_file = open(args.output_file_path[0], 'wb')
    out_file.write(bytearray(decoded_data))
    out_file.close()
        
def bytesToBinaryString(data):
    stream_bytes = bytes(data)
    string_arr = []
    for val in stream_bytes:
        string_arr.append("{0:08b}".format(val))
    decoded_str = ''.join(string_arr)
    return decoded_str
    
def askForOverwrite(path):
    do_overwrite = input(f'File {path} exists. Do you want to overwrite it? [y/N]')
    if (do_overwrite.lower() != 'y'):
        print(f"\nYou have been chosen NOT to overwrite file. Try again with different filename. Exiting...")
        exit(0)

main()