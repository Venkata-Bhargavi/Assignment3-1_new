import re

import streamlit as st
import json
import requests

from api_main import check_username_doesnot_exists


import altair as alt
from cloudwatch.logs import *
from datetime import datetime, timedelta
import plotly.express as px

# import components.authenticate as authenticate

logout_btn = False
valid_user_flag = 0
placeholder = st.empty()
placeholder_logout = st.empty()




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


df = read_user_api_usage_logs()
df['date'] = pd.to_datetime(df['timestamp']).dt.date

# st.dataframe(df)

def total_req_by_user(user):
    user_df = df[df.username == user].copy()
    # group by username and date, and count the number of requests
    # result = user_df.groupby('date')['endpoint'].count().reset_index(name='count')
    # # user_df.groupby(['username', 'date']).size().reset_index(name='count')
    #
    # # st.dataframe(result)
    #
    # # group by date and count the number of requests
    # user_df1 = user_df.groupby('date')['endpoint'].count().reset_index(name='count')

    # user_df.date.value_counts()
    st.info(f"Total Requests by Date for user - {user}: {df[df.username == user].shape[0]}")

    if df[df.username == user].shape[0] >0:
        vc = df[df.username == user]['date'].value_counts()

        # convert the value counts to a dataframe
        df_vc = vc.to_frame().reset_index()

        # rename the columns
        df_vc.columns = ['date', 'count']

        # create an Altair line chart
        # chart = alt.Chart(user_df1).mark_bar().encode(
        #     x='date',
        #     y='count'
        # )

        st.markdown("")
        # display the chart in Streamlit
        # st.altair_chart(chart)
        # c1, c2, c3 = st.columns(3)
        # with c3:
        #     st.markdown("Total Requests by Date")
        st.dataframe(df_vc)
        st.bar_chart(df_vc, x='date', y='count')
        # data_canada = px.data.gapminder().query("country == 'Canada'")
        # fig = px.bar(df_vc, x='date', y='count')
        # # fig.show()
        # st.plotly_chart(fig)
    # else:
    #     st.markdown("No Records Found")

# Total API calls for yesterday
def total_api_calls_yesterday(user):
    # Get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.date()

    # Filter dataframe to only include data from yesterday
    df_yesterday = df[(df.username == user) & (pd.to_datetime(df['timestamp']).dt.date == yesterday)].copy()
    st.markdown("")
    st.info(f"Total API Calls Previous Day: {df_yesterday.shape[0]}")

    df_yesterday['endpoint'] = df_yesterday['endpoint'].apply(lambda x: x.split('/')[-1])

    if df_yesterday.shape[0]>0:
        st.dataframe(df_yesterday)
        value_counts = df_yesterday['endpoint'].value_counts()

        # create bar chart using streamlit
        st.bar_chart(value_counts)

def total_api_calls_last_week(user):

    # Get the start and end dates for the last 7 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)

    # Filter dataframe to only include data from the last week
    df_last_week = df[(df.username==user) & (pd.to_datetime(df['timestamp']).dt.date >= start_date) & (pd.to_datetime(df['timestamp']).dt.date <= end_date)].copy()
    st.markdown("")
    st.info(f"Total API Calls Last Week: {df_last_week.shape[0]}")

    df_last_week['endpoint'] = df_last_week['endpoint'].apply(lambda x: x.split('/')[-1])

    if df_last_week.shape[0] > 0:
        st.dataframe(df_last_week)
        value_counts = df_last_week['endpoint'].value_counts()

        # create bar chart using streamlit
        st.bar_chart(value_counts)

# 5. Total API calls by Endpoint
def total_api_calls_by_endpoint(user):
    # result = df.groupby('endpoint').count().reset_index()
    # requests_by_endpoint = df.groupby('endpoint').size().reset_index(name='total_requests')

    # count = df.endpoint.value_counts().values[0] if df.shape[0] > 0 else 0

    vc = df[df.username == user]['endpoint'].value_counts()

    # convert the value counts to a dataframe
    df_vc = vc.to_frame().reset_index()

    # rename the columns
    df_vc.columns = ['endpoint', 'count']

    # user_df.groupby(['username', 'date']).size().reset_index(name='count')
    st.markdown("")
    st.info(f"Total API Calls by each Endpoint:")
    df_vc['endpoint'] = df_vc['endpoint'].apply(lambda x: x.split('/')[-1])

    if df_vc.shape[0] > 0:
        st.dataframe(df_vc)
        value_counts = df_vc['endpoint'].value_counts()

        # create bar chart using streamlit
        st.bar_chart(df_vc, x='endpoint', y='count')

    # st.dataframe(df)

    # st.markdown(df.endpoint.value_counts())

def total_api_calls_success(user):
    df = fetch_api_success_logs_for_5_days()

    if df[df.username==user].shape[0] > 0:
        df = df[df.username == user]
        #
        st.info(f"Total Success API Calls: {df.status.value_counts().values[0]}")
        df['endpoint'] = df[df.username == user]['endpoint'].apply(lambda x: x.split('/')[-1])

        if df.shape[0]>0:
            st.dataframe(df)
            value_counts = df['endpoint'].value_counts()

            # create bar chart using streamlit
            st.bar_chart(value_counts)

            # display value counts as a table
            # st.write(value_counts)

        # st.markdown()
    else:
        st.info(f"Total Success API Calls: 0")



def total_api_calls_failure(user):
    df = fetch_api_failed_logs_for_5_days()
    df = df[df.username == user]
    count = df[df.username == user].status.value_counts().values[0] if df.shape[0] > 0 else 0
    st.info(f"Total Failed API Calls: {count}")
    df['endpoint'] = df['endpoint'].apply(lambda x: x.split('/')[-1])

    if count:
        st.dataframe(df)
        # get value counts of column
        value_counts = df[df.username == user]['endpoint'].value_counts()

        # create bar chart using streamlit
        st.bar_chart(value_counts)

        # display value counts as a table
        # st.write(value_counts)


def admin_dashboard_home_page_layout(auth_session_state_flag):
    df = read_user_api_usage_logs()

    # whole_df = fetch_logs_for_5_days()
    api_logs_df = fetch_api_usage_logs_for_5_days()
    loggedin_logs_df = fetch_logs_for_5_days()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        user = st.selectbox("Select a User", loggedin_logs_df.username.unique().tolist())
        # user = st.selectbox("Select a User", ['god', 'god1'])

    # 1. Chart for Total Request by the user
    total_req_by_user(user)

#     2. total Api Calls yesterday
    total_api_calls_yesterday(user)

    # 3. Average Calls during the last week
    total_api_calls_last_week(user)

#     4. Success/Failure API calls
    total_api_calls_success(user)
    total_api_calls_failure(user)

#     5. Total APi calls by Each Endpoint
    total_api_calls_by_endpoint(user)


def user_dashboard_home_page_layout(auth_session_state_flag, username):
    df = read_user_api_usage_logs()

    # whole_df = fetch_logs_for_5_days()
    api_logs_df = fetch_api_usage_logs_for_5_days()


    # 1. Chart for Total Request by the user
    total_req_by_user(username)

#     2. total Api Calls yesterday
    total_api_calls_yesterday(username)

    # 3. Average Calls during the last week
    total_api_calls_last_week(username)

#     4. Success/Failure API calls
    total_api_calls_success(username)
    total_api_calls_failure(username)

#     5. Total APi calls by Each Endpoint
    total_api_calls_by_endpoint(username)


def logout_btn_actions():
    st.success("Found Active USER, Please logout!")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c5:
        logout_btn1 = st.button("Logout")

    if logout_btn1:
        st.session_state.authenticated = False
        st.session_state.access_token = ""
        st.session_state.user_plan = ""
        st.session_state.active_user = ""
        placeholder_logout.empty()
        # st.success("User Logged-OUT")
        dashboard_home_page_layout(st.session_state.authenticated)

        # home_introduction()

#########################################################################################

# st.markdown(f"{st.session_state.login_status} - login status flag")
# st.markdown(f"{st.session_state.authenticated} - login status flag")

# st.markdown("HOME PAGE")
# with placeholder.container():
# dashboard_home_page_layout(st.session_state.authenticated)

# if st.session_state.authenticated:
#     logout_btn = st.button('Logout!')
#     dashboard_home_page_layout(st.session_state.authenticated)

c1, c2, c3, c4, c5 = st.columns(5)


if st.session_state["authenticated"] == True:


    with c5:
        logout_btn = st.button("Logout!")

    st.markdown(
        "<h3 style='text-align: center'><span style='color: #2A76BE;'>Welcome to Data Exploration Application</span></h3>",
        unsafe_allow_html=True)
    st.markdown(
        "<h5 style='text-align: center'>One stop to leverage data from NOAA Satellite and radars for analysis and extract insights.</h5>",
        unsafe_allow_html=True)

    # st.markdown("<h1 style='text-align: center'>Data Explorator - GOES</h1>", unsafe_allow_html=True)

    if st.session_state.active_user == 'admin':
        admin_dashboard_home_page_layout(st.session_state.authenticated)
    else:
        user_dashboard_home_page_layout(st.session_state.authenticated, st.session_state.active_user)


    # c1, c2, c3, c4, c5 = st.columns(5)
    # with c5:

else:
    st.error("Please login to access session")


def loggedOutPage():
    st.success("User Logged Out!")


if logout_btn:
    st.session_state.authenticated = False
    st.session_state.access_token = ""
    st.session_state.valid_user_flag = 0
    st.session_state.user_plan = ""
    st.session_state.active_user = ""
    # st.success("User Logged-OUT")
    loggedOutPage()