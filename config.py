import os
import sys

from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = os.getenv("BASE_URL")
WANDB_API_KEY = os.getenv("WANDB_API_KEY")
MONGO_URL = os.getenv("MONGO_URL")
BQ_DATASET = os.getenv("BQ_DATASET")
BQ_TABLE = os.getenv("BQ_TABLE")
BQ_SERVICE_ACCOUNT = os.getenv("BQ_SERVICE_ACCOUNT")
USE_BIGQUERY_PRICES = os.getenv("USE_BIGQUERY_PRICES", "false").lower() == "true"

# Check and fail explicitly if something is missing
required_vars = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "BASE_URL": BASE_URL,
    "WANDB_API_KEY": WANDB_API_KEY,
    "MONGO_URL": MONGO_URL,
    "BQ_DATASET": BQ_DATASET,
    "BQ_TABLE": BQ_TABLE,
}

missing = [k for k, v in required_vars.items() if not v]
if missing:
    print(f"[error]: Missing required environment variables: {', '.join(missing)}")
    sys.exit(1)
