FROM python:3.9.12

WORKDIR /app

COPY ./Login.py ./requirements.txt  /app/

COPY pages /app/pages

COPY sql_utils /app/sql_utils

COPY ./api_main.py /app/
COPY ./config.json /app/
COPY service_plans /app/

COPY cloudwatch /app/cloudwatch

COPY Authentication /app/Authentication

COPY ./lat_long.py ./meta.db ./nexrad.csv /app/

RUN pip install -r requirements.txt

EXPOSE 8091

CMD ["streamlit", "run", "Login.py","--server.port","8091"]