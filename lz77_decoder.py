def main():
    input_file = open('encoded.lz77', 'rb')
    input_data = input_file.read()
    input_file.close()
    bin_data = bytesToBinaryString(input_data)
    decoded_data = []
    for i in range(0, len(bin_data), 40):
        data_chunk = bin_data[i:i+40]
        offset1 = int(data_chunk[0:8], 2)
        length1 = int(data_chunk[8:12], 2)
        next_char1 = int(data_chunk[12:20], 2)
        offset2 = int(data_chunk[20:28], 2)
        length2 = int(data_chunk[28:32], 2)
        next_char2 = int(data_chunk[32:40], 2)
        #print(f"<{offset1}, {length1}, {next_char1}>\n<{offset2}, {length2}, {next_char2}>")
        # TODO: FIX saving decoded file error!! Files are not the same!
        for j in range(length1):
            decoded_data.append(decoded_data[-offset1 - 1])
        decoded_data.append(next_char1)
        for j in range(length2):
            decoded_data.append(decoded_data[-offset2 - 1])
        decoded_data.append(next_char2)
    print(f'{decoded_data}')
    out_file = open('decoded.bmp', 'wb')
    out_file.write(bytearray(decoded_data))
    out_file.close()
        
        
def bytesToBinaryString(data):
    stream_bytes = bytes(data)
    string_arr = []
    for val in stream_bytes:
        string_arr.append("{0:08b}".format(val))
    decoded_str = ''.join(string_arr)
    return decoded_str
    
main()
