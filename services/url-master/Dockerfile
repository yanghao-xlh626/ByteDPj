
FROM library/python:3.9

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
# ENV PYTHONPATH=/app
# ENV FLASK_APP=src/app.py
# ENV FLASK_ENV=production

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

COPY src/ ./src/
COPY data/ ./data/

# CMD ["python","-u","./src/main.py"]
