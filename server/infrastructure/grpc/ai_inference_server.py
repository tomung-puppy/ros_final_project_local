import grpc
import asyncio
from concurrent import futures
from typing import Dict, Any

# Generated gRPC files
from server.infrastructure.grpc import ai_inference_pb2
from server.infrastructure.grpc import ai_inference_pb2_grpc


class AIInferenceServicer(ai_inference_pb2_grpc.AIInferenceServicer):
    """
    Provides methods that implement functionality of AI inference server.
    """
    def __init__(self):
        print("AI Inference gRPC Servicer 초기화 완료 (Async Mock).")

    async def DetectObjects(self, request: ai_inference_pb2.ImageRequest, context) -> ai_inference_pb2.ObjectDetectionResponse:
        print(f"gRPC 객체 인식 추론 요청... (이미지 ID: {request.image_id})")
        await asyncio.sleep(0.5) # Simulate heavy model inference

        # Mock-up response based on image_id (e.g., its length or specific values)
        # In a real scenario, you would retrieve the image data using the ID
        # and then perform inference.
        if len(request.image_id) % 2 == 0:
            return ai_inference_pb2.ObjectDetectionResponse(
                object_name="Snack_A",
                confidence=0.98,
                box=ai_inference_pb2.BoundingBox(x=100, y=150, width=50, height=80)
            )
        else:
            return ai_inference_pb2.ObjectDetectionResponse(
                object_name="Book",
                confidence=0.92,
                box=ai_inference_pb2.BoundingBox(x=120, y=100, width=80, height=80)
            )

    async def RecognizeFaces(self, request: ai_inference_pb2.ImageRequest, context) -> ai_inference_pb2.FaceRecognitionResponse:
        print(f"gRPC 얼굴 인식 추론 요청... (이미지 ID: {request.image_id})")
        await asyncio.sleep(0.8) # Simulate heavier model inference

        # Mock-up response based on image_id
        if len(request.image_id) % 3 == 0:
             return ai_inference_pb2.FaceRecognitionResponse(
                person_type="Employee",
                employee_id="EMP-1024",
                confidence=0.99
            )
        else:
            return ai_inference_pb2.FaceRecognitionResponse(
                person_type="Guest",
                confidence=0.95
            )

async def serve() -> None:
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    ai_inference_pb2_grpc.add_AIInferenceServicer_to_server(AIInferenceServicer(), server)
    server.add_insecure_port('[::]:50051') # gRPC server port
    print("AI Inference gRPC Server starting on port 50051...")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
