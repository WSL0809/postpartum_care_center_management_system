#拉取 python3.10 的基础镜像
FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip --no-cache && \
    pip install -r requirements.txt
