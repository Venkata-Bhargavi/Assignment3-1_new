import streamlit as st
import json
import requests
from streamlit_lottie import st_lottie

from api_main import hash_text, get_plan_for_user
# import components.authenticate as authenticate
from cloudwatch.logs import read_register_user_logs, write_loggedin_user_logs
from api_main import update_user_credentials

logout_btn = False
valid_user_flag = 0
placeholder = st.empty()
placeholder_logout = st.empty()

with open('config.json', 'r') as f:
    config = json.load(f)

login_endpoint = config['endpoints']['login']
st.markdown(
        "<h3 style='text-align: center'><span style='color: #2A76BE;'>Welcome to Data Exploration Application</span></h3>",
        unsafe_allow_html=True)
st.markdown(
        "<h5 style='text-align: center'>One stop to leverage data from NOAA Satellite and radars for analysis and extract insights.</h5>",
        unsafe_allow_html=True)

# from pages.Nexrad import nexrad_home
# from streamlit_extras.switch_page_button import switch_page

#current active username



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

if 'active_user' not in st.session_state:
    st.session_state.active_user = ""

if 'access_token' not in st.session_state:
    st.session_state.access_token = False

if 'user_plan' not in st.session_state:
    st.session_state.user_plan = False


if 'forgot_pwd_btn' not in st.session_state:
    st.session_state.forgot_pwd_btn = 0


valid_user_flag = False

# def validate_user_credentials(username, password):
#
#     # url = 'http://api:8000/autheticate_user'
#     url = "http://localhost:8000/autheticate_user"
#     data = {
#         # 'email': email,
#         "un": username,
#         "pwd": password,
#         # 'plan': plan
#     }
#     response = requests.post(url=url, json=data)
#     st.markdown(response.json())
#     valid_user_flag = response.json().get('matched')
#     token = response.json().get('access_token')
#     return valid_user_flag, token

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
    # st.markdown("<h3 style='text-align: center'><span style='color: #2A76BE;'>Welcome to Data Exploration Application</span></h3>",unsafe_allow_html=True)
    # st.markdown("<h5 style='text-align: center'>One stop to leverage data from NOAA Satellite and radars for analysis and extract insights.</h5>",unsafe_allow_html=True)
    st.markdown("")
    st.markdown("The 2 datasets available are: <span style='color: #2A76BE;'>[GOES](https://noaa-goes18.s3.amazonaws.com/index.html#ABI-L1b-RadC/)</span> and <span style='color: #2A76BE;'>[NEXRAD](https://noaa-nexrad-level2.s3.amazonaws.com/index.html)</span> ",unsafe_allow_html=True)
    st.markdown("")
    st.markdown("")
    st.markdown("GOES (Geostationary Operational Environmental Satellite)These satellites assist meteorologists in observing and forecasting local weather phenomena such as thunderstorms, tornadoes, fog, hurricanes, flash floods, and other severe weather. GOES observations have also been useful in monitoring dust storms, volcanic eruptions, and forest fires.")
    st.markdown("")
    st.markdown("")
    st.markdown("NEXRAD (Next Generation Radar)NEXRAD detects precipitation and atmospheric movement or wind. It returns data which when processed can be displayed in a mosaic map which shows patterns of precipitation and its movement. The radar system operates in two basic modes, selectable by the operator – a slow-scanning clear-air mode for analyzing air movements when there is little or no activity in the area, and a precipitation mode, with a faster scan for tracking active weather.")


def return_matched_password(db_password, hashed_password):
    flag = 0
    if db_password == hashed_password:
        flag = 1
    return flag


# def test_verify_user(un, pwd):
#     df = read_register_user_logs()
#     db_pwd = df[df.username == un].password[0]
#     st.markdown(db_pwd[0])
#     # verify_password(credentials.pwd, db_pwd)
#     if return_matched_password(db_pwd, hash_text(pwd)):
#         # return authentication.signJWT(credentials.email)
#         # st.markdown(f"plan --> {df[df.username == un]['plan']} for {un}")
#         st.dataframe(df[df.username == un])
#         # return {"matched": return_matched_password(db_pwd, hash_text(pwd)),
#         #         'access_token': authentication.signJWT(credentials.un),"plan":df[df.username == credentials.un].plan}
#     else:
#         # raise HTTPException(status_code=401, detail='Invalid username or password')
#         # return {"matched": return_matched_password(db_pwd, hash_text(pwd)), 'access_token': "","plan":""}
#         st.markdown("Not Found")

df = read_register_user_logs()

def verify_user_cred(username, password):
    # st.markdown(df[df.username==username]['password'][0])

    pwd = (df[df.username==username]['password'][0])
    hpwd = (hash_text(password))

    # st.markdown(f"Checking the match --> {pwd==hpwd}")

    # if compare_hashes(hpwd, pwd):
    #     st.markdown("User Found")

    # if pwd.equals(hpwd):
    #     st.markdown("User Found")



# Function for home page layout
def home_page_layout(auth_session_state_flag):
    # st.markdown(session_state_flag)
    st.session_state.forgot_pwd_btn = 0
    token = ""
    response = ""
    # Checking any user is authorized / current active user Logged-In, if not it will show logout button
    if not auth_session_state_flag:
        with st.form(key="Login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')

            login_status = st.form_submit_button("Login")

            # col1, col2, col3, col4, col5= st.columns(5)
            #
            # with col5:
            #     forgot_pwd_btn = st.form_submit_button("Forgot Password?")


            if login_status and username != "" and password != "":

                # st.markdown(hash_text(password))
                # test_verify_user(username, password)
                url = "http://localhost:8001/autheticate_user"
                data = {
                    # 'email': email,
                    "un": username,
                    "pwd": password,
                    # 'plan': plan
                }
                # r = verify_log_in(username,password)
                # st.markdown(r)
                df = read_register_user_logs()
                # st.dataframe(df)
                # st.markdown(df.shape)
                # st.dataframe(df[df.username == username])
                # st.markdown(hash_text(password))
                # verify_user_cred(username, password)


                response = requests.post(url=url, json=data)
                # st.markdown(f"{response.json()}")
                # st.markdown(response.status_code)
                # st.markdown(f"{response.json().get('matched')}---->{response.status_code}")

                if response.status_code == 200 and response.json().get('matched'):

                    # st.markdown(token)
                    st.markdown(f"Success Login!")
                    user_plan = get_plan_for_user(username)
                    # st.markdown(f"Plan {response.json().get('plan')} --> {response.json().get('access_token')}")
                    # df = read_register_user_logs()
                    write_loggedin_user_logs(username, hash_text(password), user_plan)
                    st.session_state.access_token = response.json().get('access_token')
                    st.session_state.user_plan = user_plan     #df[df.username == username]["plan"]

                    st.session_state["authenticated"] = True
                    st.session_state.active_user = username
                    # st.success("Logged In - Active User")
                    # st.markdown(f"USER --> {st.session_state.active_user} --> {st.session_state.user_plan} plan")
            # elif forgot_pwd_btn:
            #         st.session_state.forgot_pwd_btn = 1
            else:
                st.markdown("")

        # if st.session_state.forgot_pwd_btn:
        #     unr = st.text_input("Username")
        #     emailr = st.text_input("Email")
        #     pwdr = st.text_input("New Password", type='password')
        #     pwdr_btn = st.button('Update Password')
        #
        #     password_flag = 0
        #
        #     if pwdr_btn:
        #         password_flag = update_user_credentials(unr, pwdr, emailr)
        #         st.session_state.forgot_pwd_btn = 0
        #
        #     if password_flag:
        #         st.success("Password Updated Successfully")
        #     else:
        #         st.error("Provide valid Credentials")



        if username == "" or password == "":
            st.info("Please provide credentials")
        elif st.session_state["authenticated"]:
            st.info("Active USER Found!")

        else:
            st.session_state["authenticated"] = False
            st.session_state.active_user = ""
            st.error("Credentials Not Found")

    else:
        st.success("Logged In - Active User")
        c1, c2, c3, c4, c5 = st.columns(5)

        with c3:
            logout_btn = st.button("Logout!")

        if logout_btn:
            st.session_state.authenticated = False
            st.session_state.user_plan = ""
            st.session_state.active_user = ""
            # placeholder_logout.empty()
            # st.success("User Logged-OUT")

            home_page_layout(st.session_state.authenticated)

def logout_btn_actions():
    st.success("Found Active USER, Please logout!")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c5:
        logout_btn1 = st.button("Logout")

    if logout_btn1:
        st.session_state.authenticated = False
        st.session_state.access_token = ""
        st.session_state.valid_user_flag = 0
        st.session_state.user_plan = ""
        st.session_state.active_user = ""
        placeholder_logout.empty()
        # st.success("User Logged-OUT")
        home_page_layout(st.session_state.authenticated)

        # home_introduction()

#########################################################################################

# st.markdown(f"{st.session_state.login_status} - login status flag")
# st.markdown(f"{st.session_state.authenticated} - login status flag")

# st.markdown("HOME PAGE")
# with placeholder.container():
home_page_layout(st.session_state.authenticated)


st.markdown("-------------------------------------------------------------------------------------------------")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("<h3>Reset Password!</h3>", unsafe_allow_html=True)

unr = st.text_input("Username")
emailr = st.text_input("Email")
pwdr = st.text_input("New Password", type='password')
pwdr_btn = st.button('Update Password')

password_flag = 0

if pwdr_btn:
    password_flag = update_user_credentials(unr, emailr, hash_text(pwdr))
    st.session_state.forgot_pwd_btn = 0

if password_flag and unr != "" and emailr != "" and pwdr != "":
    st.success("Password Updated Successfully")
else:
    st.error("Provide valid Credentials")


