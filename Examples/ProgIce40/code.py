import board
import digitalio
import time

def not_eof(f):
    s = f.read(1)
    if s != b'':    # restore position
        f.seek(-1, 1)
    return s != b''


def write_byte(bite):
    if bite == 0:
        sout.value = False
        for _ in range(8):
            clk.value = False
            clk.value = True
    else:
        bits = bin(bite)[2:]
        sout.value = False
        for _zero in range(8 - len(bits)):
            clk.value = False
            clk.value = True

        for bit in bits:
            clk.value = False
            if bit == '0':
                sout.value = False
            else:
                sout.value = True
            clk.value = True


def dummy_clocks(clocks):
    for _dummy in range(clocks):
        clk.value = False
        sout.value = False
        clk.value = True


def flush_bytes():
    for x in range(50):
        write_byte(0x01)


def write_bytes(bitfile):
    byte_count = 0
    while True: #not_eof(bitfile)
        byte_count = byte_count + 64
        bites = f.read(64)
        if byte_count > num_bytes:
            break
        else:
            for b in bites:
                write_byte(b) # int.from_bytes(b, 0)

    print("Wrote {} bytes".format(byte_count))

sig = b'\x7e\xaa\x99\x7e'#b'~\xaa\x99~'
num_bytes = 104161

rst = digitalio.DigitalInOut(board.IO33)
rst.direction = digitalio.Direction.OUTPUT
ssel = digitalio.DigitalInOut(board.IO34)
ssel.direction = digitalio.Direction.OUTPUT
clk = digitalio.DigitalInOut(board.IO36)
clk.direction = digitalio.Direction.OUTPUT
sout = digitalio.DigitalInOut(board.IO35)
sout.direction = digitalio.Direction.OUTPUT

ssel.value = True
rst.value = False
ssel.value = False
clk.value = True
time.sleep(0.2)
rst.value = True
time.sleep(1.2)
ssel.value = True
dummy_clocks(8)
ssel.value = False

try:
    f = open("/logic.bin", "rb")
except OSError:
    print("Couldn't open file")

print("File opened")

try:
    byte_count = 0
    while not_eof(f):
        byte_count = byte_count + 1
        hex = f.read(1)
        #print(hex)
        if hex == b'\x7e':  # 0xAA
            f.seek(-1,1)
            hex = f.read(4)
            if hex == sig:
                print('Found bitimg sig: {} at {}'.format(hex, byte_count))
                f.seek(-4,1)
                write_bytes(f)
                break

    #flush_bytes()
    ssel.value = True
    dummy_clocks(100)
    dummy_clocks(49)


except OSError:
    print("Couldn't read logic bitfile")
finally:
    f.close()
print("Finished Programming")

