import json
from typing import List, Dict, Any
from .protocols import IRobotCommunicator

class MockRobotCommunicator(IRobotCommunicator):
    """
    로봇과의 통신을 흉내내는 Mock 구현체.
    실제 로봇 대신 콘솔에 명령을 출력합니다.
    """
    def __init__(self, host: str = "localhost", port: int = 6000):
        self.host = host
        self.port = port
        print(f"Mock Robot Communicator 초기화: TCP 클라이언트를 {host}:{port}에 연결 시도 (시뮬레이션).")

    def send_action_sequence(self, robot_name: str, actions: List[Dict[str, Any]]):
        """
        로봇에게 수행할 액션 시퀀스를 전송합니다.
        실제로는 TCP 소켓을 통해 JSON 메시지를 전송할 것입니다.
        """
        message = {
            "robot_name": robot_name,
            "type": "ACTION_SEQUENCE",
            "payload": actions
        }
        
        # 실제 네트워크 전송 대신, 직렬화된 메시지를 콘솔에 출력
        serialized_message = json.dumps(message, indent=2)
        print("--- [MockRobotCommunicator] 로봇에게 아래 명령 전송 ---")
        print(serialized_message)
        print("----------------------------------------------------")

    def listen_for_status(self):
        """
        로봇으로부터 상태 업데이트를 비동기적으로 수신 대기합니다.
        (이 예제에서는 별도 스레드나 asyncio 태스크에서 실행된다고 가정)
        """
        print("[MockRobotCommunicator] 로봇 상태 수신 대기 시작 (시뮬레이션)...")
        # 실제 구현에서는 루프 안에서 소켓으로부터 데이터를 읽는 로직이 들어감
        pass