import re

import streamlit as st
import json
import requests

from API import check_username_doesnot_exists
from Authentication.authentication import get_password_hash
from cloudwatch.logs import write_Register_logs

# from cloudwatch.logs import write_user_logs, write_Register_logs

# import components.authenticate as authenticate

logout_btn = False
valid_user_flag = 0
placeholder = st.empty()
placeholder_logout = st.empty()


st.markdown(
        "<h3 style='text-align: center'><span style='color: #2A76BE;'>Welcome to Data Exploration Application</span></h3>",
        unsafe_allow_html=True)
st.markdown(
        "<h5 style='text-align: center'>One stop to leverage data from NOAA Satellite and radars for analysis and extract insights.</h5>",
        unsafe_allow_html=True)

# from pages.Nexrad import nexrad_home
# from streamlit_extras.switch_page_button import switch_page


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

if 'logout_btn' not in st.session_state:
    st.session_state.logout_btn = False



valid_user_flag = False

def validate_user_credentials(username, password):

    # url = 'http://api:8000/autheticate_user'
    url = "http://127.0.0.1:8001/autheticate_user"
    data = {
        "un": username,
        "pwd": password
    }
    response = requests.post(url=url, json=data)
    valid_user_flag = response.json().get('matched')
    return valid_user_flag

# def registerUserCredentials(email, username, password, plan):
#
#     # url = 'http://api:8000/autheticate_user'
#     url = "http://localhost:8000/register_user"
#     data = {
#         'email': email,
#         "un": username,
#         "pwd": password,
#         'plan': plan
#     }
#     response = requests.post(url=url, json=data)
#     valid_user_flag = response.json().get('matched')
#     return valid_user_flag

# def register_user_cred(email, un, pwd, plan):
#     conn = sqlite3.connect('meta.db')
#     c = conn.cursor()
#
#     query = f"INSERT INTO new_user ('email', 'username', 'password', 'plan') VALUES ({email}, {un}, {pwd}, {plan})"
#     try:
#         c.execute(query)
#         c.commit()
#         c.close()
#         # db_pwd = p.fetchall()[0][0]
#         write_Register_logs(email,un, pwd, plan)
#         # write_logs(f"credentials : {verify_password(db_pwd, credentials.pwd)}")
#         # return {"matched":verify_password(db_pwd, credentials.pwd)}
#         return 1
#     except IndexError:
#         return 0


###################################################################################
# Login Form



def home_introduction():
    def load_lottiefile(filepath:str):
        with open(filepath,"r") as f:
            return json.load(f)
    def load_lottieurl(url:str):
        r = requests.get(url)
        if r.status_code !=200:
            return None
        return r.json()
    lottie_satellite = "https://assets3.lottiefiles.com/private_files/lf30_cmdcmgh0.json"
    st.markdown("")
    st.markdown("The 2 datasets available are: <span style='color: #2A76BE;'>[GOES](https://noaa-goes18.s3.amazonaws.com/index.html#ABI-L1b-RadC/)</span> and <span style='color: #2A76BE;'>[NEXRAD](https://noaa-nexrad-level2.s3.amazonaws.com/index.html)</span> ",unsafe_allow_html=True)
    st.markdown("")
    st.markdown("")
    st.markdown("GOES (Geostationary Operational Environmental Satellite)These satellites assist meteorologists in observing and forecasting local weather phenomena such as thunderstorms, tornadoes, fog, hurricanes, flash floods, and other severe weather. GOES observations have also been useful in monitoring dust storms, volcanic eruptions, and forest fires.")
    st.markdown("")
    st.markdown("")
    st.markdown("NEXRAD (Next Generation Radar)NEXRAD detects precipitation and atmospheric movement or wind. It returns data which when processed can be displayed in a mosaic map which shows patterns of precipitation and its movement. The radar system operates in two basic modes, selectable by the operator – a slow-scanning clear-air mode for analyzing air movements when there is little or no activity in the area, and a precipitation mode, with a faster scan for tracking active weather.")


# Function for home page layout
def register_home_page_layout(auth_session_state_flag):
    #st.markdown(session_state_flag)

    # Checking any user is authorized / current active user Logged-In, if not it will show logout button
    if not auth_session_state_flag:
        register_url = 'http://127.0.0.1:8001/register_new_user'
        # Register Form Starts here
        with st.form(key="Register"):
            email = st.text_input("Email")
            username = st.text_input("Username")
            password = st.text_input("Password",type='password')
            plan = st.selectbox("Select your plan", ['free', 'gold', 'platinum'])
            register_status_btn = st.form_submit_button("Register!")
            # If Register button Clicked
            if (username != "" and password != "" and email != "" and plan != "") and register_status_btn:

                input_data = {
                    "email": email,
                    "username": username,
                    "password": password,
                    "plan": str(plan)
                }

                # Define a regular expression to match email addresses
                email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

                username_unique_flag = check_username_doesnot_exists(username)

                # Validate each email address before inserting it into the table
                # for row in data:
                #     email = row[0]
                if re.match(email_regex, email) and username_unique_flag=="success":
                    # if email regex match then trigger the api to insert the date into table
                    response = requests.post(url = register_url,json = input_data)
                    res = str(response.text)
                    if response.status_code == 200:
                        st.session_state["authenticated"] = False
                        st.success("User Successfully Registered!")
                        # write_Register_logs(email,username,get_password_hash(password),plan)

                    else:
                        st.error(f"{response.status_code}")

                elif username_unique_flag != "success":
                    st.error(f"User Already Exists!")

                else:
                    st.error("Please Enter Valid Email!")
            else:
                st.info("Please Provide Valid Credentials")

            # if username == "" or password == "": st.info("Please provide credentials")


                # Bobby - Now insert the user credentials into the database

                # Validate user credentials by calling the api function passing username and password
                # valid_user_flag = validate_user_credentials(username, password)

        # st.session_state["authenticated"] = False

        if username == "" or password == "" or email == "":
            st.info("Please provide credentials")
        # elif valid_user_flag:
        #     st.session_state["authenticated"] = True
        #     st.success("Logged In - Active User")
        #     # placeholder.empty()
        #     # logout_btn_actions()
        #     # st.session_state.login_status = False
        #     # st.session_state.logout_submit = True
        #     # login_status.disabled = False
        # else:
        #     st.session_state["authenticated"] = False
        #     st.error("Username or password is invalid")

    else:
        st.success("Logged In - Active User")
        c1, c2, c3, c4, c5 = st.columns(5)

        with c3:
            logout_btn = st.button("Logout!")

        if logout_btn:
            st.session_state.authenticated = False
            # placeholder_logout.empty()
            # st.success("User Logged-OUT")
            register_home_page_layout(st.session_state.authenticated)

def logout_btn_actions():
    st.success("Found Active USER, Please logout!")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c5:
        logout_btn1 = st.button("Logout")

    if logout_btn1:
        st.session_state.authenticated = False
        st.session_state.access_token = ""
        placeholder_logout.empty()
        # st.success("User Logged-OUT")
        register_home_page_layout(st.session_state.authenticated)

        # home_introduction()

#########################################################################################

# st.markdown(f"{st.session_state.login_status} - login status flag")
# st.markdown(f"{st.session_state.authenticated} - login status flag")

# st.markdown("HOME PAGE")
# with placeholder.container():
register_home_page_layout(st.session_state.authenticated)



