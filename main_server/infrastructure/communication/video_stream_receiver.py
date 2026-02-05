import asyncio

class UDPServerProtocol(asyncio.DatagramProtocol):
    """
    UDP 통신을 위한 비동기 프로토콜 핸들러.
    """
    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        # TODO: AI 서비스와 연동하여 이미지 처리 요청
        # if self.ai_service:
        #    print("UDP 서버가 AI 서비스와 연동되었습니다.")

    def connection_made(self, transport):
        self.transport = transport
        print("UDP 서버: 엔드포인트가 생성되었습니다.")

    def datagram_received(self, data, addr):
        """
        데이터그램(패킷)을 수신했을 때 호출됩니다.
        """
        message_length = len(data)
        print(f"{addr}로부터 {message_length} 바이트의 UDP 데이터 수신 (영상 스트림 패킷)")

        # TODO: 수신한 데이터를 AI 서비스로 전달하여 처리
        # if self.ai_service:
        #     # fire and forget
        #     asyncio.create_task(self.ai_service.request_object_detection(data))


    def error_received(self, exc):
        print(f'UDP 서버 에러 발생: {exc}')

    def connection_lost(self, exc):
        print("UDP 서버: 엔드포인트가 닫혔습니다.")


async def start_udp_server(host='0.0.0.0', port=54321, ai_service=None):
    """
    AI 추론을 위한 영상 스트림을 수신하는 UDP 서버를 시작합니다.
    """
    print(f"{host}:{port}에서 UDP 서버를 시작합니다...")
    loop = asyncio.get_running_loop()
    
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(ai_service=ai_service),
        local_addr=(host, port)
    )
    
    print("UDP 서버가 성공적으로 시작되었습니다.")

    try:
        # 서버가 계속 실행되도록 유지 (예: 무한정 대기)
        await asyncio.Event().wait()
    finally:
        print("UDP 서버를 종료합니다.")
        transport.close()


# 이 파일을 직접 실행하면 테스트용 UDP 서버가 가동됩니다.
async def main():
    await start_udp_server()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nUDP 서버 종료.")
