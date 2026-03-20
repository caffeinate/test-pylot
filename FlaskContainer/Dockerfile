FROM ubuntu:latest
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --break-system-packages -r requirements.txt
EXPOSE 5000
CMD ["python3", "main.py"]
