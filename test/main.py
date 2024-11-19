payload = b"\x00" + b"test" + b"\x00" + b"test" + b"\x00" + b"test" + b"\x00" + b"test" + b"\x00"
payload = b"\xa0" + len(payload).to_bytes(byteorder="big") + payload
print(payload)
