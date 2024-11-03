import subprocess  # noqa: S404

from environs import Env

VERSION = (
    subprocess.check_output(["git", "describe", "--always"])  # noqa: S603,S607
    .strip()
    .decode()
)

env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")
BOT_ID: str = BOT_TOKEN.split(":")[0]

OPENAI_API_KEY: str = env.str("OPENAI_API_KEY")

LOGGING_LEVEL: int = env.int("LOGGING_LEVEL", 10)

POSTGRES_HOST: str = env.str("POSTGRES_HOST", "localhost")
POSTGRES_PORT: int = env.int("POSTGRES_PORT", 5432)
POSTGRES_USER: str = env.str("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD: str = env.str("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB: str = env.str("POSTGRES_DB", "papers_db")

FSM_HOST: str = env.str("FSM_HOST")
FSM_PORT: int = env.int("FSM_PORT")
FSM_PASSWORD: str = env.str("FSM_PASSWORD")

USE_CACHE: bool = env.bool("USE_CACHE", False)

if USE_CACHE:
    CACHE_HOST: str = env.str("CACHE_HOST")
    CACHE_PORT: int = env.int("CACHE_PORT")
    CACHE_PASSWORD: str = env.str("CACHE_PASSWORD")

USE_WEBHOOK: bool = env.bool("USE_WEBHOOK", False)

if USE_WEBHOOK:
    MAIN_WEBHOOK_ADDRESS: str = env.str("MAIN_WEBHOOK_ADDRESS")
    MAIN_WEBHOOK_SECRET_TOKEN: str = env.str("MAIN_WEBHOOK_SECRET_TOKEN")

    MAIN_WEBHOOK_LISTENING_HOST: str = env.str("MAIN_WEBHOOK_LISTENING_HOST")
    MAIN_WEBHOOK_LISTENING_PORT: int = env.int("MAIN_WEBHOOK_LISTENING_PORT")

    MAX_UPDATES_IN_QUEUE: int = env.int("MAX_UPDATES_IN_QUEUE", 100)

USE_CUSTOM_API_SERVER: bool = env.bool("USE_CUSTOM_API_SERVER", False)

if USE_CUSTOM_API_SERVER:
    CUSTOM_API_SERVER_IS_LOCAL: bool = env.bool("CUSTOM_API_SERVER_IS_LOCAL")
    CUSTOM_API_SERVER_BASE: str = env.str("CUSTOM_API_SERVER_BASE")
    CUSTOM_API_SERVER_FILE: str = env.str("CUSTOM_API_SERVER_FILE")

DROP_PREVIOUS_UPDATES: bool = env.bool("DROP_PREVIOUS_UPDATES", False)
