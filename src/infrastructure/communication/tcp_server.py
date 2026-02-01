import asyncio
import json

class TCPServer:
    """
    로봇의 상태 보고(TCP 클라이언트)를 받고,
    필요 시 서버에서 로봇으로 명령을 내리기 위한 비동기 TCP 서버.
    """
    def __init__(self, host='0.0.0.0', port=65432):
        self.host = host
        self.port = port
        self.server = None
        # TODO: FleetManager 등 다른 서비스와 연동하여 상태를 업데이트하는 로직 필요
        # 예: self.fms = fms 

    async def handle_robot_client(self, reader, writer):
        """
        연결된 각 로봇 클라이언트를 처리하는 핸들러.
        """
        addr = writer.get_extra_info('peername')
        print(f"{addr}로부터 새로운 TCP 연결")

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                
                message = data.decode()
                print(f"TCP 수신 데이터 ({addr}): {message.strip()}")
                
                # TODO: 수신한 데이터를 JSON으로 파싱하여 처리
                # try:
                #     status_data = json.loads(message)
                #     robot_id = status_data.get("robot_id")
                #     # self.fms.update_robot_status(...)
                # except json.JSONDecodeError:
                #     print(f"Error: Invalid JSON received from {addr}")

                # 에코 응답
                writer.write(data)
                await writer.drain()

        except asyncio.CancelledError:
            print(f"클라이언트 {addr} 연결 태스크 취소됨.")
        finally:
            print(f"클라이언트 {addr} 연결 종료")
            writer.close()
            await writer.wait_closed()

    async def start(self):
        """
        TCP 서버를 시작합니다.
        """
        self.server = await asyncio.start_server(
            self.handle_robot_client, self.host, self.port)

        addr = self.server.sockets[0].getsockname()
        print(f'{addr}에서 TCP 서버가 실행 중입니다.')

        async with self.server:
            await self.server.serve_forever()

    def stop(self):
        if self.server:
            self.server.close()
            print("TCP 서버를 종료합니다.")

# 이 파일을 직접 실행하면 테스트용 TCP 서버가 가동됩니다.
async def main():
    tcp_server = TCPServer()
    try:
        await tcp_server.start()
    except KeyboardInterrupt:
        tcp_server.stop()

if __name__ == '__main__':
    asyncio.run(main())
