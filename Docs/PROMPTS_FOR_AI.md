# AI 코드 생성을 위한 프롬프트 가이드 (v1.1)

이 문서는 'Office Robot Service' 프로젝트의 각 하위 시스템(AI 서버, 로봇, 사용자 앱, 데이터베이스)을 AI 개발 툴로 구현할 때 사용할 구체적인 프롬프트들을 모아놓은 가이드입니다.

모든 프롬프트는 메인 프로젝트의 `Docs/DEVELOPMENT_GUIDE.md`에 정의된 아키텍처와 API 명세를 기반으로 작성되었습니다. AI에게 요청 시, 이 파일의 내용을 복사하여 사용하세요.

---

## 1. AI 추론 서버 개발 프롬프트

**목표:** FastAPI를 사용하여 AI 추론을 전담하는 별도의 서버를 개발합니다. 이 서버는 로봇으로부터 UDP 영상 스트림을 직접 수신하고, 메인 서버로부터 HTTP 요청을 받아 추론 결과를 반환합니다.

```text
FastAPI를 사용하여 AI 추론 서버를 개발해줘. 이 서버는 다음 요구사항을 반드시 만족해야 해.

### 주요 요구사항:
1.  **API 엔드포인트 구현**:
    -   `POST /api/v1/inference/object_detection` 엔드포인트를 구현해야 해.
    -   요청/응답 형식은 아래 JSON 구조를 따라야 해.
        -   **요청**: `{ "request_id": "req-12345", "image_base64": "..." }`
        -   **응답**: `{ "request_id": "req-12345", "objects": [{ "class_name": "...", "confidence": 0.98, "bounding_box": [x,y,w,h] }] }`
    -   `image_base64` 필드는 실제 이미지를 Base64로 인코딩한 문자열이야.

2.  **UDP 영상 스트림 수신 기능**:
    -   로봇이 직접 보내는 H.264/MJPEG 인코딩된 UDP 영상 스트림을 수신해야 해.
    -   수신 포트는 54321을 사용하고, 비동기(asyncio) 기반으로 동작해야 해.
    -   수신한 패킷은 디코딩하여 이미지 프레임으로 변환하고, 이 프레임을 AI 추론 로직으로 전달해야 해.

3.  **Mock AI 로직**:
    -   실제 AI 모델은 아직 없어. `asyncio.sleep(0.5)`를 사용하여 0.5초의 가상 딜레이를 시뮬레이션하고, 미리 정해진 Mock JSON 데이터를 응답 형식에 맞춰 반환하도록 구현해줘.

4.  **파일 구조**:
    -   아래와 같은 파일 구조로 코드를 작성해줘.
        -   `ai_server/`
            -   `main.py`: FastAPI 앱 설정 및 API 라우터 포함
            -   `video_receiver.py`: UDP 스트림 수신 및 처리 로직
            -   `inference.py`: Mock AI 추론 함수
            -   `schemas.py`: API 요청/응답을 위한 Pydantic 모델 정의

### 의존성:
-   `fastapi`, `uvicorn`, `pydantic`, `opencv-python` 라이브러리를 사용해줘.
```

---

## 2. 로봇 엣지 패키지 개발 프롬프트

**목표:** ROS 2(rclpy)를 사용하여 로봇 위에서 동작하며 메인 서버 및 AI 서버와 통신하는 `communication_node` 패키지를 개발합니다.

```text
ROS 2 Jazzy와 rclpy(Python)를 사용하여 로봇의 `communication_node` 패키지를 개발해줘. 이 노드는 메인 서버 및 AI 서버와의 통신을 전담하며, 아래 명세를 반드시 따라야 해.

### 주요 요구사항:
1.  **제어 영역 (메인 서버와 통신)**:
    -   메인 서버의 `rosbridge_suite` (WebSocket)와 통신하는 클라이언트를 구현해야 해.
    -   **서버 -> 로봇**: 서버로부터 받은 행동 명령(`Action Command Sequence` JSON)을 파싱하여, 로봇 내부의 ROS 2 토픽인 `/cmd_sequence`로 발행(publish)해야 해.
    -   **로봇 -> 서버**: 로봇 내부의 `/robot_status` 토픽을 구독(subscribe)하고, 이 상태 데이터를 `Robot Status` JSON 형식으로 변환하여 WebSocket을 통해 서버로 전송해야 해.

2.  **데이터 영역 (AI 서버와 통신)**:
    -   로봇 내부의 이미지 토픽(`/camera/image_raw`, `sensor_msgs/Image` 타입)을 구독해야 해.
    -   구독한 이미지 프레임을 H.264 또는 MJPEG 형식으로 인코딩해야 해.
    -   인코딩된 영상 데이터를 AI 추론 서버의 IP 주소와 54321 포트로 UDP 스트리밍해야 해. 패킷 구조는 `[Frame ID (4 bytes)] + [Timestamp (8 bytes)] + [Image Data]` 형식을 따라야 해.

3.  **파일 구조**:
    -   `communication_node/` 패키지 내에 `bridge_node.py`라는 이름의 파이썬 파일로 모든 로직을 구현하고, ROS 2 패키지 필수 파일(`setup.py`, `package.xml`)을 형식에 맞게 생성해줘.

### 의존성:
-   `rclpy`, `sensor_msgs`, `websockets`, `opencv-python` 라이브러리를 사용해줘.
```

---

## 3. 사용자 앱 UI 개발 프롬프트

### 3.1. 관리자 대시보드 개발 (WebSocket 기반 실시간 업데이트)

**목표:** 기존 관리자 대시보드 HTML 파일에 WebSocket을 이용한 실시간 로봇 상태 모니터링 기능을 추가합니다.

```text
기존 `main_server/web/templates/admin_dashboard.html` 파일에 JavaScript 코드를 추가하여 WebSocket 기반의 동적인 관리자 대시보드를 만들어줘.

### 주요 요구사항:
1.  **WebSocket 연결**:
    -   JavaScript `WebSocket` API를 사용하여 메인 서버의 `/ws/admin/status` 엔드포인트에 연결해야 해.
    -   연결이 성공하면, 로봇 목록(`id="robot-list"`)과 작업 목록(`id="task-list"`)을 초기화하고, 연결 끊김 등의 예외 상황을 처리해야 해.

2.  **실시간 데이터 수신 및 UI 업데이트**:
    -   WebSocket을 통해 서버로부터 로봇 상태 업데이트 메시지를 수신해야 해.
    -   수신한 메시지는 JSON 형식이며, 업데이트된 단일 로봇 객체의 정보(예: `{ "id": 1, "name": "R-01", "status": "moving", "battery_level": 90.0, "pose_x": 1.2, "pose_y": 3.4 }`)를 포함할 거야.
    -   이 정보를 기반으로 `admin_dashboard.html` 내의 해당 로봇 정보를 찾아 업데이트하거나, 새로운 로봇이면 목록에 추가해야 해.

3.  **초기 로봇 및 작업 상태 로드**:
    -   WebSocket 연결 시점에는 모든 로봇과 작업의 초기 상태가 필요해. `fetch` API를 사용하여 `/api/v1/admin/robots`와 `/api/v1/admin/tasks` 엔드포인트에서 초기 데이터를 가져와 화면에 표시해야 해.

4.  **스타일링**:
    -   `main_server/web/static/admin_style.css` 파일을 수정하여 대시보드가 깔끔하고 보기 좋게 만들어줘. 특히 로봇의 상태(IDLE, MOVING, ERROR 등)에 따라 시각적인 피드백(색상, 아이콘)을 다르게 표현해줘.

5.  **코드 위치**:
    -   모든 JavaScript 코드는 `<script>` 태그 안에 작성하고, 이 태그는 `admin_dashboard.html` 파일의 `<body>` 태그가 닫히기 직전에 위치시켜줘.
```

### 3.2. 내부 직원용 앱 개발

**목표:** 내부 직원이 간단하게 로봇에게 작업을 요청할 수 있는 UI를 개발합니다.

```text
기존 `main_server/web/templates/employee_app.html` 파일에 JavaScript와 Form을 추가하여 작업 요청 기능을 구현해줘.

### 주요 요구사항:
1.  **입력 폼 (Form) 구현**:
    -   작업 종류를 선택할 수 있는 Dropdown(select) 메뉴를 만들어줘. (예: "간식 심부름", "사내 배달")
    -   상세 내용을 입력할 수 있는 텍스트 입력창(input)을 만들어줘. (예: "콜라 2개", "A팀 김대리에게 서류 전달")
    -   "작업 요청" 버튼을 만들어줘.

2.  **API 호출**:
    -   "작업 요청" 버튼을 클릭하면, `fetch` API를 사용하여 메인 서버의 `POST /api/v1/employee/tasks` 엔드포인트를 호출해야 해.
    -   Form에서 입력받은 데이터를 JSON 형식으로 만들어 요청 본문(body)에 담아 전송해야 해.

3.  **결과 피드백**:
    -   API 호출이 성공하면, 페이지에 "작업 요청이 성공적으로 접수되었습니다."와 같은 확인 메시지를 표시해줘.
```

---

## 4. 데이터베이스 스키마 생성 프롬프트

**목표:** 메인 서버와 동일한 위치에 있는 MySQL 데이터베이스의 초기 테이블 스키마를 생성하는 SQL 스크립트를 작성합니다.

```text
메인 서버의 `main_server/domains/` 디렉토리에 있는 Pydantic 모델들을 기반으로, MySQL 데이터베이스의 초기 테이블을 생성하는 SQL `CREATE TABLE` 스크립트를 작성해줘.

### 주요 요구사항:
1.  **`robots` 테이블**:
    -   `main_server/domains/robots/robot.py`의 `Robot` 모델과 `RobotStatus` Enum을 참조해줘.
    -   `id` (VARCHAR, PK), `status` (ENUM 타입), `battery` (FLOAT) 등의 컬럼을 포함해야 해.

2.  **`tasks` 테이블**:
    -   `main_server/domains/tasks/task.py`의 `Task` 모델과 `TaskStatus`, `TaskType` Enum을 참조해줘.
    -   `id` (VARCHAR, PK), `status` (ENUM 타입), `task_type` (ENUM 타입), `details` (TEXT), `robot_id` (VARCHAR, FK) 등의 컬럼을 포함해야 해.

3.  **공통 규칙**:
    -   모든 테이블은 `InnoDB` 엔진과 `utf8mb4` 캐릭터셋을 사용해야 해.
    -   모든 테이블에 `created_at` (기본값 CURRENT_TIMESTAMP)과 `updated_at` (업데이트 시 자동 변경) 컬럼을 `TIMESTAMP` 타입으로 추가해줘.
```
