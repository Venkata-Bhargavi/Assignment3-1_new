from cloudwatch.logs import *
from datetime import datetime, timedelta






def check_user_usage_limit_within_lasthour(username, endpoint):
    # Pull the API logs data then filter by username and api endpoint
    api_usage_df = pd.DataFrame()
    api_usage_df = read_user_api_usage_logs() #-----------------reading logs

    df = api_usage_df[(api_usage_df.username == username) & (api_usage_df.endpoint == endpoint)].copy()

    if df.shape[0] >0:

        # Convert the timestamp column to a datetime object
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Define the time range you want to look at
        time_range = timedelta(hours=1)

        # Define a function that takes a timestamp and returns the count of unique API endpoints in the time range
        def count_unique_endpoints(row):
            start_time = row['timestamp'] - time_range
            end_time = row['timestamp']
            endpoints = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]['endpoint']
            return endpoints.value_counts()

        # Apply the function to each row in the dataframe and store the result in a new column
        df['unique_endpoints_last_hour'] = df.apply(count_unique_endpoints, axis=1)
        st.dataframe(df)

        df = df.sort_values(by='timestamp', ascending=False)

        # Get the api_endpoints_last_hour value for the first row
        total_triggers_in_last_hour = df.iloc[0]['unique_endpoints_last_hour']
        return total_triggers_in_last_hour
    else:
        return 0
    # st.markdown(total_triggers_in_last_hour)

# if __name__ == "__main__":
#     endpoint = "http://localhost:8001/get_nexrad_url"
#
#     check_user_usage_limit_within_lasthour("bob", endpoint)
