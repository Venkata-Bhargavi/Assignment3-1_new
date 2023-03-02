# system imports
import sqlite3
import re

# import status as status
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel
from dotenv import load_dotenv
import streamlit as st
import boto3
import os
import botocore
import logging
import pandas as pd
# from sql_credentials import verify_password
import hashlib
import streamlit as st
from Authentication import authentication, auth_bearer
from Authentication.auth_bearer import JWTBearer
from Authentication.authentication import get_password_hash
from cloudwatch.logs import write_user_logs, write_Register_logs

# from utils_goes_API import goes_get_my_s3_url
# from utils_nexrad_API import nexrad_get_my_s3_url

load_dotenv()
app = FastAPI()
bearer_scheme = HTTPBearer()

#
# #custom imports
# from sql_goes import fetch_data_from_table_goes
# from sql_nexrad import  fetch_data_from_table_nexrad

if 'access_token' not in st.session_state:
    st.session_state.access_token = ""

database_file_name = "meta.db"
database_file_path = os.path.join(os.path.dirname(__file__), database_file_name)


def hash_text(text):
    # Convert the text to bytes using UTF-8 encoding
    text_bytes = text.encode('utf-8')

    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the text bytes
    sha256_hash.update(text_bytes)

    # Get the hexadecimal representation of the hash
    hex_digest = sha256_hash.hexdigest()

    # Return the hexadecimal hash digest
    return hex_digest


def verify_password1(db_password, given_password):
    flag = 0
    if str(hash_text(given_password)) == str(db_password):
        flag = 1
    return flag


# secret_key = "bullshit"
def goes_get_my_s3_url(filename):
    # print(dir_to_geos)
    print(filename)
    static_url = "https://damg7245-ass1.s3.amazonaws.com"
    filename_alone = filename.split("/")[-1]
    generated_url = f"{static_url}/{filename}"
    return generated_url


"""
return concatenated url of our s3 bucket
"""


def nexrad_get_my_s3_url(filename):
    static_url = "https://damg7245-ass1.s3.amazonaws.com"
    filename_alone = filename.split("/")[-1]
    generated_url = f"{static_url}/{filename}"
    return generated_url


@st.cache
def fetch_data_from_table_nexrad():
    conn = sqlite3.connect(database_file_path)
    df = pd.read_sql('SELECT * FROM nexrad', conn)
    logging.info("Data Loaded")
    return df


#
@st.cache
def fetch_data_from_table_goes():
    conn = sqlite3.connect(database_file_path)
    df = pd.read_sql('SELECT * FROM goes_meta', conn)
    return df


data_df_goes = fetch_data_from_table_goes()
data_df_nexrad = fetch_data_from_table_nexrad()

"""
Arguments : Directory of the bucket
returns : list of all files from the dir
"""


def get_files_from_noaa_bucket(dir):
    files_from_bucket = []
    s3_client = boto3.client("s3", region_name="us-east-1",
                             aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                             aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'))
    paginator = s3_client.get_paginator('list_objects_v2')
    noaa_bucket = paginator.paginate(Bucket="noaa-goes18", Prefix=dir)  # ,PaginationConfig  = {"PageSize":2}
    for count, page in enumerate(noaa_bucket):
        files = page.get("Contents")
        for file in files:
            files_from_bucket.append(file['Key'])
            # print(file['Key'])
            # f = open("output.txt", "a")
            # print(f"{file['Key']}",file = f)
    # print(files_from_bucket)
    return files_from_bucket


def get_files_from_nexrad_bucket(dir):
    files_from_nexrad_bucket = []
    s3_client = boto3.client("s3", region_name="us-east-1",
                             aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                             aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'))
    paginator = s3_client.get_paginator('list_objects_v2')
    nexrad_bucket = paginator.paginate(Bucket="noaa-nexrad-level2", Prefix=dir)  # ,PaginationConfig  = {"PageSize":2}
    for count, page in enumerate(nexrad_bucket):
        files = page.get("Contents")
        for file in files:
            files_from_nexrad_bucket.append(file['Key'])
            # print(file['Key'])
            # f = open("output1.txt", "a")?\
            # print(f"{file['Key']}",file = f)
    # print(files_from_nexrad_bucket)
    logging.info("Files extracted from Nexrad bucket")
    return files_from_nexrad_bucket


def copy_s3_file_if_exists(src_bucket_name, src_file_name, dst_bucket_name, dst_file_name):
    # session = boto3.Session(
    #     aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    #     aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
    # )
    session = boto3.Session(region_name="us-east-1",
                            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
                            )
    # print(os.environ.get('AWS_ACCESS_KEY'), "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    s3 = session.resource('s3')
    src_bucket = s3.Bucket(src_bucket_name)

    copy_source = {
        'Bucket': src_bucket_name,
        'Key': src_file_name
    }
    dst_bucket = s3.Bucket(dst_bucket_name)

    try:
        dst_bucket.Object(dst_file_name).load()
        # print(f"Object {dst_file_name} already exists in destination bucket {dst_bucket_name}.")
        # already copied so flag 1
        flag = 1
    except botocore.exceptions.ClientError as e:

        if e.response['Error']['Code'] == "404":
            # st.markdown(f"File NOT found in dst bucket {e.response['Error']['Code']}")
            dst_bucket.copy(copy_source, dst_file_name)
            print(
                f"Object {src_file_name} copied from source bucket {src_bucket_name} to destination bucket {dst_bucket_name}.")
            # now copied so flat = 1
            write_user_logs(
                f"Object {src_file_name} copied from source bucket {src_bucket_name} to destination bucket {dst_bucket_name}.")
            flag = 1
        else:
            st.error("No Such File")
            # so such file to copy , so flag =0
            flag = 0
    return flag


def copy_s3_file(src_bucket_name, src_file_name, dst_bucket_name, dst_file_name):
    session = boto3.Session(region_name="us-east-1",
                            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                            aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
                            )

    flag = 0

    s3 = session.resource('s3')
    src_bucket = s3.Bucket(src_bucket_name)

    try:
        src_bucket.Object(src_file_name).load()
        # st.markdown(f"Here {src_bucket.Object(src_file_name).load()}")
        flag = copy_s3_file_if_exists(src_bucket_name, src_file_name, dst_bucket_name, dst_file_name)
        # st.markdown(flag)
        return flag

    except botocore.exceptions.ClientError as e:
        st.markdown("EXCEPTION")
        if e.response['Error']['Code'] == "404":
            write_user_logs(f"File {src_file_name} not found in source bucket {src_bucket_name}.")
            st.error(f"File {src_file_name} not found in source bucket {src_bucket_name}.")
            # flag = 0
            return 0


class GoesUserInput(BaseModel):
    filename_with_dir: str


#

# selected_file is a full filename with dir structure
@app.post("/get_goes_url")
async def goes_copy_file_to_S3_and_return_my_s3_url_Api(selected_file: GoesUserInput,credentials: HTTPAuthorizationCredentials = Depends(
                                                              bearer_scheme)):
    if not JWTBearer.verify_jwt(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    else:
        my_s3_file_url = ""
        src_bucket = "noaa-goes18"
        des_bucket = "damg7245-ass1"

        dir_list = str(selected_file.filename_with_dir).split("/")

        if dir_list[1] not in data_df_goes.year.unique().tolist():
            raise HTTPException(status_code=400, detail="Selected Year out of range")
        elif dir_list[2] not in data_df_goes[(data_df_goes.year == dir_list[1])].day.unique().tolist():
            raise HTTPException(status_code=400, detail="Selected Day out of range")
        elif dir_list[3] not in data_df_goes[
            (data_df_goes.year == dir_list[1]) & (data_df_goes.day == dir_list[2])].hour.unique().tolist():
            raise HTTPException(status_code=400, detail="Selected Hour out of range")
        else:
            # copying user selected file from AWS s3 bucket to our bucket
            copied_flag = copy_s3_file(src_bucket, selected_file.filename_with_dir, des_bucket,
                                       selected_file.filename_with_dir)

        # print(f"{copied_flag} -- flag")
        # copying user selected file from AWS s3 bucket to our bucket
        # copied_flag = copy_s3_file(src_bucket, selected_file, des_bucket, selected_file)
        # getting url of user selected file from our s3 bucket
        if copied_flag:
            my_s3_file_url = goes_get_my_s3_url(selected_file.filename_with_dir)
        else:
            write_user_logs("File not found")
            raise HTTPException(status_code=404, detail="File not found")

        # return {'url': my_s3_file_url}
        return {'url': my_s3_file_url}


class NexradUserInput(BaseModel):
    filename_with_dir: str


#

@app.post("/get_nexrad_url")
async def nexrad_copy_file_to_S3_and_return_my_s3_url_API(selected_file: NexradUserInput,
                                                          credentials: HTTPAuthorizationCredentials = Depends(
                                                              bearer_scheme)):
    if not JWTBearer.verify_jwt(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    else:
        # else:
        src_bucket = "noaa-nexrad-level2"
        des_bucket = "damg7245-ass1"
        my_s3_file_url = ""

        dir_list = str(selected_file.filename_with_dir).split("/")

        if dir_list[0] not in data_df_nexrad.year.unique().tolist():
            raise HTTPException(status_code=400, detail="Selected Year out of range")
        elif dir_list[1] not in data_df_nexrad[(data_df_nexrad.year == dir_list[0])].month.unique().tolist():
            raise HTTPException(status_code=400, detail="Selected Month out of range")
        elif dir_list[2] not in data_df_nexrad[
            (data_df_nexrad.year == dir_list[0]) & (data_df_nexrad.month == dir_list[1])].day.unique().tolist():
            raise HTTPException(status_code=400, detail="Selected day out of 3range")
        elif dir_list[3] not in data_df_nexrad[
            (data_df_nexrad.year == dir_list[0]) & (data_df_nexrad.month == dir_list[1]) & (
                    data_df_nexrad.day == dir_list[2])].station.unique().tolist():
            raise HTTPException(status_code=404, detail="StationCode not found")
        else:
            # copying user selected file from AWS s3 bucket to our bucket
            copied_flag = copy_s3_file(src_bucket, selected_file.filename_with_dir, des_bucket,
                                       selected_file.filename_with_dir)

        print(f"{copied_flag} -- flag")
        # getting url of user selected file from our s3 bucket
        if copied_flag:
            my_s3_file_url = nexrad_get_my_s3_url(selected_file.filename_with_dir)
            return {'url': my_s3_file_url}
        else:
            # return {'url': ""}

            raise HTTPException(status_code=404, detail="File not found")


class GoesInputs(BaseModel):
    year: int
    day: str
    hour: str


"""
takes geos dir (only directory structure) as input and returns all the files in that dir as list
"""


# async def return_goes_files_list(dir_to_check_geos:GoesInputs, payload: str = Depends(JWTBearer.verify_jwt(st.session_state.access_token))):

@app.post("/get_goes_files")
async def return_goes_files_list(dir_to_check_geos: GoesInputs,
                                 credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not JWTBearer.verify_jwt(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    else:
        goes_files_list = []
        dir = f"ABI-L1b-RadC/{dir_to_check_geos.year}/{dir_to_check_geos.day}/{dir_to_check_geos.hour}"

        goes_files_list = get_files_from_noaa_bucket(dir)

        return {'files': goes_files_list}


class NexradInputs(BaseModel):
    year: int
    month: str
    day: str
    station_code: str


"""
takes nexrad dir as input and returns all the files in that dir as list 
"""


@app.post("/get_nexrad_files")
async def return_nexrad_files_list(dir_to_check_nexrad: NexradInputs,
                                   credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not JWTBearer.verify_jwt(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    else:
        noaa_files_list = []
        dir_to_check_nexrad = f"{dir_to_check_nexrad.year}/{dir_to_check_nexrad.month}/{dir_to_check_nexrad.day}/{dir_to_check_nexrad.station_code}"

        noaa_files_list = get_files_from_nexrad_bucket(dir_to_check_nexrad)

        return {'files': noaa_files_list}


def return_matched_password(db_password, hashed_password):
    flag = 0
    if db_password == hashed_password:
        flag = 1
    return flag


class CredInputs(BaseModel):
    un: str
    pwd: str


@app.post("/autheticate_user")
async def verify_user(credentials: CredInputs):
    # conn = sqlite3.connect('meta.db')
    # c = conn.cursor()
    # tableName = "registered_user"
    #
    # query = f"SELECT password, email FROM {tableName}  WHERE username = '{credentials.un}'"
    # p = c.execute(query)
    # db_pwd = p.fetchall()[0][0]
    # try:
    #     p = c.execute(query)
    #     db_pwd = p.fetchall()[0][0]
    #     email = p.fetchall()[0][1]
    #
    #     # if verify_password1(db_pwd, credentials.pwd) == "true":#verify_password(credentials.pwd, db_pwd):
    #         # return authentication.signJWT(credentials.email)
    #         # st.markdown(f"Credentials matched --> Access Token: {authentication.signJWT(email)}")
    #     return {"matched": verify_password1(db_pwd, credentials.pwd), 'access_token': authentication.signJWT(email)}
    #     # else:
    #     #     raise HTTPException(status_code=401, detail='Invalid username and/or password')
    #
    #     # return {"matched":verify_password(credentials.pwd, db_pwd), 'access_token': authentication.signJWT(Cred.email)}
    # except IndexError:
    #     return {"matched": 0, 'access_token': ""}

    conn = sqlite3.connect('meta.db')
    c = conn.cursor()

    query = f"SELECT password FROM registered_user  WHERE username = '{credentials.un}'"

    try:
        p = c.execute(query)
        db_pwd = p.fetchall()[0][0]

        # verify_password(credentials.pwd, db_pwd)
        if return_matched_password(db_pwd, hash_text(credentials.pwd)):
            # return authentication.signJWT(credentials.email)
            return {"matched": return_matched_password(db_pwd, hash_text(credentials.pwd)),
                    'access_token': authentication.signJWT(credentials.un)}
        else:
            # raise HTTPException(status_code=401, detail='Invalid username or password')
            return {"matched": return_matched_password(db_pwd, hash_text(credentials.pwd)), 'access_token': ""}

    except IndexError:
        return {"matched": 0, 'access_token': ""}


class RegisterInputs(BaseModel):
    email: str
    username: str
    password: str
    plan: str


"""
takes nexrad dir as input and returns all the files in that dir as list 
"""


@app.post("/register_new_user")
async def register_user(Cred: RegisterInputs):
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('meta.db')

    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    tableName = 'registered_user'

    # Define the SQL code to create a table
    create_table = f'''
    CREATE TABLE IF NOT EXISTS {tableName} (
        email TEXT NOT NULL UNIQUE,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        plan TEXT NOT NULL
    );
    '''

    # Execute the SQL code to create the table
    cursor.execute(create_table)

    # Define the SQL code to insert data into the table
    insert_data = f'''
    INSERT INTO {tableName} (email, username, password, plan)
    VALUES (?, ?, ?, ?);
    '''
    # Checking for username exists or not
    cursor.execute(f"SELECT COUNT(*) FROM {tableName} WHERE username = ?", (Cred.username,))
    count = cursor.fetchone()[0]

    # Hashing the password
    hashed_pwd = hash_text(Cred.password)

    if count == 0:
        cursor.execute(insert_data, (Cred.email, Cred.username, hashed_pwd, Cred.plan))
        conn.commit()
        conn.close()
        return "success"
    else:
        return "failed"


def check_username_doesnot_exists(username):
    conn = sqlite3.connect('meta.db')
    cursor = conn.cursor()
    tableName = 'registered_user'

    cursor.execute(f"SELECT COUNT(*) FROM {tableName} WHERE username = ?", (username,))
    count = cursor.fetchone()[0]

    if count == 0:
        return "success"
    else:
        return "failed"
