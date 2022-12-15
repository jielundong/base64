import argparse
import sys
base64_letters = []
base64_letters+=[(chr(i)) for i in range(ord('A'),ord('Z')+1)] + \
[chr(i) for i in range(ord('a'),ord('z')+1)] + [chr(i) for i in range(ord('0'),ord('9')+1)] + ['+', '/']
base64_map = dict(zip(base64_letters, range(64)))

def generateBase64Bytes(data):
    b64 = []
    index = 0
    previousByte = None
    dataLen = len(data)
    for i in range(dataLen):
        b = data[i]
        cycle = i % 3
        if cycle == 0:
            b64.append(base64_letters[(b & 0b11111100) >> 2])
            index += 1
        elif cycle == 1:
            b64.append(base64_letters[((previousByte & 0b00000011) << 4) | ((b & 0b11110000) >> 4)] )
            index += 1
        elif cycle == 2:
            b64.append(base64_letters[((previousByte & 0b00001111) << 2) | ((b & 0b11000000) >> 6)] )
            b64.append(base64_letters[b & 0b00111111])
            index += 2
        if i == dataLen - 1:
            if cycle == 0:
                b64.append(base64_letters[(b & 0b00000011) << 4])
                index += 1
            elif cycle == 1:
                b64.append(base64_letters[(b & 0b00001111) << 2])
                index += 1
        if index % 76 == 0:
            b64.append('\n')
        previousByte = b
    return "".join(b64)

def streamedEncodeBase64(file):
    b64 = []
    #the original file index
    i = 0
    #base64 index
    index = 0
    previousByte = None
    data = file.read(1)
    while data:
        b = data[0]
        cycle = i % 3
        if cycle == 0:
            b64.append(base64_letters[(b & 0b11111100) >> 2])
            index += 1
        elif cycle == 1:
            b64.append(base64_letters[((previousByte & 0b00000011) << 4) | ((b & 0b11110000) >> 4)] )
            index += 1
        elif cycle == 2:
            b64.append(base64_letters[((previousByte & 0b00001111) << 2) | ((b & 0b11000000) >> 6)] )
            b64.append(base64_letters[b & 0b00111111])
            index += 2
        data = file.read(1)
        if not data:
            if cycle == 0:
                b64.append(base64_letters[(b & 0b00000011) << 4])
                index += 1
            elif cycle == 1:
                b64.append(base64_letters[(b & 0b00001111) << 2])
                index += 1
            break
        if index % 76 == 0:
            b64.append('\n')
            print("".join(b64), end="")
            b64 = []
        previousByte = b
        i += 1
    #To calculate the number of supplemental '=' sign, we should exclude the new line '\n', so , we use index instead of len(b64)
    supplemet = index % 4
    if supplemet > 0:
        b64 += ["="] * (4 - supplemet)
    print("".join(b64))



def streamedDecodeBase64(file):
    goodformat = True
    org = bytearray()
    # base64 index
    i = 0
    # index of org
    index = 0
    data = file.read(4)
    while data:
        if ("".join(data).strip()) == "":
            data = file.read(4)
            continue
        tmp = data.split('\n')
        while len(tmp) > 1:
            data = "".join(tmp)
            data2 = file.read(4-len(data))
            data += data2
            tmp = data.split('\n')
        if len(data) < 4:
            goodformat = False
        data = data.strip("=")
        val = []
        for d in data:
            val.append(base64_map[d])
        if len(val) == 4:
            org.append((val[0] & 0b00111111) << 2 | (val[1] & 0b00110000) >> 4)
            org.append((val[1] & 0b00001111) << 4 | (val[2] & 0b00111100) >> 2)
            org.append((val[2] & 0b00000011) << 6 | val[3] )
            index += 3
        elif len(val) == 3:
            org.append((val[0] & 0b00111111) << 2 | (val[1] & 0b00110000) >> 4)
            org.append((val[1] & 0b00001111) << 4 | (val[2] & 0b00111100) >> 2)
            index += 2
        elif len(val) == 2:
            org.append((val[0] & 0b00111111) << 2 | (val[1] & 0b00110000) >> 4)
            index += 1
        else:
            goodformat = False
        if index % 128 == 0:
            sys.stdout.buffer.write(org)
            org.clear()
        data = file.read(4)
    sys.stdout.buffer.write(org)
    if not goodformat:
        print("invalid input")
        
    

def encodeBase64Streamed(path):
    with open(path, "rb") as f:
        streamedEncodeBase64(f)

def decodeBase64Streamed(path):
    with open(path, "r") as f:
        streamedDecodeBase64(f)

def encodeBase64(path):
    with open(path, "rb") as f:
        data = f.read()
        b64 = generateBase64Bytes(data)
        print(b64)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", action='store_true', help="decode base64")
    ap.add_argument("filename")
    args = vars(ap.parse_args())
    decode = args['d']
    if decode:
        decodeBase64Streamed(args['filename'])
    else:
        encodeBase64Streamed(args['filename'])

