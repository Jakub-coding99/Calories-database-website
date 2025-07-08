
from sqlalchemy import Column, Integer, String, Date, JSON, DateTime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime


db = SQLAlchemy()


class DailyMeals(db.Model):
    __tablename__ = "daily_meals"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    porcion = Column(String)
    calories = Column(Integer)
    protein = Column(Integer)
    carbs = Column(Integer)
    sugar = Column(Integer)
    fat = Column(Integer)
    fiber = Column(Integer)
    hour_of_update = Column(Integer)
    user = Column(Integer)
    def __init__(self, name, porcion, calories, protein, carbs, sugar, fat,fiber,hour_of_update, user):
        self.name = name
        self.porcion = porcion
        self.calories = calories
        self.protein = protein
        self.carbs  = carbs
        self.sugar = sugar
        self.fat = fat
        self.fiber = fiber
        self.hour_of_update = hour_of_update
        self.user = user

class DailyCalories(db.Model):
        
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    total_calories = Column(Integer)
    day = Column(Date)
    
    user = Column(Integer)
    def __init__(self, total_calories, day, user):
        self.total_calories = total_calories
        self.day = day
        self.user = user


class Users(db.Model, UserMixin):
    id = Column( Integer, primary_key=True)
    user_name = Column(String,unique= True ,nullable = False)
    email = Column(String,unique= True ,nullable = False)
    password1 = Column(String, unique= True,nullable = False)
    

    def __init__(self, user_name,email, password1):
        self.user_name = user_name
        self.email = email
        self.password1 = password1
        
class UserStats(db.Model):
    id = Column(Integer, primary_key=True)
    user = Column(Integer)
    goal = Column(String)
    gender = Column(String)
    age = Column(Integer)
    height = Column(Integer)
    weight = Column(Integer)
    activity = Column(String)
    time_of_update = Column(DateTime, default = datetime.datetime.now)
    manual_macros = Column(JSON)

    def __init__(self, user, goal, gender, age, height, weight, activity):
        self.user = user
        self.goal = goal
        self.gender = gender
        self.age = age
        self.height = height
        self.weight = weight
        self.activity = activity
        
    def to_dict(self):
        return {
            "goal" : self.goal,
            "gender" : self.gender,
            "age" : self.age,
            "height":self.height,
            "weight" : self.weight,
            "activity":self.activity,
            "time_of_update" : self.time_of_update


        }

class UserSettings(db.Model):
    id = Column(Integer, primary_key = True)
    user = Column(Integer)
    manual_macro = Column(JSON)
    time_of_update = Column(DateTime, default = datetime.datetime.now)
