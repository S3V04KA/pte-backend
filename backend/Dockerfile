FROM python:3.11.8-alpine3.19
WORKDIR /backend
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY index.py .
ENTRYPOINT ["python", "index.py"]