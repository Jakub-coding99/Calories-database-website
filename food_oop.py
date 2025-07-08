import requests

from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)



# raw api data can be stored in database for max of 24h
class CalorieCounter:
    def __init__(self):
        self.API_ID = os.getenv("API_ID")
        self.API_KEY = os.getenv("API_KEY")
        self.URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
   
   
   
    def find_food(self, food_with_amount):
        headers =  {
            "Content-Type": 'application/x-www-form-urlencoded',
            "x-app-id" : self.API_ID ,
            "x-app-key": self.API_KEY ,
                }

        query = {
            "query" : food_with_amount,
            "timezone" : "Europe/Prague"
        }
        try:
            response = requests.post(url=self.URL, headers=headers,data=query, verify= False )
            data = response.json()
            

            for food in data["foods"]:
                
                
                
                food_info = {
                    "name" : food["food_name"],
                    "porcion" : f"{food.get('serving_qty', 0)}{food.get('serving_unit', '')}",
                    "calories" :  food["nf_calories"],
                    "protein" : food["nf_protein"],
                    "carbs" : food["nf_total_carbohydrate"],
                    "sugar" : food ["nf_sugars"],
                    "fat" : food["nf_total_fat"],
                    "fiber" : food["nf_dietary_fiber"]
                }
        except KeyError:
            return "Not found"
            
        
        
        for key,value in food_info.items():
           
            if value == None:
                food_info[key] = 0
           
        
        
       

        return food_info



   
   
   
   
   
