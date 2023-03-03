import typer
import os
import requests

app = typer.Typer()

BASE_URL = 'http://localhost:8000/'


@app.command()
def register_user(
        email: str = typer.Option(..., prompt=True),
        username: str = typer.Option(..., prompt=True),
        password: str = typer.Option(..., prompt=True),
        plan: str = typer.Option(..., prompt=True)
):
    URL = BASE_URL + 'register_new_user'
    data = {
        "email": email,
        "username": username,
        "password": password,
        "plan": plan
    }
    response = requests.post(URL, json=data)
    typer.echo(response.text)


@app.command()
def get_goes_files_list(
        year: int = typer.Option(..., prompt=True),
        day: str = typer.Option(..., prompt=True),
        hour: str = typer.Option(..., prompt=True)
):
    URL = BASE_URL + 'get_goes_files'
    data = {
        "year": year,
        "day": day,
        "hour": hour
    }
    response = requests.post(URL, json=data)
    typer.echo(response.text)


# @app.command()
# def get_goes_files2(
#         year: int = typer.Option(..., prompt=True),
#         day: str = typer.Option(..., prompt=True),
#         hour: str = typer.Option(..., prompt=True),
#         token: str = typer.Option(..., prompt=True)
# ):
#     URL = BASE_URL + 'get_goes_files_list'
#     data = {
#         "year": year, "day": day, "hour": hour
#     }
#     """Retrieve a list of files from the GOES bucket."""
#     credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials=token)
#     response = repquests.post(URL, json=data)
#     typer.echo(response)


@app.command()
def get_nexrad_files_list(
        year: int = typer.Option(..., prompt=True),
        month: str = typer.Option(..., prompt=True),
        day: str = typer.Option(..., prompt=True),
        station_code: str = typer.Option(..., prompt=True)
):
    URL = BASE_URL + 'get_nexrad_files'
    data = {
        "year": year,
        "month": month,
        "day": day,
        "station_code": station_code
    }
    response = requests.post(URL, json=data)
    typer.echo(response.text)


@app.command()
def get_file_by_name(
        filename_with_dir: str = typer.Option(..., prompt=True)
):
    file_name = {"filename_with_dir": filename_with_dir}

    if filename_with_dir.endswith('.nc'):
        URL = BASE_URL + 'get_nexrad_url'
    else:
        URL = BASE_URL + 'get_goes_url'
    response = requests.get(URL, params=file_name)
    typer.echo(response.text)


if __name__ == "__main__":
    app()
