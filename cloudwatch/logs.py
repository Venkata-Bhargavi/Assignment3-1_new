import datetime
import pandas as pd
import boto3
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
client_logs = boto3.client('logs',region_name="us-east-1",
        aws_access_key_id=os.environ.get("LOGS_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("LOGS_SECRET_KEY"))



def write_user_logs (message: str):
    client_logs.put_log_events(
    logGroupName="data_explorer",
    logStreamName="user_api_usage",
    logEvents=[{
        'timestamp': int(datetime.datetime.now().timestamp() * 1000),#int(datetime.time.time() * 1e3),
        'message': message
    }])


def write_api_success_or_failure_logs (logstreamname,username,endpoint,status,code):
    client_logs.put_log_events(
    logGroupName="data_explorer",
    logStreamName=logstreamname,
    logEvents=[{
        'timestamp': int(datetime.datetime.now().timestamp() * 1000),
        'message': f"{username}///{endpoint}///{status}///{code}"

    }])



def write_Register_logs(email, username,password, plan):
    st.markdown("Registered!")
    client_logs.put_log_events(
    logGroupName="data_as_a_service",
    logStreamName="user_register_logs",
    logEvents=[{
        'timestamp': int(datetime.datetime.now().timestamp() * 1000),  # int(datetime.time.time() * 1e3),
        'message': f"{username}///{password}///{email}///{plan}"
    }])


def read_user_registered_logs():
    client = boto3.client('logs', region_name="us-east-1",
                               aws_access_key_id=os.environ.get('LOGS_ACCESS_KEY'),
                               aws_secret_access_key=os.environ.get('LOGS_SECRET_KEY'))

    # Specify the log group and log stream names
    log_group_name = 'data_as_a_service'
    log_stream_name = 'user_register_logs'

    # Call get_log_events to retrieve all log events from the log stream
    response = client.get_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
    )


    # Extract the timestamp and message from each log event
    timestamps = []
    messages = []
    for event in response['events']:
        timestamps.append(event['timestamp'])
        messages.append(event['message'])

    # Split each message into its components and store them in a DataFrame
    df = pd.DataFrame([m.split('///') for m in messages], columns=['username', 'password', 'email', 'plan'])
    df['timestamp'] = pd.to_datetime(timestamps, unit='ms')
    return df

if __name__ == "__main__":
    print(write_user_logs("sdf"))