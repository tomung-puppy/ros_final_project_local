import asyncio
from typing import Dict, Any

class AIInferenceService:
    """
    카메라 영상(데이터)을 받아 객체/얼굴을 인식하고 결과를 반환하는 비동기 서비스.
    실제로는 원격 GPU 서버에 HTTP 요청을 보내는 등의 작업을 수행할 수 있습니다.
    """
    def __init__(self):
        print("AI Inference Service 초기화 완료 (Async Mock).")
        # 예: self.http_client = httpx.AsyncClient(base_url="http://gpu-server:8000")

    async def request_object_detection(self, image_data: bytes) -> Dict[str, Any]:
        """
        주어진 이미지에서 간식 등 객체를 식별하도록 요청합니다.
        (SR-006: 간식 인식 기능)
        """
        print(f"객체 인식 추론 요청... (이미지 크기: {len(image_data)} bytes)")
        # 원격 서버와 통신하거나 무거운 모델을 돌리는 시간 가정
        await asyncio.sleep(0.5) 
        
        # Mock-up 응답 (이미지 내용에 따라 다른 결과 반환 시뮬레이션)
        if len(image_data) % 2 == 0:
            return {"object_name": "Snack_A", "confidence": 0.98, "box": [100, 150, 50, 80]}
        else:
            return {"object_name": "Book", "confidence": 0.92, "box": [120, 100, 80, 80]}


    async def request_face_recognition(self, image_data: bytes) -> Dict[str, Any]:
        """
        주어진 이미지에서 얼굴을 감지하고 내부인/외부인을 판별하도록 요청합니다.
        (SR-005: 방문객 확인 기능)
        """
        print(f"얼굴 인식 추론 요청... (이미지 크기: {len(image_data)} bytes)")
        await asyncio.sleep(0.8) # 얼굴 인식이 더 오래 걸린다고 가정

        # Mock-up 응답
        # 실제로는 DB와 연동하여 직원 ID 등을 반환
        if len(image_data) % 3 == 0:
             return {"person_type": "Employee", "employee_id": "EMP-1024", "confidence": 0.99}
        else:
            return {"person_type": "Guest", "confidence": 0.95}

