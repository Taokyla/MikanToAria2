FROM python:3.9

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# 每3600秒(一小时)执行一次
CMD bash -c 'while true; do python /app/main.py; sleep 3600; done'
