# main_server/config.py

# Server configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# Database configuration (example)
DATABASE_URL = "mysql+mysqlconnector://user:password@%:3306/mydatabase"

# ROS Bridge configuration (example)
ROS_BRIDGE_HOST = "0.0.0.0" # Updated from localhost to 0.0.0.0 for consistency with app.py example
ROS_BRIDGE_PORT = 9090

# AI Inference service configuration (example)
AI_INFERENCE_GRPC_HOST = "localhost"
AI_INFERENCE_GRPC_PORT = 50051

# Video Stream configuration
VIDEO_STREAM_HOST = "0.0.0.0"
VIDEO_STREAM_PORT = 54321

# FastAPI Application Metadata
APP_TITLE = "Office Robot Service API"
APP_DESCRIPTION = "[v3.0] UI와 API가 통합된 오피스 로봇 서비스"
APP_VERSION = "3.0.0"

# Web configurations
STATIC_FILES_DIR = "main_server/web/static"
ADMIN_DASHBOARD_PATH = "/web/admin"
EMPLOYEE_APP_PATH = "/web/employee"

