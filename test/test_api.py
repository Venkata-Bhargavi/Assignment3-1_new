from fastapi.testclient import TestClient
from api_main import app

client = TestClient(app)
def test_nexrad_url():
    response = client.post(
        url="/get_nexrad_url",
        json= {
            'filename_with_dir': '2022/04/08/TDFW/TDFW20220408_022326_V08'
        }
    )
    assert response.status_code == 200
    message = response.json()["url"]
    assert message == 'https://damg7245-ass1.s3.amazonaws.com/2022/04/08/TDFW/TDFW20220408_022326_V08'

def test_geos_url():
    response = client.post(
        url="/get_goes_url",
        json= {
            'filename_with_dir': 'ABI-L1b-RadC/2023/002/02/OR_ABI-L1b-RadC-M6C01_G18_s20230020201172_e20230020203551_c20230020204001.nc'
        }
    )
    assert response.status_code == 200
    message = response.json()["url"]
    assert message == 'https://damg7245-ass1.s3.amazonaws.com/ABI-L1b-RadC/2023/002/02/OR_ABI-L1b-RadC-M6C01_G18_s20230020201172_e20230020203551_c20230020204001.nc'
    

def test_authentication():
    response = client.post(
        url="/autheticate_user",
        json= {
            'un': 'damg7245',
            'pwd': 'spring2023'
        }
    )    
    assert response.status_code == 200
    message = response.json()["matched"]
    # assert message =='verify'   