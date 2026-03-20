FROM registry.access.redhat.com/ubi9/python-311

# Switch to Root to update 
USER 0

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python3", "main.py"]
