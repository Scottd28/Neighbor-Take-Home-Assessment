from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()
#CLASS THAT CONTAINS THE VEHICLES OF THE REQUEST (USES PEDANTIC)
class VehicleRequest(BaseModel):
    length: int
    quantity: int

#LOAD ALL LISTINGS
parking_locations = {}
DATA_PATH = "listings.json"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError("listings.json not found in project root")

#GET THE LISTINGS
with open(DATA_PATH, "r") as f:
    LISTINGS = json.load(f)

#create a Dictionary that has all the parking locations and that contains all parking spots per location
for spot in LISTINGS:
    location_id = spot["location_id"]
    if location_id in parking_locations.keys(): # if we already have that parking spot in our dictionary
        parking_locations[location_id].append((spot["id"], spot["length"], spot["width"], spot["price_in_cents"]))
    else:
        parking_locations[location_id] = [[spot["id"], spot["length"], spot["width"], spot["price_in_cents"]]]

# POST endpoint

@app.post("/")

def find_locations(vehicles: List[VehicleRequest]):
    """
    List[Vehicle Request] is the users vehicles that they need to find parking spots for
    This function will eventually:
    - process the vehicle request
    - find all locations that can store them
    - compute cheapest combinations
    - return sorted results
    """

    #update vehicles so you can have a list of all vehicles
    list_of_vehicles = []
    final_locations= []
    for vehicle in vehicles:
        for _ in range(vehicle.quantity):
            list_of_vehicles.append((vehicle.length, 10)) # add all teh vehicle height ad width


    #figures out what locations can fit all vehicles
    '''
    SPOTS
    location_id = the parking location
    spot[0] = spot in the parking location
    spot[1] = length
    spot[2] = width
    spot[3] = price_in_cents
    
    VEHICLES
    vehicles[0] = length
    vehicles[1] = width
    '''
    for location_id, list_of_spots in parking_locations.items(): #for each location and its  list of values per spot
        list_of_spots = sorted(list_of_spots, key=lambda x: x[3])  # get the cheapest spots first
        succesful_locations = 0
        price_location = 0
        chosen_spots = []
        for vehicle in list_of_vehicles:
            for index, spot in enumerate(list_of_spots):
                if spot[1] >= vehicle[0] and spot[2] >= vehicle[1]: #if the vehicle fits in the parking spot
                    succesful_locations += 1
                    price_location += spot[3]
                    parked_spot = list_of_spots.pop(index)
                    chosen_spots.append(parked_spot[0])
                    break



        if(succesful_locations == len(list_of_vehicles)): #if all cars where parked succesfully
            final_locations.append({  "location_id": location_id,
            "listing_ids": chosen_spots,
            "total_price_in_cents": price_location})



    final_locations.sort(key=lambda x: x["total_price_in_cents"])
    return final_locations
