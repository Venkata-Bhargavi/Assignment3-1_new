import os
from datetime import datetime
# import great_expectations_provider
import boto3
import pandas as pd
import psycopg2
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from dotenv import load_dotenv
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
from great_expectations.data_context.types.base import (
    CheckpointConfig,
    DataContextConfig,
)

load_dotenv()

BASE_URL = os.getenv("DB_URL", "postgresql://team11:team11@host_db:5432/noaa_database")
base_path = "/opt/airflow/working_dir"
ge_root_dir = os.path.join(base_path, "great_expectations")

goes_bucket = "noaa-goes18"
nexrad_bucket = "noaa-nexrad-level2"
des_bucket = "damg7245-ass1"

aws_access_key_id = 'AKIAVDK4IUCRNV5UP46G'
aws_secret_access_key='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'

# aws_access_key_id = os.environ.get('AWS_ACCESS_KEY')
# aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')

# Initialize Connection
s3 = boto3.client('s3', region_name='us-east-1',
                  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                  aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'))
s3 = boto3.client('s3', region_name='us-east-1',
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key)

# Define DAG arguments
default_args = {
    'owner': 'Charu Singh',
    'depends_on_past': False,
    'start_date': datetime.today()
}

def GOES_scrap_load():
    goes18_dict = {
        'id': [],
        'product': [],
        'year': [],
        'day': [],
        'hour': []
    }
    prefix = 'ABI-L1b-RadC/'
    delimiter = '/'
    id = 1
    result = s3.list_objects(Bucket=goes_bucket, Prefix=prefix, Delimiter='/')
    for o in result.get('CommonPrefixes'):
        path = o.get('Prefix').split('/')
        prefix_new = prefix + path[-2] + "/"
        sub_folder = s3.list_objects(
            Bucket=goes_bucket, Prefix=prefix_new, Delimiter=delimiter)
        if sub_folder is not None:  # Check if sub_folder is not None
            for p in sub_folder.get('CommonPrefixes'):
                sub_path = p.get('Prefix').split('/')
                prefix_new2 = prefix_new + sub_path[-2] + "/"
                sub_sub_folder = s3.list_objects(
                    Bucket=goes_bucket, Prefix=prefix_new2, Delimiter=delimiter)
                if sub_sub_folder is not None:
                    for q in sub_sub_folder.get('CommonPrefixes'):
                        sub_sub_path = q.get('Prefix').split('/')
                        sub_sub_path = sub_sub_path[:-1]
                        goes18_dict['id'].append(id)
                        goes18_dict['product'].append(sub_sub_path[0])
                        goes18_dict['year'].append(sub_sub_path[1])
                        goes18_dict['day'].append(sub_sub_path[2])
                        goes18_dict['hour'].append(sub_sub_path[3])
                        id += 1

    df = pd.DataFrame(goes18_dict)

    # Connect to PostgreSQL database
    conn = psycopg2.connect(host="host_db", database="noaa_database", user="team11", password="team11")
    cur = conn.cursor()

    # Create table for metadata
    cur.execute('''CREATE TABLE IF NOT EXISTS metadata_goes18
                (id integer, product text, year integer, day integer, hour integer)''')

    # insert the DataFrame into a new table named 'metadata_goes18'
    for index, row in df.iterrows():
        cur.execute("INSERT INTO metadata_goes18 (id, product, year, day, hour) VALUES (%s, %s, %s, %s, %s)",
                    (row[0], row[1], row[2], row[3], row[4]))

    # Commit changes and close database connection
    conn.commit()
    conn.close()


def NEXRAD_scrap_load():
    NEXRAD_dict = {
        'id': [],
        'year': [],
        'month': [],
        'day': [],
        'station': []
    }
    years = ['2022', '2023']
    id = 1
    delimiter = '/'

    for y in years:
        prefix = y + '/'
        result = s3.list_objects(Bucket=nexrad_bucket, Prefix=prefix, Delimiter='/')
        for o in result.get('CommonPrefixes'):
            path = o.get('Prefix').split('/')
            prefix_new = prefix + path[-2] + "/"
            sub_folder = s3.list_objects(Bucket=nexrad_bucket, Prefix=prefix_new, Delimiter='/')
            if sub_folder is not None:  # Check if sub_folder is not None
                for p in sub_folder.get('CommonPrefixes'):
                    sub_path = p.get('Prefix').split('/')
                    prefix_new2 = prefix_new + sub_path[-2] + "/"
                    sub_sub_folder = s3.list_objects(Bucket=nexrad_bucket, Prefix=prefix_new2, Delimiter='/')
                    if sub_sub_folder is not None:
                        for q in sub_sub_folder.get('CommonPrefixes'):
                            sub_sub_path = q.get('Prefix').split('/')
                            sub_sub_path = sub_sub_path[:-1]
                            NEXRAD_dict['id'].append(id)
                            NEXRAD_dict['year'].append(sub_sub_path[0])
                            NEXRAD_dict['month'].append(sub_sub_path[1])
                            NEXRAD_dict['day'].append(sub_sub_path[2])
                            NEXRAD_dict['station'].append(sub_sub_path[3])
                            id += 1

    df = pd.DataFrame(NEXRAD_dict)

    conn = psycopg2.connect(host="host_db", database="noaa_database", user="team11", password="team11")
    cur = conn.cursor()

    # Create table for metadata
    cur.execute('''CREATE TABLE IF NOT EXISTS metadata_nexrad
                (id integer, year integer, month integer, day integer, station text)''')

    # insert the DataFrame into a new table named 'nexrad'
    for index, row in df.iterrows():
        cur.execute("INSERT INTO metadata_nexrad (id, year, month, day, station) VALUES (%s, %s, %s, %s, %s)",
                    (row[0], row[1], row[2], row[3], row[4]))

    # Close database connection
    conn.commit()
    conn.close()


def export_to_csv(**kwargs):
    engine = create_engine(BASE_URL)
    engine.connect()
    goes = pd.read_sql_table("metadata_goes18", con=engine)
    goes.to_csv(f"/opt/airflow/working_dir/data/goes.csv", sep=',', index=False)
    nexrad = pd.read_sql_table("metadata_nexrad", con=engine)
    nexrad.to_csv(f"/opt/airflow/working_dir/data/nexrad.csv", sep=',', index=False)


def nexrad_stations(**kwargs):
    engine = create_engine(BASE_URL)
    engine.connect()
    cols = [
        (20, 51),  # Name
        (72, 75),  # ST
        (106, 116),  # Lat
        (116, 127)  # Lon
    ]
    df = pd.read_fwf(r"https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt", colspecs=cols, skiprows=[1])
    df.to_sql(name='nexrad_stations', con=engine, if_exists='replace', index=False)

    station = pd.read_sql_table("nexrad_stations", con=engine)
    station.to_csv(f"/opt/airflow/working_dir/data/nexrad-stations.csv", sep=',', index=False)

# Define DAG
scrapper_dag = DAG(
    'metadata_scraper',
    default_args=default_args,
    description='Scrape data from an S3 bucket and upload database',
    schedule_interval='0 0 * * *'
)
# Define DAG tasks
scrape_goes = PythonOperator(
    task_id='scrape_goes_data',
    python_callable=GOES_scrap_load,
    dag=scrapper_dag
)
scrape_nexrad = PythonOperator(
    task_id='scrape_nexrad_data',
    python_callable=NEXRAD_scrap_load,
    dag=scrapper_dag
)

fetch_nexrad_stations = PythonOperator(
    task_id='fetch_nexrad_stations',
    python_callable=nexrad_stations,
    provide_context=True,
    dag=scrapper_dag
)

export_csv = PythonOperator(
    task_id='export_to_csv',
    python_callable=export_to_csv,
    dag=scrapper_dag
)

ge_goes = GreatExpectationsOperator(
    task_id="goes18_run_data_validation",
    data_context_root_dir=ge_root_dir,
    checkpoint_name="goes_ck_v1",
    fail_task_on_validation_failure=False,
    dag=scrapper_dag
)

ge_nexrad = GreatExpectationsOperator(
    task_id="nexrad_run_data_validation",
    data_context_root_dir=ge_root_dir,
    checkpoint_name="nexrad_ck_v1",
    dag=scrapper_dag
)

# (scrape_goes, scrape_nexrad, fetch_nexrad_stations) >> export_csv
(scrape_goes, scrape_nexrad) >> fetch_nexrad_stations >> export_csv >> (ge_goes, ge_nexrad)
