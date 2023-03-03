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


def fetch_register_logs_for_5_days():
    # Define start and end time for query
    end_time = int(datetime.datetime.now().timestamp()) * 1000
    start_time = int((datetime.datetime.now() - datetime.timedelta(days=5)).timestamp()) * 1000

    # Fetch logs for last 5 days
    response = client_logs.get_log_events(
        logGroupName='data_explorer',  # Replace with your log group name
        logStreamName="register_user_logs",
        startTime=start_time,
        endTime=end_time
    )


    # Extract the timestamp and message from each log event
    timestamps = []
    messages = []
    for event in response['events']:
        timestamps.append(event['timestamp'])
        messages.append(event['message'])
    st.markdown(response['events'])
    st.markdown(messages[0:2])
    # Split each message into its components and store them in a DataFrame
    df = pd.DataFrame([m.split('///') for m in messages], columns=['email', 'username', 'password', 'plan'])
    df['timestamp'] = pd.to_datetime(timestamps, unit='ms')
    return df

def fetch_api_usage_logs_for_5_days():
    # Define start and end time for query
    end_time = int(datetime.datetime.now().timestamp()) * 1000
    start_time = int((datetime.datetime.now() - datetime.timedelta(days=5)).timestamp()) * 1000

    # Fetch logs for last 5 days
    response = client_logs.get_log_events(
        logGroupName='data_explorer',  # Replace with your log group name
        logStreamName="user_api_usage",
        startTime=start_time,
        endTime=end_time
    )

    timestamps = []
    messages = []
    for event in response['events']:
        timestamps.append(event['timestamp'])
        messages.append(event['message'])

    # Split each message into its components and store them in a DataFrame
    df = pd.DataFrame([m.split('///') for m in messages], columns=['username', 'endpoint', 'status'])
    df['timestamp'] = pd.to_datetime(timestamps, unit='ms')
    return df

def fetch_logs_for_5_days():
    # Define start and end time for query
    end_time = int(datetime.datetime.now().timestamp()) * 1000
    start_time = int((datetime.datetime.now() - datetime.timedelta(days=5)).timestamp()) * 1000

    # Fetch logs for last 5 days
    response = client_logs.get_log_events(
        logGroupName='data_explorer',  # Replace with your log group name
        logStreamName="loggedin_user_logs",
        startTime=start_time,
        endTime=end_time
    )
    #
    # # Print each log message
    # for event in response['events']:
    #     print(event['message'])


    # Extract the timestamp and message from each log event
    timestamps = []
    messages = []
    for event in response['events']:
        timestamps.append(event['timestamp'])
        messages.append(event['message'])

    # Split each message into its components and store them in a DataFrame
    df = pd.DataFrame([m.split('///') for m in messages], columns=['username', 'endpoint', 'status'])
    df['timestamp'] = pd.to_datetime(timestamps, unit='ms')
    return df


def fetch_api_success_logs_for_5_days():
    # Define start and end time for query
    end_time = int(datetime.datetime.now().timestamp()) * 1000
    start_time = int((datetime.datetime.now() - datetime.timedelta(days=5)).timestamp()) * 1000

    # Fetch logs for last 5 days
    response = client_logs.get_log_events(
        logGroupName='data_explorer',  # Replace with your log group name
        logStreamName="api_success_logs",
        startTime=start_time,
        endTime=end_time
    )
    #
    # # Print each log message
    # for event in response['events']:
    #     print(event['message'])


    # Extract the timestamp and message from each log event
    timestamps = []
    messages = []
    for event in response['events']:
        timestamps.append(event['timestamp'])
        messages.append(event['message'])

    # Split each message into its components and store them in a DataFrame
    df = pd.DataFrame([m.split('///') for m in messages], columns=['username', 'endpoint', 'status', 'code'])
    df['timestamp'] = pd.to_datetime(timestamps, unit='ms')
    return df


def fetch_api_failed_logs_for_5_days():
    # Define start and end time for query
    end_time = int(datetime.datetime.now().timestamp()) * 1000
    start_time = int((datetime.datetime.now() - datetime.timedelta(days=5)).timestamp()) * 1000

    # Fetch logs for last 5 days
    response = client_logs.get_log_events(
        logGroupName='data_explorer',  # Replace with your log group name
        logStreamName="api_failure_logs",
        startTime=start_time,
        endTime=end_time
    )
    #
    # # Print each log message
    # for event in response['events']:
    #     print(event['message'])

    # Extract the timestamp and message from each log event
    timestamps = []
    messages = []
    for event in response['events']:
        timestamps.append(event['timestamp'])
        messages.append(event['message'])

    # Split each message into its components and store them in a DataFrame
    df = pd.DataFrame([m.split('///') for m in messages], columns=['username', 'endpoint', 'status', 'code'])
    df['timestamp'] = pd.to_datetime(timestamps, unit='ms')
    return df

def write_user_api_usage (username,endpoint,status):
    client_logs.put_log_events(
    logGroupName="data_explorer",
    logStreamName="user_api_usage",
    logEvents=[{
        'timestamp': int(datetime.datetime.now().timestamp() * 1000),#int(datetime.time.time() * 1e3),
        'message':f"{username}///{endpoint}///{status}"
    }])


def write_api_success_or_failure_logs (logstreamname,username,endpoint,status,code):
    client_logs.put_log_events(
    logGroupName="data_explorer",
    logStreamName=logstreamname,
    logEvents=[{
        'timestamp': int(datetime.datetime.now().timestamp() * 1000),
        'message': f"{username}///{endpoint}///{status}///{code}"

    }])



def write_register_user_logs(email, username, password, plan):
    client_logs.put_log_events(
    logGroupName="data_explorer",
    logStreamName="register_user_logs",
    logEvents=[{
        'timestamp': int(datetime.datetime.now().timestamp() * 1000),  # int(datetime.time.time() * 1e3),
        'message': f"{email}///{username}///{password}///{plan}"
    }])

def write_loggedin_user_logs(username,password,plan):
    client_logs.put_log_events(
        logGroupName="data_explorer",
        logStreamName="loggedin_user_logs",
        logEvents=[{
            'timestamp': int(datetime.datetime.now().timestamp() * 1000),  # int(datetime.time.time() * 1e3),
            'message': f"{username}///{password}///{plan}"
        }])



#-----------------------------------reading logs--------------------------


def read_user_api_usage_logs():

    # Specify the log group and log stream names
    log_group_name = 'data_explorer'
    log_stream_name = 'user_api_usage'

    # Call get_log_events to retrieve all log events from the log stream
    response = client_logs.get_log_events(
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
    df = pd.DataFrame([m.split('///') for m in messages], columns=['username', 'endpoint', 'status'])
    df['timestamp'] = pd.to_datetime(timestamps, unit='ms')
    return df




def read_register_user_logs():

    log_group_name = 'data_explorer'
    log_stream_name = 'register_user_logs'
    # Set start time to the beginning of the log stream

    # Initialize an empty list to store log events
    # Call get_log_events to retrieve all log events from the log stream
    response = client_logs.get_log_events(
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
    df = pd.DataFrame([m.split('///') for m in messages], columns=['email', 'username', 'password','plan'])
    df['timestamp'] = pd.to_datetime(timestamps, unit='ms')
    return df


if __name__ == "__main__":
    print(read_register_user_logs())