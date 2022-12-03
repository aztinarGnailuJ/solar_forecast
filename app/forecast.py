from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from datetime import datetime
import requests, uvicorn, pandas as pd, numpy as np


templates = Jinja2Templates(directory="app/templates")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
app.mount("/app/scripts", StaticFiles(directory="app/scripts"), name="scripts")
app.mount("/app/public/", StaticFiles(directory="app/public"), name="public")


url="https://api.solcast.com.au/rooftop_sites/e3d7-0d26-64bb-b182/forecasts?format=csv&api_key=qNZvOXVxnO4dO55bkjT-YjVtPTyzbUes"

def refresh_data():
    global url
    content=requests.get(url).content
    decoded_data=content.decode('utf-8')
    with open('app/static/forecast.csv', 'w') as forecast:
        forecast.write(decoded_data)

refresh_data()
last_refresh = datetime.now().timestamp()

@app.get("/",response_class = HTMLResponse)
async def get_index(request: Request):
    global last_refresh
    if datetime.now().timestamp() - last_refresh > 3600:
        print("Refreshing Data...")
        refresh_data()
        last_refresh = datetime.now().timestamp()
    
    data = pd.read_csv('app/static/forecast.csv', sep = ",")
    PVEst = data['PvEstimate'].to_numpy()
    PVEst10 = data['PvEstimate10'].to_numpy()
    PVEst90 = data['PvEstimate90'].to_numpy()
    # PeriodEnd = [datetime.fromisoformat(date.replace('Z', '+00:00')).astimezone(pytz.timezone('Europe/Berlin')).isoformat() for date in data['PeriodEnd'].to_numpy()]
    PeriodEnd = [datetime.fromisoformat(date.replace('Z', '+00:00')).isoformat() for date in data['PeriodEnd'].to_numpy()]

    expected_production = []
    expected_production_low = []
    expected_production_high = []
    current_sum_of_prod = 0
    current_sum_of_prod_high = 0
    current_sum_of_prod_low = 0

    for idx, Period in enumerate(PeriodEnd):
        hour = datetime.fromisoformat(Period).hour
        minute = datetime.fromisoformat(Period).minute

        if (hour == 23 and minute == 0) or idx+1 == (len(PeriodEnd)):
            expected_production.append(round(current_sum_of_prod, 2))
            current_sum_of_prod = 0
            expected_production_high.append(round(current_sum_of_prod_high, 2))
            current_sum_of_prod_high = 0
            expected_production_low.append(round(current_sum_of_prod_low, 2))
            current_sum_of_prod_low = 0
        current_sum_of_prod += PVEst[idx]
        current_sum_of_prod_high += PVEst90[idx]
        current_sum_of_prod_low += PVEst10[idx]

    return templates.TemplateResponse("index.html",
                                        {'request': request,
                                         "PVEst": PVEst.tolist(),
                                         "PVEst10": PVEst10.tolist(),
                                         "PVEst90": PVEst90.tolist(),
                                         "periodend": PeriodEnd,
                                         "expected": expected_production,
                                         "expected10": expected_production_low,
                                         "expected90": expected_production_high})




    
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)