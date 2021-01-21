from argparse import ArgumentParser
import os.path

def main():
    # Parse input parameters
    parser = ArgumentParser()
    parser.add_argument("input_file_path", nargs=1)
    parser.add_argument("output_file_path", nargs=1)
    parser.add_argument('-v', '--verbose', action='store_true', help='an optional argument to show each step of encoding and additional info')
    args = parser.parse_args()
    if args.verbose:
        print(f"Given args: \n\t \
        Input file: {args.input_file_path}\n\t \
        Output file: {args.output_file_path}\n\t")
    
    # Init buffers length
    DICT_BUFFER_LENGTH = 256
    LOOK_AHEAD_BUFFER_LENGTH = 15
    OUTPUT_BUFFER_SIZE = 2.5 * 8 * 2 # 2.5 byte per information * 8 bits * 2 informations to get 5 full bytes to write to file

    # Open input and output files
    with open(args.input_file_path[0], 'rb') as input_file:
        input_data = input_file.read()
    input_data_length = len(input_data)
    output_file_path = args.output_file_path[0]
    file_extension = output_file_path.split('.')[-1] if len(output_file_path.split('.')) > 1 else ''
    if file_extension == '':
        output_file_path = output_file_path + '.lz77'
        if args.verbose:
            print(f"Output file has not have any extension, changed output file path to {output_file_path}")
    if os.path.isfile(output_file_path):
        askForOverwrite(output_file_path)
    output_file = open(output_file_path, 'wb')

    output_data_length = 0
    output_buffer = '' # init output file buffer
    current_pos = 0 # init current processing byte in input file variable
    while current_pos < input_data_length:
        # fill the buffers
        dict_buffer = input_data[current_pos - DICT_BUFFER_LENGTH:current_pos] if current_pos - DICT_BUFFER_LENGTH > 0 else input_data[0:current_pos]
        look_ahead_buffer = input_data[current_pos:current_pos + LOOK_AHEAD_BUFFER_LENGTH] if current_pos + LOOK_AHEAD_BUFFER_LENGTH < input_data_length else input_data[current_pos:input_data_length]

        # find longest match
        [offset, length, next_char] = findLongestMatch(dict_buffer, look_ahead_buffer)
        
        if args.verbose:
            print(f'<{offset}, {length}, {next_char}>') 
        
        # write encoded data to file
        bin_result = convertSearchResultToBinary(offset, length, next_char)
        output_buffer = output_buffer + bin_result
        if len(output_buffer) == OUTPUT_BUFFER_SIZE:
            output_data_length = output_data_length + (OUTPUT_BUFFER_SIZE / 8)
            writeDataChunk(output_file, output_buffer)
            output_buffer = ''

        # seek input file by length of longest match + one character encoded in third parameter of LZ77 algorithm output
        current_pos = current_pos + length + 1

    printCompressionInfo(input_data_length, output_data_length) # print compression summary info

    # close file handlers
    input_file.close()
    output_file.close()
    
    
def convertSearchResultToBinary(offset, length, next_char):
    offset_binary = '{0:08b}'.format(offset)
    length_binary = '{0:04b}'.format(length)
    next_char_binary = '{0:08b}'.format(next_char)
    return offset_binary + length_binary + next_char_binary

def binaryStringToBytearray(stream):
    return bytearray(int(stream[i:i+8], 2) for i in range(0, len(stream), 8))

def writeDataChunk(out_file, out_buffer):
    bytes_to_write= binaryStringToBytearray(out_buffer)
    out_file.write(bytes_to_write)

def findLongestMatch(db, lab):
    buff = db + lab # merge buffers to enable to find match going beyond dictionary buffer

    #init result variables
    offset = 0
    length = 0
    next_char = lab[0]
    
    for i in range(0, len(db)):
        curr_offset = 0
        curr_length = 0
        while (buff[i + curr_length] == lab[curr_length]):
            if (curr_length == 0):
                curr_offset = len(db) - i - 1 # searching from start of dictionary buffer (farthest position from current data)
            curr_length = curr_length + 1
            if curr_length > length:
                length = curr_length
                offset = curr_offset
                next_char = lab[curr_length] if curr_length < len(lab) else ''
            if curr_length == len(lab): # if pattern match is as long as whole look ahead buffer go back by 1 step (otherwise next character parameter will be null)
                length = curr_length - 1
                next_char = lab[length]
                break
    return [offset, length, next_char]

def askForOverwrite(path):
    do_overwrite = input(f'File {path} exists. Do you want to overwrite it? [y/N]')
    if (do_overwrite.lower() != 'y'):
        print(f"\nYou have been chosen NOT to overwrite file. Try again with different filename. Exiting...")
        exit(0)

def getFileSize(file):
    file.seek(0,2) # move the cursor to the end of the file
    size = file.tell()
    return size

def printCompressionInfo(input_size, output_size):
    cr = input_size / output_size
    cp = 1 - (1 / cr)
    br = 1 / cr * 8
    print(f"\nCompression stats: \n \
        \tCR (compression ratio) = {cr}\n \
        \tCP (compression percentage) = {cp}\n \
        \tBR (bit rate) = {br}\n")

main()
