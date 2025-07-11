from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime


db = SQLAlchemy()


class DailyMeals(db.Model):
    __tablename__ = "daily_meals"
    id = db.Column(db.db.Integer, primary_key=True)
    name = db.Column(db.String)
    porcion = db.Column(db.String)
    calories = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    sugar = db.Column(db.Integer)
    fat = db.Column(db.Integer)
    fiber = db.Column(db.Integer)
    hour_of_update = db.Column(db.Integer)
    user = db.Column(db.Integer)
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
    id = db.Column(db.Integer, primary_key=True)
    total_calories = db.Column(db.Integer)
    day = db.Column(db.Date)
    
    user = db.Column(db.Integer)
    def __init__(self, total_calories, day, user):
        self.total_calories = total_calories
        self.day = day
        self.user = user


class Users(db.Model, UserMixin):
    id = db.Column( db.Integer, primary_key=True)
    user_name = db.Column(db.String,unique= True ,nullable = False)
    email = db.Column(db.String,unique= True ,nullable = False)
    password1 = db.Column(db.String, unique= True,nullable = False)
    

    def __init__(self, user_name,email, password1):
        self.user_name = user_name
        self.email = email
        self.password1 = password1
        
class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer)
    goal = db.Column(db.String)
    gender = db.Column(db.String)
    age = db.Column(db.Integer)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    activity = db.Column(db.String)
    time_of_update = db.Column(db.DateTime, default = datetime.datetime.now)
    manual_macros = db.Column(db.JSON)

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
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer)
    manual_macro = db.Column(db.JSON)
    time_of_update = db.Column(db.DateTime, default = datetime.datetime.now)
