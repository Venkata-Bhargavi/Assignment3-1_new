# Assignment 3- Code Enhancement

User Guide - <a href="https://codelabs-preview.appspot.com/?file_id=1WuXZUl3ZoBxxDY33n4CoS1PDx_Qhr2KuQ16byUmUeMc#8">Assignment 3 - User Guide</a>


<h3> Description </h3>

In this repository, we are going to add functionality to the existing Goes-Nexrad Streamlit Application from Assignment 1.
The following changes have been incorporated to enhance the Application reusability.
* 1. Fast API : 

* 2. Docker:
  
* 3. Great Expectation:
     1. Great Expectation hosted on s3 bucket : http://data-great-expect.s3-website-us-east-1.amazonaws.com

* 4. Airflow: 



<h3> Flow of Data</h3>

1. NOAA's website has raw GOES and NEXRAD satellite data.
2. This data is scraped in order to generate metadata, which is then stored in SQLite.
3. These values pertain to metadata directories.
4. There is an Authentication page that authenticates the user.
5. The user has access to our Exploration Web App, where he must specify the 'Year,' 'Day,' and 'Hour'.
6. Using these values, a unique file is fetched and a link to download the file displayed.
7. User can also use the filename to retrive and download the file.
8. Downloaded file is in .NC format, used to store multidimensional data.


1. Streamlit

* Implementation of login page and allowing authenticated users to interact with the dashboard.[1]
* Sending RestAPI calls to FastAPI endpoints and display the returned response.

2. FastAPI
* Endpoints as per the usecase.
* Process of file transfer within fastapi with status of the request returned appropriatly to streamlit. Example, if the user inputs are invalid, the response return code should be “400 - Bad Request”

3. Airflow
* Create DAG’s with task’s in order of their dependency.
<h3> Built With </h3>

Following are the stacks used to build this project

1. AWS
2. SQLite3
3. Python 3.9
4. Streamlit 1.12
5. FastAPI for authenticating the user
6. Docker to containerize the entire application
7. Great Expectation 
8. Airflow to build workflows connecting virtually any technology
9. Cloud Hosting
10. Architecture diagram for Cloud

<h3> Steps to run this project </h3>

1. Open terminal
2. Change to the location where you want to copy the repository
3. Copy and paste the following command, and press enter
```bash
   https://github.com/BigDataIA-Spring2023-Team-11/Assignment3.git
```
4.Run the following to install the requirements file.
```bash
 pip install -r requirements.txt
```

<h3> Contribution </h3>

1. Aakash :  23.33%  
2. Bhakti :  23.33%
3. Bhargavi: 30%
4. Charu :   23.33%

WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK
