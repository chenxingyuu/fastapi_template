import configparser
import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    project_name: str = "My FastAPI Project"
    api_version: str = "/api/v1"
    doc_path: str = "/docs"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000


@dataclass
class MySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    @property
    def db_url(self):
        return f"mysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def db_url_pymysql(self):
        return f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'


@dataclass
class RedisConfig:
    host: str
    port: int
    password: str
    default_db: int

    @property
    def db_url(self):
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.default_db}"


@dataclass
class SecurityConfig:
    secret_key: str
    algorithm: str
    token_expire_days: int


@dataclass
class GithubOAuthConfig:
    client: str
    secret: str


@dataclass
class Settings:
    app: AppConfig
    mysql: MySQLConfig
    redis: RedisConfig
    security: SecurityConfig
    github: GithubOAuthConfig


def get_config_path() -> str:
    """获取配置文件的路径，确保路径为绝对路径"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.getenv("CONFIG_FILE_PATH", "../config.ini")
    if not os.path.isabs(config_file_path):
        config_file_path = os.path.abspath(os.path.join(base_dir, config_file_path))
    return config_file_path


def read_config() -> Settings:
    """读取配置文件并返回配置设置"""
    file_path = get_config_path()

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    config = configparser.ConfigParser()
    config.read(file_path)

    app_config = AppConfig(**config["app"])
    app_config.debug = config.getboolean("app", "debug")
    app_config.port = config.getint("app", "port")

    mysql_config = MySQLConfig(**config["mysql"])
    redis_config = RedisConfig(**config["redis"])
    security_config = SecurityConfig(**config["security"])
    security_config.token_expire_days = config.getint("security", "token_expire_days")

    github_oauth_config = GithubOAuthConfig(**config["github"])

    return Settings(
        app=app_config,
        mysql=mysql_config,
        redis=redis_config,
        security=security_config,
        github=github_oauth_config,
    )


settings = read_config()
