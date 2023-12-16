import socket
import json
import struct

def pack_varint(data: int) -> bytes:
    o = b''

    while True:
        byte = data & 0x7F
        data >>= 7
        o += struct.pack('B', byte | (0x80 if data > 0 else 0))

        if data == 0:
            break

    return o

def unpack_varint_socket(sock: socket.socket) -> int:
    data = 0
    for i in range(5):
        o = sock.recv(1)

        if len(o) == 0:
            break

        byte = ord(o)
        data |= (byte & 0x7F) << 7 * i

        if not byte & 0x80:
            break

    return data

def send_json(sock: socket.socket, json_data: dict):    
    response = json.dumps(json_data).encode('utf8')
    response = pack_varint(len(response)) + response
    response = pack_varint(0x00) + response
    response = pack_varint(len(response)) + response

    sock.send(response)

def read_long_data(sock: socket.socket, size:int ) -> bytearray:
    data = bytearray()

    while len(data) < size:
        data += bytearray(sock.recv(size - len(data)))

    return data

def handle_client(sock: socket.socket, addr: str):
    packet_len = unpack_varint_socket(sock)
    data = read_long_data(sock, packet_len)

    if data[-1] == 1:
        status(sock)
    elif data[-1] == 2:
        login(sock)

def status(sock: socket.socket):
    a = sock.recv(2)
    if  a == b'\x01\x00':
        status = {
                    "version": {
                        "name": "ばーじょんのなまえ",
                        "protocol": 47
                    },
                    "players": {
                        "max": 0,
                        "online": 0
                    },
                    "description": {
                        "text": "せつめい"
                    }
                }
        send_json(sock, status)

def login(sock: socket.socket):
    login = {
        "text": "Hello, world!"
    }
    send_json(sock, login)

if __name__ =="__main__":
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('127.0.0.1', 25565))
    server_sock.listen()
    try:
        while True:
            sock, addr = server_sock.accept()
            handle_client(sock, addr)
    except KeyboardInterrupt:
        pass
    finally:
        server_sock.close()