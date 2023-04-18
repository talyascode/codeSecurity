FROM python:3.8

WORKDIR /

ENV FILE=sql_server_fixed.py
ENV PORT=5000

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install requests
RUN pip install CORS
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

COPY code_files.zip .

RUN apt-get install -y unzip && \
    unzip code_files.zip

ENTRYPOINT python ${FILE} ${PORT} --database "sqlite:///data.db"

