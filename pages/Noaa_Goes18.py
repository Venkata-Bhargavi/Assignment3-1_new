import logging

import streamlit as st
import os
import json
import requests

from Authentication.auth_bearer import JWTBearer
from cloudwatch.logs import write_user_logs, write_api_success_or_failure_logs
# from cloudwatch.logs import write_logs, write_api_success_or_failure_logs
from utils_goes_API import get_dir_from_filename_geos
from sql_utils.sql_goes import fetch_data_from_table_goes

# from aws_geos import get_dir_from_filename_geos

path = os.path.dirname(__file__)
from dotenv import load_dotenv

logout_btn = False


load_dotenv()
with open('config.json', 'r') as f:
    config = json.load(f)

get_goes_files_url = config['endpoints']['get_goes_files']
get_goes_url_url = config['endpoints']['get_goes_url']
data_df = fetch_data_from_table_goes()

# """
# returns values from df of selected column
# """


if 'login_status' not in st.session_state:
    st.session_state.login_status = False

if 'login_btn' not in st.session_state:
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

if 'logout_btn' not in st.session_state:
    st.session_state.logout_btn = False
if 'active_user' not in st.session_state:
    st.session_state.active_user = ""

if 'access_token' not in st.session_state:
    st.session_state.access_token = ""


st.markdown(f"Access Token: {st.session_state.access_token}")

st.markdown(f"Payload for token: {JWTBearer.verify_jwt(st.session_state.access_token)}")

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

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


selected_year_geos = ""
selected_day_geos = ""
selected_hour_geos = ""
def goes_enabled():

    #creating columns to show year, day, hour to user to select
    year,day,hour = st.columns([1,1,1])

    with year:
        yl = data_df.year.unique().tolist()
        yl.insert(0, "Select Year")
        year = st.selectbox('Year', yl)
        # year = st.selectbox('Year', range(2020, 2023))
        selected_year_geos = year
    days_of_selected_year = extract_values_from_df(data_df[data_df.year==selected_year_geos],"year",selected_year_geos,"day")

    with day:
        dsyl = days_of_selected_year
        dsyl.insert(0, "Select Day")
        day = st.selectbox('Day',dsyl)
        selected_day_geos = day
    hours_of_selected_day = extract_values_from_df(data_df[(data_df.year==selected_year_geos) & (data_df.day==selected_day_geos)],"day",selected_day_geos,"hour")

    with hour:
        hsdl = hours_of_selected_day
        hsdl.insert(0,"Select Hour")
        hour = st.selectbox("Hour",hsdl)
        selected_hour_geos = hour




    #
    #
    #     # """
    #     # takes geos dir as input and returns all the files in that dir as list
    #     # """
    # def return_list(dir_to_check_geos):
    #     noaa_files_list = []
    #
    #     noaa_files_list = get_files_from_noaa_bucket(dir_to_check_geos)
    #
    #     return noaa_files_list
    #
    #



    #creating dir based on user input
    dir_to_check_geos = ""
    selected_file = ""

    if (selected_hour_geos != "Select Hour") and (selected_day_geos != "Select Day") and (selected_year_geos != "Select Year"):
        dir_to_check_geos = f"ABI-L1b-RadC/{selected_year_geos}/{selected_day_geos}/{selected_hour_geos}"
        # Takes list of files from user selected directory and showing them in selectbox
        # noaa_files_list = return_list(dir_to_check_geos) if dir_to_check_geos != "" else []




        # url = 'http://api:8000/get_goes_files'
        url = get_goes_files_url
        data = {
            "year": int(selected_year_geos),
            "day": selected_day_geos,
            "hour": selected_hour_geos
        }
        # write_logs(f"accessed {url}")
        response = requests.post(url=url, json=data, headers =headers)
        files_list = response.json().get('files')

        # response = requests.post(url, data = dir_to_check_geos)
        # files_from_api = response.json()
        # st.markdown(files_from_api['files'])
        selected_file = st.selectbox("Select a file", files_list)
        write_user_logs(f"{st.session_state.active_user}///{get_goes_files_url}///success")
        write_api_success_or_failure_logs("api_success_logs", st.session_state.active_user, get_goes_files_url,
                                          "success", response.status_code)

    else:
        st.error("Please select all fields")


    # st.markdown(dir_to_check_geos)


    fetching, image = st.columns([3, 1])





    # #retrieving url from AWS s3 bucket for selected file
    # geos_file_url = get_noaa_geos_url(f"{dir_to_check_geos}/{selected_file}")


    get_url_btn = st.button("Get Url")
    my_s3_file_url = ""







    #using user inputs
    if get_url_btn:
        if ((selected_hour_geos != "Select Hour") and (selected_day_geos != "Select Day") and (selected_year_geos != "Select Year")):
            # get_goes_url = 'http://api:8000/get_goes_url'
            get_goes_url = get_goes_url_url

            goes_data = {
                "filename_with_dir":selected_file
            }
            # write_logs(f"accessed {get_goes_url}")

            jwt_token = "myjwttoken"
            tk = st.session_state.access_token
            headers1 = {"Authorization": f"Bearer {tk}"}
            response = requests.post(url=get_goes_url, json=goes_data, headers=headers1)
            my_s3_file_url = response.json().get('url')

            # my_s3_file_url = asyncio.run(goes_copy_file_to_S3_and_return_my_s3_url_Api(selected_file))  #-----for API--------

            if my_s3_file_url != "":
                st.success(f"Download link has been generated!\n [URL]({my_s3_file_url})")
                with st.expander("Expand for URL"):
                    text2 = f"<p style='font-size: 20px; text-align: center'><span style='color: #15b090; font-weight:bold ;'>{my_s3_file_url}</span></p>"
                    st.markdown(f"[{text2}]({my_s3_file_url})", unsafe_allow_html=True)
                    write_user_logs(f"{st.session_state.active_user}///{get_goes_url_url}///success")
                    write_api_success_or_failure_logs("api_success_logs", st.session_state.active_user,
                                                      get_goes_url_url,
                                                      "success", response.status_code)
            else:
                # logging.DEBUG("File not found in NOAA database")
                st.error("File not found in NOAA database, Please enter a valid filename!")
        else:
            st.error("Please select all fields!")




    st.markdown("----------------------------------------------------------------------------------------------------")
    st.markdown("<h2 style='text-align: center'>Download Using FileName</h2>",unsafe_allow_html=True)
    given_file_name = st.text_input("Enter File Name")
    button_url = st.button("Get url")

    #usign filename
    if button_url:
        get_goes_url = get_goes_url_url
        if given_file_name != "":
            full_file_name = get_dir_from_filename_geos(given_file_name)
            if full_file_name != "":
                # get_goes_url = 'http://api:8000/get_goes_url'


                data = {
                    "filename_with_dir": full_file_name
                }
                # write_logs(f"accessed {get_goes_url}")
                tk1 = st.session_state.access_token
                headers2 = {"Authorization": f"Bearer {tk1}"}
                response = requests.post(url=get_goes_url, json=data, headers =headers2)
                my_s3_file_url = response.json().get('url')
                    # displaying url through expander
                if response.status_code == 200 and my_s3_file_url != "":
                    st.success(f"Download link has been generated!\n [URL]({my_s3_file_url})")
                    with st.expander("Expand for URL"):
                        text2 = f"<p style='font-size: 20px; text-align: center'><span style='color: #15b090; font-weight:bold ;'>{my_s3_file_url}</span></p>"
                        st.markdown(f"[{text2}]({my_s3_file_url})", unsafe_allow_html=True)
#-------------------------------write_logs-----------------------------
                        write_user_logs(f"{st.session_state.active_user}///{get_goes_url_url}///success")
                        write_api_success_or_failure_logs("api_success_logs", st.session_state.active_user,
                                                          get_goes_url_url,
                                                          "success", response.status_code)
                else:

                    st.error("File not found in NOAA database, Please enter a valid filename!")

            else:
                st.error("File not found in NOAA database, Please enter a valid filename")
        else:
            st.error("Please Enter a file name")

if st.session_state["authenticated"] == True:

    c1, c2, c3, c4, c5 = st.columns(5)

    with c5:
        logout_btn = st.button("Logout!")

    st.markdown("<h1 style='text-align: center'>Data Explorator - GOES</h1>", unsafe_allow_html=True)

    # c1, c2, c3, c4, c5 = st.columns(5)
    # with c5:

    goes_enabled()
else:
    st.error("Please login to access session")



# if logout_btn:
#     st.session_state.authenticated = False
#     st.success("User Logged-OUT")
#     home_page_layout(st.session_state.authenticated)



if logout_btn:
    st.session_state.authenticated = False
    st.session_state.access_token = ""
    st.success("User Logged-OUT")

    # home_page_layout(st.session_state.authenticated)
