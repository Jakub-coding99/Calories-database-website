from food_oop import CalorieCounter
from flask import Flask, render_template, url_for, request, redirect, session
from flask_bootstrap import Bootstrap5
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from models import db,DailyCalories, DailyMeals, Users, UserStats, UserSettings
from auth.auth import auth_bp
from flask_login import LoginManager,current_user
import os

calorie_counter = CalorieCounter()


app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.register_blueprint(auth_bp)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("secret_key")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db.init_app(app)


# Uncomment to create database
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


def all_food():
    with app.app_context():
        u_id = get_user_id()
        food_all = db.session.query(DailyMeals).filter_by(user = u_id).all()
        
    
    return food_all

def get_user_id():
    try:
        if current_user.id > 0:
            return current_user.id
    except AttributeError:
        return 0
 

@app.route("/")
def home():
    
    now = datetime.datetime.now()
    year = now.year
    found_food = session.get("food", None)
    food_not_found = session.get("food_not_found", None)
    
    if not found_food and not food_not_found:
        food_info  = { "name" : "-","porcion" : "-","calories" : "-","protein" : "-","carbs" : "-","sugar" : "-","fat" :  "-","fiber" : "-" }
    
    elif not found_food:
        food_info = food_not_found
        session.pop("food_not_found", None)
    else: 
        food_info = found_food
        session.pop("food", None)

    add_hour = int(datetime.datetime.now().strftime("%H"))
    food = all_food()
    
   
    
    all_nutrients = macro()
    personal = personal_macro_perc()
    daily_personal_kcal = define_user_macro()



    
    return render_template("home.html",  food = food, add_hour = add_hour, all_nutrients = all_nutrients, personal = personal,
                            daily_personal_kcal = daily_personal_kcal, user = current_user, food_info = food_info, year = year  )

@app.route("/profile", methods = ["GET", "POST"])
def my_profile():
    d = request.args.get("d")
    daily_personal_kcal = define_user_macro()
    if request.method == "POST":
        if request.form.get("form") == "form1":
            profile_stats = {
                "user" : current_user.id,
                "goal" : request.form.get("goal"),
                "gender" : request.form.get("gender"),
                "age":  request.form.get("age"),
                "height" : request.form.get("height"),
                "weight" : request.form.get("weight"),
                "activity" : request.form.get("activity"),
                

            }   
            
            new_stat = UserStats(
                user = profile_stats["user"],goal = profile_stats["goal"],gender=profile_stats["gender"],
                age = profile_stats["age"], height= profile_stats["height"], weight= profile_stats["weight"],
                activity=profile_stats["activity"]
                                )
            db.session.add(new_stat)
            db.session.commit()
            return redirect(url_for("my_profile"))
            
        elif request.form.get("form") == "form2":
            session["personal_macro"] = {
            
            "kcal" : request.form.get("kcal"),
            "protein" : request.form.get("protein"),
            "carbs":  request.form.get("carbs"),
            "fat" : request.form.get("fat"),
            "fiber" : request.form.get("fiber"), 

        }     
            user_updated_macro = session.get("personal_macro", None)
            if user_updated_macro:           
                u_id = get_user_id()
                now =datetime.datetime.now()
                
                personal = {
                                "calories" : int(user_updated_macro["kcal"]),
                                "proteins" : int(user_updated_macro["protein"]),
                                "carbs" : int(user_updated_macro["carbs"]),
                                "fat" : int(user_updated_macro["fat"]),
                                "fiber" : int(user_updated_macro["fiber"]),
                                    }   
                    
                manual = UserSettings(user=u_id,manual_macro=personal, time_of_update = now)
                db.session.add(manual)
                db.session.commit()
                
                session.pop("personal_macro", None)
                return redirect(url_for("my_profile"))
                
        elif request.form.get("form") == "form3":
            
            day = request.form.get("dailylog")
            
            if day:
                log = check_for_dailylog(day)
                    
                
                return redirect(url_for("my_profile", d = log))
           
                

        

    return render_template("profile_stats.html", user = current_user, macro = daily_personal_kcal, d = d  )




@app.route("/",methods = ["GET", "POST"])
def get_food():
    
    if request.method == "POST":
        data = request.form["food"]
        
        find_food = calorie_counter.find_food(data)
        
        if find_food == "Not found":
            session["food_not_found"] = {
                    "name" : "N/A",
                    "porcion" : "N/A",
                    "calories" : "N/A",
                     "protein" : "N/A",
                    "carbs" : "N/A",
                    "sugar" : "N/A",
                    "fat" :  "N/A",
                    "fiber" : "N/A",
                }
            return redirect(url_for("home"))
        
        
        else: 
            if get_user_id() != 0:
                user_id = get_user_id()
                
                hour_now = datetime.datetime.now().strftime("%H")
                new_meal = DailyMeals(name = find_food["name"], porcion = find_food["porcion"],
                                        calories = int(find_food["calories"]), protein = int(find_food["protein"]),
                                        carbs = int(find_food["carbs"]), sugar = int(find_food["sugar"]) ,
                                        fat = int(find_food["fat"]),fiber = int(find_food["fiber"]),hour_of_update = hour_now, user = user_id)
                db.session.add(new_meal)
                db.session.commit()
                
                
                session["food"] =  {
                    "name" :find_food["name"],
                    "porcion" : find_food["porcion"],
                    "calories" : int(find_food["calories"]),
                     "protein" : int(find_food["protein"]),
                    "carbs" : int(find_food["carbs"]), 
                    "sugar" : int(find_food["sugar"]) ,
                    "fat" :  int(find_food["fat"]),
                    "fiber" : int(find_food["fiber"]),
                }
                
                
                
                return redirect(url_for("home"))
            else:
                session.permanent = False
                session["food"] =  {
                    "name" :find_food["name"],
                    "porcion" : find_food["porcion"],
                    "calories" : int(find_food["calories"]),
                     "protein" : int(find_food["protein"]),
                    "carbs" : int(find_food["carbs"]), 
                    "sugar" : int(find_food["sugar"]) ,
                    "fat" :  int(find_food["fat"]),
                    "fiber" : int(find_food["fiber"]),
                }
                
                return redirect(url_for("home"))

                

def getting_all_users_content():
    with app.app_context():
        u = []
        all_users = db.session.query(DailyMeals).all()
        if all_users:
            for user in all_users:
                u.append(user.user)
                users = list(set(u))
                return users
        else:
            return 0

def check_for_dailylog(choosen_day):
    u_id = get_user_id()
    
    try:
        datetime_date = datetime.datetime.strptime(choosen_day, "%d/%m/%Y").date()
        check_db = db.session.query(DailyCalories).filter_by(user = u_id, day =  datetime_date).first()
        print(type(check_db.total_calories))
        return f"Total calories for this day: <span style = 'color:#0E2E50; font-weight:bold'>{check_db.total_calories}<span>"
    
    except (ValueError, AttributeError):
        return "No calories record found for this day."
    
    


def daily_count_calories():
    daily_kcal = []
    
    today_date = datetime.datetime.now()
    if getting_all_users_content() != 0:
        for u in getting_all_users_content():
            with app.app_context():
                
                
                all_meals = db.session.query(DailyMeals).filter_by(user = u).all()
                if all_meals:
                    for kcal in all_meals:
                        daily_kcal.append(kcal.calories)
                    all_daily_kcal = sum(daily_kcal)
                    daily_kcal.clear()
                    
                    daily_calories = DailyCalories(total_calories= all_daily_kcal, day = today_date,  user = u)
                    db.session.add(daily_calories)
                    db.session.flush()
                    db.session.query(DailyMeals).filter_by(user = u).delete()
                    db.session.commit()
    else:
        pass


def macro():
    import math
    f = all_food()
    all_macro = []
    for m in f:
        macros = {
             "cal" : m.calories,
            "protein" : m.protein,
            "carbs" : m.carbs,
            "fat" : m.fat,
            "fiber" : m.fiber,
        }
        all_macro.append(macros)
    
    cal = [cal["cal"] for cal in all_macro]
    cal_sum = math.fsum(cal)
    
    protein = [protein["protein"] for protein in all_macro]
    protein_sum = math.fsum(protein)

    carb = [carb["carbs"] for carb in all_macro]
    carb_sum = math.fsum(carb)

    fat = [fat["fat"] for fat in all_macro]
    fat_sum = math.fsum(fat)

    fiber = [fiber["fiber"] for fiber in all_macro]
    fiber_sum = math.fsum(fiber)

    all_nutrients = {

        "calories" : int(cal_sum),
        "proteins" : int(protein_sum),
        "carbs" : int(carb_sum),
        "fat" : int(fat_sum),
        "fiber" : int(fiber_sum)
    }
    
    return all_nutrients




def find_one():
    u_id = get_user_id()
    
    try:
        with app.app_context():
            user_stat = db.session.query(UserStats).filter_by(user = u_id).all()
            user_setting = db.session.query(UserSettings).filter_by(user = u_id).all()
            now = datetime.datetime.now()
            
            latest_setting = min(user_setting, key=lambda x: abs(x.time_of_update - now)) if user_setting else None
            latest_stat = min(user_stat, key=lambda x: abs(x.time_of_update - now)) if user_stat else None
            
          
            candidates = [x for x in [latest_stat, latest_setting] if x is not None]
            
            if not candidates:
                return None
            
            find_recent = min(candidates, key=lambda x: abs(x.time_of_update - now))
            return find_recent
            
    
    except ValueError:
        return None

        
        

        
def sort_delete(result, to_delete):
    
    u_id = get_user_id()
    model = type(result)
    all_db = db.session.query(model).filter_by(user = u_id).all()
    for stat in all_db:
        if result.id != stat.id:
            db.session.delete(stat)
    db.session.query(to_delete).filter_by(user = u_id).delete()
    db.session.commit()

def define_user_macro():
    u_id = get_user_id()

    sedentary = 1.2
    moderately_active = 1.5
    very_active = 1.75
    extra_active = 2.0

    if u_id != 0:
        try:
            result = find_one()
            typ = type(result).__name__
            if result:
                if typ == "UserSettings":
                    sort_delete(result,UserStats)
                    macro = result.manual_macro
                    return macro
                else:
                    sort_delete(result,UserSettings)
                    x = result.to_dict()
                        
           
            if "Sedentary" in x["activity"]:
                act = sedentary
            elif "Moderately Active" in x["activity"]:
                act = moderately_active  
            elif "Very Active" in x["activity"]:
                act = very_active
            else:
                act = extra_active
                
            
            bmr = (10 * x["weight"]) + (6.25 * x["height"])
            
            if x["gender"] == "Male":
                bmr -=  (5 * x["age"] - 5)
                bmr *= act
                
                if x["goal"] == "Gain Weight":
                    bmr += 350
                    protein = (bmr / 100) * (30 / 4)
                    carbs = (bmr / 100) * (50 / 4)
                    fat = (bmr / 100) * (20 / 9)

                elif x["goal"] == "Lose Fat":
                    bmr -= 350
                    protein = (bmr / 100) * (40 / 4)
                    carbs = (bmr / 100) * (30 / 4)
                    fat = (bmr / 100) * (30 / 9)
                
                else:
                    protein = (bmr / 100) * (30 / 4)
                    carbs = (bmr / 100) * (40 / 4)
                    fat = (bmr / 100) * (30 / 9)
            
            
            else:
                bmr -= (5 * x["age"] - 161) 
                bmr *= act
                
                if x["goal"] == "Gain Weight":
                    bmr += 350
                    protein = (bmr / 100) * (30 / 4)
                    carbs = (bmr / 100) * (50 / 4)
                    fat = (bmr / 100) * (20 / 9)

                elif x["goal"] == "Lose Fat":
                    bmr -= 350
                    protein = (bmr / 100) * (40 / 4)
                    carbs = (bmr / 100) * (30 / 4)
                    fat = (bmr / 100) * (30 / 9)
                
                else:
                    protein = (bmr / 100) * (30 / 4)
                    carbs = (bmr / 100) * (40 / 4)
                    fat = (bmr / 100) * (30 / 9)


            personal = {
                        "calories" : int(bmr),
                        "proteins" : int(protein),
                        "carbs" : int(carbs),
                        "fat" : int(fat),
                        "fiber" : 30
                                    }   
            return personal
            
        
        except (AttributeError, TypeError, KeyError, UnboundLocalError):
            return None
        


def personal_macro_perc():
    all_macro = macro()
    pers_macro = define_user_macro()
    
    if pers_macro != None:
    
        a = int(all_macro["calories"] / pers_macro["calories"] * 100)
        b = int(all_macro["proteins"] / pers_macro["proteins"] * 100)
        c = int(all_macro["carbs"] / pers_macro["carbs"] * 100)
        d = int(all_macro["fat"] / pers_macro["fat"] * 100)
        e = int(all_macro["fiber"] / pers_macro["fiber"] * 100)
        user_macro = {

            "calories" : a,
            "proteins" : b,
            "carbs" : c,
            "fat" : d,
            "fiber" : e

        }
        
        return user_macro
    return None


    

def automatic_database():
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily_count_calories, "cron", hour = 23, minute = 59, second = 59)
    scheduler.start()

@app.route("/delete/<int:meal_id>")       
def delete_meal(meal_id):
    selected_meal = db.session.query(DailyMeals).get(meal_id)
    db.session.delete(selected_meal)
    db.session.commit()
    return redirect(url_for("home"))


if app.name == "main":
    automatic_database()
    
    app.run(debug=True, use_reloader = False)
   
