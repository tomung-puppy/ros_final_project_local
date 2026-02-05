import grpc
from typing import Dict, Any

# Generated gRPC files
from main_server.infrastructure.grpc import ai_inference_pb2
from main_server.infrastructure.grpc import ai_inference_pb2_grpc

class AIInferenceService:
    """
    gRPC를 통해 원격 AI Inference 서버와 통신하는 클라이언트 서비스.
    """
    def __init__(self, host: str = 'localhost', port: int = 50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = ai_inference_pb2_grpc.AIInferenceStub(self.channel)
        print(f"AI Inference gRPC Client 초기화 완료 (Connecting to {host}:{port}).")

    async def request_object_detection(self, image_id: str) -> Dict[str, Any]:
        """
        주어진 이미지 ID로 객체 인식을 요청합니다.
        """
        request = ai_inference_pb2.ImageRequest(image_id=image_id)
        response = await self.stub.DetectObjects(request)
        
        return {
            "object_name": response.object_name,
            "confidence": response.confidence,
            "box": {
                "x": response.box.x,
                "y": response.box.y,
                "width": response.box.width,
                "height": response.box.height
            }
        }

    async def request_face_recognition(self, image_id: str) -> Dict[str, Any]:
        """
        주어진 이미지 ID로 얼굴 인식을 요청합니다.
        """
        request = ai_inference_pb2.ImageRequest(image_id=image_id)
        response = await self.stub.RecognizeFaces(request)
        
        result = {
            "person_type": response.person_type,
            "confidence": response.confidence
        }
        if response.HasField("employee_id"): # Check if optional field is set
            result["employee_id"] = response.employee_id
            
        return result
    
    async def close(self):
        """gRPC 채널을 닫습니다."""
        await self.channel.close()
