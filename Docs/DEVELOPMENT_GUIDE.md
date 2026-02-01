# Office Robot Service - 개발 가이드

이 문서는 Office Robot Service 프로젝트의 구조를 이해하고, 다음 개발 단계를 진행하는 데 도움을 주기 위해 작성되었습니다.
리팩토링을 통해 각 모듈의 역할이 명확해졌고, 중앙화된 DI 컨테이너를 도입하여 유지보수성을 높였습니다.

---

## 1. 프로젝트 실행 방법

### 필수 환경
- Python 3.8+
- `uvicorn`, `fastapi`, `python-dotenv`, `sqlalchemy`, `asyncmy`, `jinja2` 등
- **(권장)** `requirements.txt` 파일을 생성하여 아래 패키지들을 관리하세요.
  ```
  fastapi
  uvicorn[standard]
  python-dotenv
  sqlalchemy
  asyncmy
  pydantic
  jinja2
  ```

### 실행
1.  프로젝트 루트 디렉토리에서 아래 명령어를 실행하여 단일 통합 서버(API + Web UI + Communication)를 시작합니다.
    ```bash
    uvicorn src.app:app --reload --host 0.0.0.0
    ```
2.  서버가 시작되면 아래 주소로 접속하여 각 기능을 확인할 수 있습니다.
    - **관리자 대시보드**: `http://127.0.0.1:8000/web/admin`
    - **직원용 앱**: `http://127.0.0.1:8000/web/employee`
    - **API 문서 (Swagger UI)**: `http://127.0.0.1:8000/docs`

### 실행 순서 (Startup Flow)
1.  `src/app.py`가 실행됩니다.
2.  FastAPI `startup_event`가 트리거됩니다.
    1.  데이터베이스 연결 풀을 생성합니다.
    2.  `src/container.py`를 통해 모든 서비스를 싱글턴으로 생성하고 의존성을 주입합니다.
    3.  TCP 및 UDP 통신 서버를 백그라운드 태스크로 실행합니다.
3.  API와 웹 UI 요청을 처리할 준비가 완료됩니다.

---

## 2. 주요 코드 파일 설명

### `src/`
-   `app.py`: FastAPI 애플리케이션의 메인 진입점. 서버 시작/종료, 라우터 등록, 정적 파일 마운트를 관리합니다.
-   `container.py`: **(중요)** 의존성 주입(DI) 컨테이너. 애플리케이션의 모든 핵심 서비스를 생성하고 관리하는 중앙 허브입니다.
-   `web_routes.py`: **(UI)** Jinja2 템플릿을 사용하여 HTML 웹 페이지(관리자 대시보드, 직원 앱)를 렌더링하는 라우터.

### `src/api/v1/`
-   `admin_routes.py`: 관리자용 REST API 엔드포인트.
-   `employee_routes.py`: 직원용 REST API 엔드포인트.

### `src/core_layer/`
-   **`fleet_management/fleet_manager.py`**: **(핵심 로직)** 로봇 군집(Fleet) 관리 시스템. 최적 로봇 배차, 작업 명령 시퀀스 생성, 로봇 상태 업데이트를 담당합니다.
-   **`task_management/task_manager.py`**: **(핵심 로직)** 작업 관리 시스템. 사용자 요청을 받아 작업을 생성하고, `FleetManager`와 연동하여 로봇에 작업을 할당합니다.
-   `ai_inference/inference_service.py`: AI 추론 서비스. 로봇의 카메라로부터 받은 이미지로 객체/얼굴 인식을 수행합니다 (현재 Mock).
-   `office_iot/iot_controller.py`: 사무실 IoT 장비(조명, 온도 등)를 제어하는 서비스입니다 (현재 Mock).

### `src/domains/`
-   `robots/robot.py`: `Robot` 데이터 모델(Pydantic) 및 상태(Enum) 정의.
-   `robots/robot_repository.py`: `Robot` 데이터에 접근하기 위한 리포지토리 인터페이스(Protocol).
-   `tasks/task.py`: `Task` 데이터 모델 및 상태/타입(Enum) 정의.
-   `tasks/task_repository.py`: `Task` 데이터에 접근하기 위한 리포지토리 인터페이스(Protocol).

### `src/infrastructure/`
-   `database/`: 데이터베이스 연결 및 실제 Repository 구현체.
    -   `connection.py`: `asyncio` 기반 DB 연결 관리.
    -   `repositories/mysql_robot_repository.py`: `IRobotRepository`의 MySQL 구현체.
    -   `repositories/mysql_task_repository.py`: `ITaskRepository`의 MySQL 구현체.
-   `communication/`: 로봇과의 통신 인프라.
    -   `protocols.py`: 로봇 통신 인터페이스(`IRobotCommunicator`) 정의.
    -   `robot_communicator.py`: `IRobotCommunicator`의 Mock 구현체. **(실제 통신 로직 구현 필요)**
    -   `tcp_server.py`: 로봇의 상태 보고 및 명령 하달을 위한 TCP 서버.
    -   `udp_server.py`: 로봇의 영상 스트림 수신을 위한 UDP 서버.

---

## 3. 다음 구현 단계 (상세 구현 로드맵)

현재 시스템의 핵심 뼈대는 완성되었지만, 내부 로직은 대부분 Mock 상태이거나 초기 단계입니다. 아래 함수와 알고리즘을 상세히 구현하여 프로젝트를 완성해야 합니다.

### **1. 최적 로봇 배차 알고리즘 구체화 (Priority: 높음)**
-   **파일:** `src/core_layer/fleet_management/fleet_manager.py`
-   **함수:** `find_optimal_robot(self, target_pose: tuple)`
-   **현재 상태:** IDLE 상태이고 배터리가 20% 이상인 로봇 중, 유클리드 거리(`L2-norm`)만 계산하여 가장 가까운 로봇을 선택.
-   **구현할 내용:**
    -   **경로 거리 계산:** 현재 위치에서 목적지까지의 실제 경로 거리를 계산하는 로직 추가 필요. (단순 직선 거리가 아닌, 지도 기반의 A* 또는 Dijkstra 알고리즘 적용 고려)
    -   **작업 우선순위 반영:** `Task`의 우선순위(`details`에 포함)를 점수 계산에 반영. (예: 긴급 > 일반)
    -   **로봇 상태 가중치:** 로봇의 현재 작업 큐 길이, 에러 상태 여부 등을 점수에 반영.
    -   **최종 점수(Score) 계산:** `Score = w1 * (경로 거리) + w2 * (배터리 패널티) + w3 * (우선순위 보너스)` 와 같은 종합 점수 모델 설계.

### **2. 실제 로봇 통신 로직 구현 (Priority: 높음)**
-   **파일:** `src/infrastructure/communication/robot_communicator.py`
-   **클래스:** `MockRobotCommunicator`를 `RealRobotCommunicator` (가칭)로 교체 또는 수정.
-   **현재 상태:** 로봇에게 보낼 명령(JSON)을 콘솔에 출력만 하는 Mock 클래스.
-   **구현할 내용:**
    -   `__init__`: 실제 로봇과의 통신 채널(TCP 소켓, MQTT 클라이언트 등)을 초기화.
    -   `send_action_sequence`: 직렬화된 JSON 메시지를 실제 통신 채널을 통해 로봇에게 **전송(send)**.
-   **파일:** `src/infrastructure/communication/tcp_server.py`
    -   `handle_robot_client`: 로봇이 보내는 상태 보고(JSON)를 수신하면, 이를 파싱하여 `container.fleet_manager.update_robot_status`를 호출하도록 로직 추가. (주석 처리된 부분 활성화)

### **3. AI 추론 서비스 연동 (Priority: 중간)**
-   **파일:** `src/core_layer/ai_inference/inference_service.py`
-   **함수:** `request_object_detection`, `request_face_recognition`
-   **현재 상태:** `asyncio.sleep`으로 대기 후, 정해진 Mock 데이터를 반환.
-   **구현할 내용:**
    -   실제 GPU 추론 서버가 있다면, `httpx` 같은 HTTP 클라이언트를 사용하여 이미지 데이터(`image_data`)를 해당 서버의 API로 POST 요청을 보내고, 그 결과를 받아 반환하는 로직 구현.
    -   경량 모델(TFLite 등)을 엣지에서 직접 돌릴 경우, 해당 모델을 로드하고 추론하는 코드를 이 함수 내에 작성.
-   **파일:** `src/infrastructure/communication/udp_server.py`
    -   `datagram_received`: 수신한 UDP 패킷(`data`)을 `ai_service`의 추론 함수로 넘겨주는 `asyncio.create_task` 부분의 주석을 해제하고 실제 호출.

### **4. 교착 상태(Deadlock) 회피/해결 로직 (Priority: 낮음)**
-   **파일:** `src/core_layer/fleet_management/fleet_manager.py`
-   **함수:** (신규 생성 필요) `resolve_traffic_conflict` 등
-   **현재 상태:** 미구현.
-   **구현할 내용:**
    -   주기적으로 모든 로봇의 경로를 확인하여, 경로가 겹치거나 충돌 위험이 있는지 감지하는 로직.
    -   충돌 감지 시, 작업 우선순위가 낮은 로봇에게 `PAUSE` 또는 `RE-PATH(임시 대기 장소)` 명령을 `IRobotCommunicator`를 통해 전송하는 기능 구현.
    -   `SR-013` 문서의 우선순위 (가이드 > 물품 > 간식)를 참고하여 정책 수립.
