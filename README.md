# FastAPI 模板

一个用于构建 FastAPI 应用程序的模板项目，包含 Tortoise ORM 和 Aerich 用于数据库迁移。

## 特性

- 使用 FastAPI 构建 API
- 使用 Tortoise ORM 进行数据库建模
- 使用 Aerich 管理数据库迁移
- 使用 Pydantic 进行数据验证
- 支持 Docker 和 Docker Compose 进行容器化
- 实现了基于角色的访问控制（RBAC）

## 使用

### 安装

1. **克隆仓库：**

    ```bash
    git clone https://github.com/chenxingyuu/fastapi_template.git
    cd fastapi-template
    ```

2. **创建并激活虚拟环境：**

    ```bash
    python -m venv venv
    source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
    ```

3. **安装依赖项：**

    ```bash
    pip install -r requirements.txt
    ```

### 迁移

1. **初始化 Aerich：**

    ```bash
    aerich init -t cores.model.TORTOISE_ORM
    ```

2. **初始化数据库：**

    ```bash
    aerich init-db
    ```

3. **创建并应用迁移：**

    ```bash
    aerich migrate
    aerich upgrade
    ```

4. **你也可以使用make**

    ```bash
    make help
    ```

### 运行

1. **设置配置文件路径：**

   在 Linux 或 macOS 上：
    ```bash
    export CONFIG_FILE_PATH=/path/to/your/config.ini
    ```

   在 Windows 上：
    ```cmd
    set CONFIG_FILE_PATH=C:\path\to\your\config.ini
    ```

2. **启动 FastAPI 应用程序：**

    ```bash
    uvicorn app.main:app --reload
    ```

3. **访问应用程序：**

   打开浏览器并访问 `http://127.0.0.1:8000`。

### 使用 Docker

1. **构建 Docker 镜像：**

    ```bash
    docker build -t fastapi-template .
    ```

2. **运行 Docker 容器：**

    ```bash
    docker run -d -p 8000:8000 --name fastapi-template fastapi-template
    ```

3. **访问应用程序：**

   打开浏览器并访问 `http://127.0.0.1:8000`。

### 使用 Docker Compose

1. **启动服务：**

    ```bash
    docker-compose up -d
    ```

2. **访问应用程序：**

   打开浏览器并访问 `http://127.0.0.1:8000`。

3. **停止服务：**

    ```bash
    docker-compose down
    ```

## 开发

1. **安装 pre-commit 钩子：**

    ```bash
    pre-commit install
    ```

2. **运行测试：**

    ```bash
    pytest
    ```

3. **检查代码并格式化：**

    ```bash
    pre-commit run --all-file
    ```

4. **在开发模式下运行应用程序：**

    ```bash
    uvicorn app.main:app --reload
    ```

## 配置

配置通过 `config.ini` 文件进行管理。在运行应用程序之前，请确保将 `CONFIG_FILE_PATH` 环境变量设置为指向你的配置文件。

示例 `config.ini`：

```ini
[app]
project_name = 我的自定义 FastAPI 项目
api_version = /api/v1

[mysql]
host = 127.0.0.1
port = 3306
user = root
password =
database = fastapi_template

[redis]
host = localhost
port = 6379
password = root

[security]
secret_key = 你的自定义秘密密钥
access_token_expire_minutes = 60
```