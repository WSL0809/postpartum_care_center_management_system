#拉取 python3.10 的基础镜像
FROM python:3.10
WORKDIR /app
COPY . /app
COPY api /app/api
COPY schema /app/schema
COPY crud /app/crud
COPY models /app/models
COPY main.py /app
COPY requirements.txt /app
COPY .env /app
COPY utils.py /app
COPY database.py /app
COPY auth_schema.py /app
COPY auth.py /app
COPY config.py /app
RUN pip install --upgrade pip --no-cache && \
    pip install --no-cache -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2"]
