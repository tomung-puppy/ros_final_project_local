# Office Robot Service - 개발 가이드 (v2.1)

이 문서는 'API 우선(API-First)' 개발 전략에 따라, Office Robot Service 프로젝트의 개선된 구조를 이해하고 병렬적인 다음 개발 단계를 진행하는 데 도움을 주기 위해 작성되었습니다.

---

## 1. 프로젝트 아키텍처 개요

본 프로젝트는 다음과 같은 두 개의 주요 애플리케이션으로 구성된 **모노레포(Monorepo)** 구조를 가집니다.

-   **`main_server/`**: 메인 서버 애플리케이션. FastAPI로 구현되었으며, 시스템의 두뇌 역할을 하는 컨트롤 타워입니다.
-   **`robot/`**: 로봇 엣지 애플리케이션. ROS 2 패키지들로 구성되며, 실제 로봇 위에서 구동됩니다.

## 2. 메인 서버 실행 방법 (`main_server/`)

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
1.  프로젝트 루트 디렉토리에서 아래 명령어를 실행하여 메인 서버를 시작합니다.
    ```bash
    uvicorn main_server.app:app --reload --host 0.0.0.0
  ```
2.  서버가 시작되면 아래 주소로 접속하여 각 기능을 확인할 수 있습니다.
    - **관리자 대시보드**: `http://127.0.0.1:8000/web/admin`
    - **직원용 앱**: `http://127.0.0.1:8000/web/employee`
    - **API 문서 (Swagger UI)**: `http://127.0.0.1:8000/docs`

### 실행 순서 (Startup Flow)
1.  `main_server/app.py`가 실행됩니다.
2.  FastAPI `startup_event`가 트리거됩니다.
    1.  데이터베이스 연결 풀을 생성합니다.
    2.  `main_server/container.py`를 통해 모든 서비스를 싱글턴으로 생성하고 의존성을 주입합니다.
    3.  **(TODO)** 로봇과의 통신을 담당할 `ROSBridge`와 `VideoStreamReceiver`가 백그라운드 태스크로 실행될 예정입니다. (현재는 비활성화)
3.  API와 웹 UI 요청을 처리할 준비가 완료됩니다.

---

## 3. 디렉토리 및 주요 코드 설명

### `robot/`
-   `src/`: 로봇에서 실행될 ROS 2 패키지들이 위치합니다.
    -   `navigation_node`: 자율 주행 및 경로 계획 담당.
    -   `perception_node`: 센서 데이터 기반 장애물 인식 담당.
    -   `communication_node`: 메인 서버와의 통신 담당.

### `main_server/`
-   `app.py`: FastAPI 애플리케이션의 메인 진입점.
-   `container.py`: **(중요)** 의존성 주입(DI) 컨테이너. 애플리케이션의 모든 핵심 서비스를 관리하는 중앙 허브.
-   `web/`: 웹 UI 관련 파일을 그룹화합니다.
    -   `routes.py`: Jinja2 템플릿을 사용하여 HTML 웹 페이지를 렌더링하는 라우터.
    -   `static/`: CSS, JS 등 정적 파일.
    -   `templates/`: HTML 템플릿 파일.
    -   `connection_manager.py`: WebSocket 연결을 관리하고 클라이언트에게 실시간 데이터를 브로드캐스트하는 모듈.
-   `api/v1/`: 버전 1의 REST API 엔드포인트.
    -   `admin_routes.py`, `employee_routes.py`, `guest_routes.py`.
-   `core_layer/`: 시스템의 핵심 비즈니스 로직.
    -   `fleet_management/fleet_manager.py`: 로봇 군집 관리 및 배차 담당.
    -   `task_management/task_manager.py`: 작업 생성 및 할당 담당.
-   `domains/`: 비즈니스 데이터 모델(Pydantic) 및 리포지토리 인터페이스(Protocol) 정의.
-   `infrastructure/`: 외부 시스템(DB, 통신 등)과의 연동을 책임지는 구현체.
    -   `database/`: SQLAlchemy 기반 DB 연결 및 Repository 구현.
    -   `communication/`: 통신 인프라.
        -   `ros_bridge.py`: **(제어)** 로봇과의 명령/상태 통신(Control Plane) 담당.
        -   `video_stream_receiver.py`: **(데이터)** 로봇의 영상 스트림 수신(Data Plane) 담당.

---

## 4. API 및 프로토콜 명세 (v1.0)

이 명세는 각 팀(로봇, AI, 앱)이 메인 서버와 통신하기 위해 지켜야 할 **개발 계약(Contract)**입니다.

### A. 메인 서버 <-> 로봇 통신

#### 1. 제어 영역 (Control Plane)
-   **프로토콜**: WebSocket을 사용한 `rosbridge_suite` (TCP 기반)
-   **메시지 형식**: JSON

##### 서버 -> 로봇: Action Command Sequence
로봇에게 수행할 행동의 순차 목록을 전달합니다.
```json
{
  "sequence_id": "seq-1672531200",
  "actions": [
    {
      "action_id": "act-001",
      "type": "GOTO",
      "params": { "x": 10.5, "y": -2.1, "theta": 1.57 }
    },
    {
      "action_id": "act-002",
      "type": "PICKUP",
      "params": { "item_id": "snack-01" }
    },
    {
      "action_id": "act-003",
      "type": "DISPLAY",
      "params": { "screen": "follow_me" }
    }
  ]
}
```

##### 로봇 -> 서버: Robot Status
로봇이 자신의 상태를 주기적으로 서버에 보고합니다.
```json
{
  "robot_id": "R-01",
  "battery": 85.5,
  "status": "IDLE",
  "pose": { "x": 0.5, "y": 1.2, "theta": 0.0 },
  "last_action_id": "act-001",
  "action_status": "COMPLETED"
}
```

#### 2. 데이터 영역 (Data Plane)
-   **대상**: 로봇 -> AI 추론 서버
-   **프로토콜**: Raw UDP
-   **데이터 형식**: H.264/MJPEG 인코딩 영상 프레임
-   **패킷 구조 (예시)**: `[Frame ID (4 bytes)] + [Timestamp (8 bytes)] + [Image Data]`

### B. AI 추론 서버 API
AI 추론 서버는 다음 REST API 엔드포인트를 구현해야 합니다.

##### `POST /api/v1/inference/object_detection`
-   **요청 (Request)**:
    ```json
    {
      "request_id": "req-12345",
      "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAE..."
    }
    ```
-   **응답 (Response)**:
    ```json
    {
      "request_id": "req-12345",
      "objects": [
        {
          "class_name": "Snack_A",
          "confidence": 0.98,
          "bounding_box": [100, 150, 50, 50]
        }
      ]
    }
    ```

### C. 사용자 앱 <-> 메인 서버 API
-   **프로토콜**: HTTP/HTTPS (REST API), WebSocket (실시간 업데이트)

##### 1. REST API 명세
메인 서버 실행 후 `http://<서버_IP>:8000/docs` 에서 제공되는 **Swagger UI 문서를 기준**으로 합니다.
-   **주요 신규 API**:
    -   `POST /api/v1/guest/qr/verify`: 게스트의 QR 코드를 검증하고 안내 로봇을 호출합니다.

##### 2. 관리자 앱 실시간 업데이트 (WebSocket)
-   **엔드포인트**: `ws://<서버_IP>:8000/ws/admin/status`
-   **메시지 형식**: 서버가 클라이언트에게 `Robot` 객체의 JSON 직렬화 문자열을 푸시합니다.
    ```json
    {
      "id": 1,
      "name": "R-01",
      "status": "moving",
      "battery_level": 90.0,
      "pose_x": 1.2,
      "pose_y": 3.4,
      "current_task_id": 123
    }
    ```

---

## 5. 다음 구현 단계 (상세 구현 로드맵)

### **1. 최적 로봇 배차 알고리즘 구체화 (Priority: 높음)**
-   **파일:** `main_server/core_layer/fleet_management/fleet_manager.py`
-   **함수:** `find_optimal_robot(self, target_pose: tuple)`
-   **구현할 내용:** 단순 직선 거리가 아닌, 실제 지도 기반 경로 거리, 작업 우선순위, 로봇 상태 가중치를 포함하는 종합 점수 모델을 설계하여 최적의 로봇을 선택하도록 알고리즘을 고도화합니다.

### **2. 실제 로봇 통신 로직 구현 (Priority: 높음)**
-   **파일:** `main_server/infrastructure/communication/ros_bridge.py`
-   **클래스:** `MockRobotCommunicator`를 실제 `rosbridge_suite`와 연동하는 `RealRobotCommunicator` (가칭)로 교체합니다. 서버가 로봇의 상태 보고를 수신하고, 행동 명령 시퀀스를 전송하는 로직을 구현합니다.

### **3. AI 추론 서비스 연동 (Priority: 중간)**
-   **파일:** `main_server/core_layer/ai_inference/inference_service.py`
-   **구현할 내용:** 현재 Mock 상태인 AI 서비스를, 실제 AI 추론 서버의 REST API (`B. AI 추론 서버 API` 명세 참고)를 호출하는 HTTP 클라이언트로 구현합니다.
-   **파일:** `main_server/infrastructure/communication/video_stream_receiver.py`
    -   AI 서버가 아닌 메인 서버에서 UDP 스트림을 받는다면, 수신한 데이터를 `AIInferenceService`로 전달하는 로직을 활성화합니다. (이상적으로는 이 로직은 AI 서버에 있어야 합니다.)