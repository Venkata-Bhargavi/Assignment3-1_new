import pandas as pd
import os
import json
import requests
import streamlit as st
import logging
import folium
from cloudwatch.logs import *
from sql_utils.sql_nexrad import fetch_data_from_table_nexrad
from streamlit_folium import folium_static
from utils_nexrad_API import get_dir_from_filename_nexrad
from datetime import datetime, timedelta
from Authentication.utils import check_user_usage_limit_within_lasthour


path = os.path.dirname(__file__)
from dotenv import load_dotenv

load_dotenv()

logout_btn = False
with open('config.json', 'r') as f:
    config = json.load(f)

get_nexrad_files_url = config['endpoints']['get_nexrad_files']
get_nexrad_url_url = config['endpoints']['get_nexrad_url']


# st.markdown("Checking api df")



    # st.markdown(f"{api_usage_df.shape}")
# api_usage_df.endpoint

if 'login_status' not in st.session_state:
    st.session_state.login_status = False

if 'login_submit' not in st.session_state:
    st.session_state.login_submit = False

if 'logout_submit' not in st.session_state:
    st.session_state.logout_submit = True

if 'username' not in st.session_state:
    st.session_state.username = False

if 'password' not in st.session_state:
    st.session_state.password = False

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'valid_user_flag' not in st.session_state:
    st.session_state.valid_user_flag = False

if 'login_btn' not in st.session_state:
    st.session_state.login_btn = False


if 'logout_btn' not in st.session_state:
    st.session_state.logout_btn = False

if 'active_user' not in st.session_state:
    st.session_state.active_user = ""

if 'access_token' not in st.session_state:
    st.session_state.access_token = ""

if 'user_plan' not in st.session_state:
    st.session_state.user_plan = ""

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}


# Triggers limit and nex rad url
if st.session_state.authenticated == True:
    max_triggers = config['plans'][f"{st.session_state.user_plan}"]
    user_triggers = check_user_usage_limit_within_lasthour(st.session_state.active_user, get_nexrad_url_url)


# """
# returns values from df of selected column
# """

def extract_values_from_df(df, key, value, col):
    # Extract the rows where key is equal to value
    filtered_df = df[df[key] == value]

    # Return all the values from the specified column
    return filtered_df[col].unique().tolist()

def load_lottiefile(filepath:str):
    with open(filepath,"r") as f:
        return json.load(f)
def load_lottieurl(url:str):
    r = requests.get(url)
    if r.status_code !=200:
        return None
    return r.json()

lottie_satellite = "https://assets3.lottiefiles.com/private_files/lf30_cmdcmgh0.json"

# with st.sidebar:
#     lottie_pro = load_lottieurl(f"{lottie_satellite}")
#     st_lottie(
#         lottie_pro,
#         speed=1,
#         reverse=False,
#         loop=True,
#         height="450px",
#         width=None,
#         key=None,
#     )

selected_year_nexrad = ""
selected_month_nexrad = ""
selected_day_nexrad = ""
selected_station_nexrad = ""

def nexrad_enabled():


    #creating columns to show year, day, hour to user to select
    year, month, day, station_code = st.columns([1, 1, 1, 1])

    data_df = fetch_data_from_table_nexrad()

    with year:
        yl = data_df.year.unique().tolist()
        yl.insert(0, "Select Year")
        year = st.selectbox('Year', yl)
        selected_year_nexrad = year
    month_of_selected_year = extract_values_from_df(data_df[data_df.year==selected_year_nexrad], "year", selected_year_nexrad, "month")
    with month:
        msyl = month_of_selected_year
        msyl.insert(0, "Select Month")
        month = st.selectbox('Month', msyl)
        selected_month_nexrad = month
    day_of_selected_month = extract_values_from_df(data_df[(data_df.year==selected_year_nexrad) & (data_df.month==selected_month_nexrad)], "month", selected_month_nexrad, "day")

    with day:
        dsml = day_of_selected_month
        dsml.insert(0, "Select Day")
        day = st.selectbox("Day", dsml)
        selected_day_nexrad = day
    station_code_of_selected_hour = extract_values_from_df(data_df[(data_df.year==selected_year_nexrad) & (data_df.month==selected_month_nexrad) & (data_df.day==selected_day_nexrad)],"day", selected_day_nexrad, "station")

    with station_code:
        scshl = station_code_of_selected_hour
        scshl.insert(0,"Select station")
        station = st.selectbox("Station Code",scshl)
        selected_station_nexrad = station

    # Files pulling

    # if st.button("Retreive"):
    dir_to_check_nexrad = ""
    if ((selected_year_nexrad != "Select Year") and (selected_month_nexrad != "Select Month") and (
            selected_day_nexrad != "Select Day") and (selected_station_nexrad != "Select station")):

            # url = 'http://api:8000/get_nexrad_files'
            url = get_nexrad_files_url

            data = {
                "year": int(selected_year_nexrad),
                "month": selected_month_nexrad,
                "day":selected_day_nexrad,
                "station_code":selected_station_nexrad
            }
            # write_logs(f"accessed {url}")
            response = requests.post(url=url, json=data, headers =headers)
            noaa_files_list = response.json().get('files')

            # response = requests.post(url, data = dir_to_check_geos)
            # files_from_api = response.json()
            # st.markdown(files_from_api['files'])
            selected_file = st.selectbox("Select a file", noaa_files_list)
            #--------------------------writing_logs--------------------------------------
            write_user_api_usage(st.session_state.active_user,get_nexrad_files_url,"success")
            write_api_success_or_failure_logs("api_success_logs",st.session_state.active_user,get_nexrad_files_url,"success",response.status_code)
    else:
        st.error("Please select all fields")




    get_url_btn = st.button("Get Url")
    my_s3_file_url = ""

    # URL Generating

    #through user dropdown inputs
    if get_url_btn:
        get_nexrad_url = get_nexrad_url_url
        if((selected_year_nexrad != "Select Year") and (selected_month_nexrad != "Select Month") and (selected_day_nexrad != "Select Day") and (selected_station_nexrad != "Select station")):
            if (int(user_triggers) < max_triggers):
                nexrad_data = {
                    "filename_with_dir": selected_file
                }
                # write_logs(f"accessed {get_nexrad_url}")
                num_retries = 3
                tk = st.session_state.access_token
                headers1 = {"Authorization": f"Bearer {tk}"}
                for i in range(num_retries):
                    response = requests.post(url=get_nexrad_url, json=nexrad_data, headers =headers1)
                    my_s3_file_url = response.json().get('url')
                    if my_s3_file_url != "":
                        break

                if my_s3_file_url != "":
                    # write_api_success_or_failure_logs("api_success_logs", st.session_state.active_user, get_nexrad_url, "success", response.status_code)
                    st.success(f"Download link has been generated!\n [URL]({my_s3_file_url})")
                    with st.expander("Expand for URL"):
                        text2 = f"<p style='font-size: 20px; text-align: center'><span style='color: #15b090; font-weight:bold ;'>{my_s3_file_url}</span></p>"
                        st.markdown(f"[{text2}]({my_s3_file_url})", unsafe_allow_html=True)
                        logging.info("URL has been generated")
                        #-----------------------writing_logs-----------------------------
                        write_user_api_usage(st.session_state.active_user,get_nexrad_url_url,"success")
                        write_api_success_or_failure_logs("api_success_logs", st.session_state.active_user,
                                                          get_nexrad_url, "success", response.status_code)

                else:
                    st.error("File not found in NEXRAD Dataset, Please enter a valid filename")
            else:
                st.error("Usage Limit Exceeded")

        else:
            st.error("Please select all fields!")




    st.markdown("----------------------------------------------------------------------------------------------------")
    st.markdown("<h2 style='text-align: center'>Download Using FileName</h2>",unsafe_allow_html=True)
    given_file_name = st.text_input("Enter File Name")
    button_url = st.button("Get url")


    # through file input
    if button_url:

        get_nexrad_url = get_nexrad_url_url

        if (int(user_triggers) < max_triggers):
            if given_file_name != "":
                src_bucket = "noaa-nexrad-level2"
                des_bucket = "damg7245-ass1"

                #generating filename with dir structure
                full_file_name = get_dir_from_filename_nexrad(given_file_name)

                # get_nexrad_url = 'http://api:8000/get_nexrad_url'
                get_nexrad_url = get_nexrad_url_url

                nexrad_data = {
                    "filename_with_dir": full_file_name
                }
                # write_logs(f"accessed {get_nexrad_url}")
                tk2 = st.session_state.access_token
                headers2 = {"Authorization": f"Bearer {tk2}"}
                response = requests.post(url=get_nexrad_url, json=nexrad_data, headers =headers2)
                # try:
                my_s3_file_url = response.json().get('url')
                st.markdown(my_s3_file_url)
                # except json.JSONDecodeError as e:
                #     st.error(f"Error decoding JSON:, {e}")
                # except Exception as e:
                #     st.error(f"Error:, {e}")

                # st.markdown(my_s3_file_url)

                if my_s3_file_url != None:  #checks if the file url is not empty
                    st.success(f"Download link has been generated!\n [URL]({my_s3_file_url})")
                    logging.info("Download link generated")

                    # displaying url through expander
                    with st.expander("Expand for URL"):
                        text2 = f"<p style='font-size: 20px; text-align: center'><span style='color: #15b090; font-weight:bold ;'>{my_s3_file_url}</span></p>"
                        st.markdown(f"[{text2}]({my_s3_file_url})", unsafe_allow_html=True)

                        logging.info("URL has been generated")
                        write_user_api_usage(st.session_state.active_user,get_nexrad_url_url,"success")
                        write_api_success_or_failure_logs("api_success_logs", st.session_state.active_user,
                                                          get_nexrad_url, "success", response.status_code)
                else:
                    st.error("File not found in NEXRAD Dataset, Please enter a valid filename")

            else:
                st.error("Please Enter a file name")
        else:
            st.error("Usage Limit Exceeded")



    DATA_URL = ('nexrad.csv')
    @st.cache(persist=True)
    def load_data(nrows):
        data = pd.read_csv(DATA_URL, nrows=nrows)
        # lowercase = lambda x:str(x).lower()
        return data
    data = load_data(10000)
    df = pd.DataFrame({'name': data['NAME'],'lat': data['LAT'],'lon':data['LON']})

    m = folium.Map(location=[20,0], tiles="OpenStreetMap", zoom_start=2)
    # st.map(df)
    for i in range(0,len(data)):
       folium.Marker(
          location=[df.iloc[i]['lat'], df.iloc[i]['lon']],
          popup=df.iloc[i]['name'],
       ).add_to(m)
    # st.markdown()
    folium_static(m)


if st.session_state["authenticated"] == True:

    c1, c2, c3, c4, c5 = st.columns(5)
    with c5:
        logout_btn = st.button("Logout!")

    st.markdown("<h1 style='text-align: center'>Data Explorator - NEXRAD</h1>", unsafe_allow_html=True)

    nexrad_enabled()
else:
    st.error("Please login through login page to view session ")


if logout_btn:
    active_user = ""
    st.session_state.valid_user_flag = 0
    st.session_state.authenticated = False
    st.session_state.access_token = ""
    st.session_state.user_plan = ""
    st.session_state.active_user = ""
    st.success("User Logged-OUT")
    # home_page_layout(st.session_state.authenticated)


# if logout_btn:
#     st.session_state.authenticated = False
#     st.success("User Logged-OUT")
#     home_page_layout(st.session_state.authenticated)
