# 영속적인 큐 생성 예제
# 디스크에 큐를 저장함

import requests
import json

# 큐 이름 및 브로커 주소
queue_name = "myPersistentQueue"
broker_url = "http://192.168.0.64:8161"  # ActiveMQ Artemis의 REST API URL

# 큐 생성 요청
response = requests.post(
    f"{broker_url}/api/addresses/{queue_name}",
    headers={'Content-Type': 'application/json'},
    json={
        "name": queue_name,
        "type": "queue",
        "durable": True,  # 영속적인 큐
        "auto-delete": False,
        "routing-types": ["anycast"]  # 큐 유형 설정
    }
)

# 응답 확인
if response.status_code == 201:
    print(f"큐 '{queue_name}' 가 성공적으로 생성되었습니다.")
else:
    print(f"큐 생성 실패: {response.status_code}, {response.text}")
