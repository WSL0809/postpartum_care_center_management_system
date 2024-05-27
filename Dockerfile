##拉取 python3.10 的基础镜像
#FROM python:3.10
#
#WORKDIR /app
#
#COPY . /app
#
#RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
#    pip install --upgrade pip --no-cache && \
#    pip install --no-cache -r requirements.txt
#
#EXPOSE 80
#
#CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "20245", "--workers", "4"]

FROM python:3.10-slim AS builder

WORKDIR /app

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .
