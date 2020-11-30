FROM python:3.8-slim
WORKDIR /bot
COPY *.py ./
COPY requirements.txt .
RUN pip install -qr requirements.txt
ADD http://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh .
RUN chmod +x wait-for-it.sh