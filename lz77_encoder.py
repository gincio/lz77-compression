from argparse import ArgumentParser

def main():
    # Buffer lengths in bytes
    parser = ArgumentParser()
    parser.add_argument("input_file_path", nargs=1)
    parser.add_argument("output_file_path", nargs=1)
    args = parser.parse_args()
    print(f"Given args: {args}")
    DICT_BUFFER_LENGTH = 256
    LOOK_AHEAD_BUFFER_LENGTH = 15
    OUTPUT_BUFFER_SIZE = 2.5 * 8 * 2 # 2.5 byte * 8 bits * 2 informations to get 5 full bytes to write to file (python works only with bytes, not bits)

    with open(args.input_file_path[0], 'rb') as input_file:
        input_data = input_file.read()
    input_data_length = len(input_data)
    
    output_file = open(args.output_file_path[0], 'wb')
    output_buffer = ''
    current_pos = 0
    while current_pos < input_data_length:
        # fill the buffers
        dict_buffer = input_data[current_pos - DICT_BUFFER_LENGTH:current_pos] if current_pos - DICT_BUFFER_LENGTH > 0 else input_data[0:current_pos]
        look_ahead_buffer = input_data[current_pos:current_pos + LOOK_AHEAD_BUFFER_LENGTH] if current_pos + LOOK_AHEAD_BUFFER_LENGTH < input_data_length else input_data[current_pos:input_data_length]
        #print(f"dict buffer: {dict_buffer}\nlook ahead: {look_ahead_buffer}")
        
        # find longest match
        [offset, length, next_char] = findLongestMatch(dict_buffer, look_ahead_buffer)
        
        # TODO: write encoded data to file
        bin_result = convertSearchResultToBinary(offset, length, next_char)
        output_buffer = output_buffer + bin_result
        if len(output_buffer) == OUTPUT_BUFFER_SIZE:
            writeDataChunk(output_file, output_buffer)
            output_buffer = ''
        # seek data by length of longest match + one character encoded in third parameter of LZ77 encoding
        current_pos = current_pos + length + 1
    
    input_file.close()
    output_file.close()
    
def convertSearchResultToBinary(offset, length, next_char):
    offset_binary = '{0:08b}'.format(offset)
    length_binary = '{0:04b}'.format(length)
    next_char_binary = '{0:08b}'.format(next_char)
    #print(f'offset: {offset} ({offset_binary}), len: {length} ({length_binary}), next: {next_char} ({next_char_binary})')
    return offset_binary + length_binary + next_char_binary

def binaryStringToBytearray(stream):
    return bytearray(int(stream[i:i+8], 2) for i in range(0, len(stream), 8))

def writeDataChunk(out_file, out_buffer):
    bytes_to_write= binaryStringToBytearray(out_buffer)
    #print(f"{bytes_to_write}")
    out_file.write(bytes_to_write)

def findLongestMatch(db, lab):
    buff = db + lab
    offset = 0
    length = 0
    next_char = lab[0]
    
    for i in range(0, len(db)):
        curr_offset = 0
        curr_length = 0
        while (buff[i + curr_length] == lab[curr_length]):
            if (curr_length == 0):
                curr_offset = len(db) - i - 1
            curr_length = curr_length + 1
            if curr_length > length:
                length = curr_length
                offset = curr_offset
                next_char = lab[curr_length] if curr_length < len(lab) else ''
            if curr_length == len(lab):
                length = curr_length - 1
                next_char = lab[length]
                break
    #print(f'<{offset}, {length}, {next_char}>') 
    return [offset, length, next_char]


main()
