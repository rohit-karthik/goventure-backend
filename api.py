import requests
from flask import Flask, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def getCityCode(city):
    url = "https://priceline-com-provider.p.rapidapi.com/v2/flight/autoComplete"

    querystring = {
        "string": city,
        "cities": "true",
    }

    headers = {
        "X-RapidAPI-Key": "c4eb4cd005msh573cc84fd39a74ep1f8ed7jsncbcbe93e3816",
        "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers,
                           params=querystring)

    res = response.json()

    base = res["getAirAutoComplete"]["results"]["getSolr"]["results"]["data"]["city_data"]
    for i in base:
        if "city_code" in base[i]:
            return base[i]["city_code"]

    return "NULL"

def getLocId(city):
    url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/locations"


    querystring = {"name": city, "search_type": "ALL"}

    headers = {
        "X-RapidAPI-Key": "c4eb4cd005msh573cc84fd39a74ep1f8ed7jsncbcbe93e3816",
        "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    res = response.json()
    return res[0]["id"]

@app.route("/hotels/<city>/<cIn>/<cOut>")
def hotels(city, cIn, cOut):
    url = "https://priceline-com-provider.p.rapidapi.com/v1/hotels/search"

    locId = getLocId(city)
    querystring = {"sort_order":"PRICE","location_id":locId,"date_checkout":cOut,"date_checkin":cIn}

    headers = {
        "X-RapidAPI-Key": "c4eb4cd005msh573cc84fd39a74ep1f8ed7jsncbcbe93e3816",
        "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    res = response.json()

    tR = []
    for i in res["hotels"]:
        if "name" in i:
            tR.append({
                "name": i["name"],
                "fare": i["ratesSummary"]["minPrice"]
            })
    
    return {
        "data": tR
    }

@app.route("/flights/<origin>/<destination>/<date>")
def main(origin, destination, date):
    url = "https://priceline-com-provider.p.rapidapi.com/v1/flights/search"

    origin = getCityCode(origin)
    destination = getCityCode(destination)

    print(origin)
    print(destination)

    querystring = {
        "itinerary_type": "ONE_WAY",
        "class_type": "ECO",
        "location_arrival": destination,
        "date_departure": date,
        "location_departure": origin,
        "sort_order": "PRICE"
    }

    headers = {
        "X-RapidAPI-Key": "c4eb4cd005msh573cc84fd39a74ep1f8ed7jsncbcbe93e3816",
        "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    res = response.json()

    base = res["pricedItinerary"]
    tR = []

    for i in base:
        if i["pricingInfo"]["ticketingAirline"] == "AA":
            tA = {
                "airline": "American Airlines",
                "fare": i["pricingInfo"]["totalFare"]
            }
            if tA not in tR:
                tR.append(tA)
        elif i["pricingInfo"]["ticketingAirline"] == "UA":
            tA = {
                "airline": "United Airlines",
                "fare": i["pricingInfo"]["totalFare"]
            }
            if tA not in tR:
                tR.append(tA)
        elif i["pricingInfo"]["ticketingAirline"] == "DL":
            tA = {
                "airline": "Delta Airlines",
                "fare": i["pricingInfo"]["totalFare"]
            }
            if tA not in tR:
                tR.append(tA)

    return {
        "data": tR
    }
