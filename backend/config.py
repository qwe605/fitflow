import os
from dotenv import load_dotenv

load_dotenv()

ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
ARK_MODEL_ID = os.environ.get("ARK_MODEL_ID", "")
ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
