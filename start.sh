source .venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > output.log 2>&1 &
ps -ef|grep uvicorn