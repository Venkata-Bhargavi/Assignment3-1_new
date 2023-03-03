FROM python:3.9.12
# Base docker image of python 3.x

RUN pip install --upgrade pip
# Upgrade pip package

WORKDIR /app
# Change working dir to app
COPY Authentication /app/Authetication

COPY cloudwatch /app/cloudwatch
COPY ./requirements.txt ./meta.db ../api_main.py /app/
COPY ./config.json /app/

#COPY ../sql_util /app/sql_util

# COPY pages /app/pages
# Copy the necessary files from one level up into the app directory inside the container

RUN pip install -r requirements.txt
# Install the required dependencies

EXPOSE 8000
# Expose a port inside the container on which services run

#CMD ["uvicorn","API:app","--host","0.0.0.0"]
# Start the FastAPI server with Gunicorn
CMD ["gunicorn" ,"-w", "4", "-k", "uvicorn.workers.UvicornWorker" , "--bind", "0.0.0.0:8000", "api_main:app"]

#CMD ["uvicorn", "API:app", "--host", "0.0.0.0", "--port", "8091"]