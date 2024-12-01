# 페이로드 테스트 노트
# 파이썬 코드 테스트 용

payload = b"\x00" + b"test" + b"\x00" + b"test" + b"\x00" + b"test" + b"\x00" + b"test" + b"\x00"
payload = b"\xa0" + len(payload).to_bytes(byteorder="big") + payload
print(payload)
