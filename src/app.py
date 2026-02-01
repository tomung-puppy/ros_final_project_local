import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# --- DI 컨테이너 및 서비스 초기화 ---
from src.container import container
from src.infrastructure.database.connection import Database
from src.infrastructure.communication.tcp_server import TCPServer
from src.infrastructure.communication.udp_server import start_udp_server

# .env 파일에서 환경 변수 로드
load_dotenv()

# 전역 변수로 백그라운드 태스크 저장
background_tasks = set()

# --- FastAPI 애플리케이션 설정 ---
async def startup_event():
    """애플리케이션 시작 시 모든 서비스를 초기화하고 백그라운드 서버를 가동합니다."""
    # 1. 데이터베이스 연결 풀 생성
    await Database.initialize()
    print("Database pool initialized.")
    
    # 2. DI 컨테이너 초기화 (서비스, 리포지토리 등)
    container.services()
    print("DI container and services initialized.")

    # 3. TCP/UDP 통신 서버를 백그라운드 태스크로 시작
    tcp_server = TCPServer(host='0.0.0.0', port=65432)
    tcp_task = asyncio.create_task(tcp_server.start())
    background_tasks.add(tcp_task)
    
    udp_task = asyncio.create_task(start_udp_server(host='0.0.0.0', port=54321, ai_service=container.ai_service))
    background_tasks.add(udp_task)
    
    print("TCP and UDP background servers are running.")


async def shutdown_event():
    """애플리케이션 종료 시 모든 백그라운드 태스크를 취소하고 리소스를 정리합니다."""
    for task in background_tasks:
        task.cancel()
    
    await asyncio.gather(*background_tasks, return_exceptions=True)
    print("Background servers stopped.")
    
    await Database.close()
    print("Database pool closed.")


# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="Office Robot Service API",
    description="[v3.0] UI와 API가 통합된 오피스 로봇 서비스",
    version="3.0.0",
    on_startup=[startup_event],
    on_shutdown=[shutdown_event]
)

# --- 정적 파일 마운트 ---
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# --- API 및 웹 라우터 등록 ---
from src.api.v1 import admin_routes, employee_routes
from src import web_routes
app.include_router(admin_routes.router)
app.include_router(employee_routes.router)
app.include_router(web_routes.router) # 웹 UI 라우터 추가

@app.get("/")
def read_root():
    """API 서버의 상태를 확인하고 UI 링크를 제공하는 기본 엔드포인트"""
    return {
        "message": "Office Robot Service API is running!",
        "admin_dashboard": "/web/admin",
        "employee_app": "/web/employee",
        "api_docs": "/docs"
    }

# uvicorn으로 이 앱을 실행하려면 터미널에서 다음 명령어를 사용하세요:
# uvicorn src.app:app --reload
