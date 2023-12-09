from flask import Flask, request, render_template,session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

# Database setup
import mysql.connector 

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="4044",
    database="project"
)

# App config
app = Flask(__name__)

# Session config 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Routes
@app.route("/" , methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if session.get("user_id"):      
            return render_template("index.html")
        
        else:
            return redirect("/login")
        
    if request.method == "POST":
        q = request.form.get("q")

        cur = db.cursor(buffered=True)
        query = "SELECT * FROM locations WHERE location_name LIKE %s"
        data = (str(q)+"%", ) #Temp MIGHT HAVE TO CHANGE LATER
        cur.execute(query, data) 
        search_result = cur.fetchall()

        cur.close()

        return render_template("search.html", search_result=search_result, q=str(q))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":
        email = request.form.get("email")
        user_name = request.form.get("username")
        password = request.form.get("password")
        password_again = request.form.get("password_again")
        user_type = request.form.get("user_type")

        if user_type not in ["V", "R"]:
            session["error_massage"] = "Invalid user type."
            return redirect("/apology")

        if not password or not password_again or not user_name or not email or not user_type:
            session["error_massage"] = "Please fill out all the required fields."
            return redirect("/apology")

        if password != password_again:
            session["error_massage"] = "Confirmation password doesn't match."
            return redirect("/apology")
        
        cur = db.cursor(buffered=True)

        query = "INSERT INTO users (user_name, email, password_hash, user_type) VALUES (%s, %s, %s, %s)"
        data =  (user_name, email, str(generate_password_hash(password)), user_type)
        cur.execute(query, data)
        
        db.commit()
        cur.close()

        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect("index")

    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        identification = request.form.get("identification")
        password = request.form.get("password")

        if not identification:
            session["error_massage"] = "Must provide username or email"
            return redirect("/apology")

        if not password:
            session["error_massage"] = "Must provide password"
            return redirect("/apology")

        cur = db.cursor(buffered=True)

        query = "SELECT * FROM users WHERE user_name = %s OR email = %s"
        data = (identification, identification)
        cur.execute(query, data)
        
        if cur.rowcount == 0:
            session["error_massage"] = "Invalid username or email"
            return redirect("/apology")
        
        user = cur.fetchall()[0]

        #user[3] = password_hash
        if check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["user_type"] = user[4]

        else:
            session["error_massage"] = "incorrect password"
            return redirect("/apology")
    
        cur.close()
        return redirect("/")
        
        
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/apology")
def apology():
    error_massage = session.get("error_massage", "Unknown error")
    session["Unknown error"] = None
    return render_template("apology.html", error_massage=error_massage)


# Location
@app.route("/add_location", methods=["GET", "POST"])
def add_location():
    if not session.get("user_id"):
        return redirect("/")

    if request.method == "GET":
        return render_template("add_location.html")
    
    if request.method == "POST":
        location_name = request.form.get("location_name")
        description = request.form.get("description")

        if not location_name:
            session["error_massage"] = "You must enter a location name."
            return redirect("/apology")
                
        cur = db.cursor(buffered=True)

        try:            
            if description:
                query = "INSERT INTO locations (user_id, location_name, description) VALUES (%s, %s, %s)"
                data = (session.get("user_id"), location_name, description)    
                cur.execute(query, data)
            
            else:
                query = "INSERT INTO locations (user_id, location_name) VALUES (%s, %s)"
                data = (session.get("user_id"), location_name)
                cur.execute(query, data)
        
        except:
            session["error_massage"] = "Location name must be less then 255 and description must be less then 6000 characters long"
            return redirect("/apology")
            
        db.commit()
        cur.close()

    return redirect("/")


@app.route("/edit_location", methods=["POST"])
def edit_location():
    if request.method == "POST":
        location_id = request.form.get("location_id")
        
        if not location_id:
            session["error_massage"] = "Must provide location ID"
            return redirect("/apology")
        
        cur = db.cursor(buffered=True)

        query = "SELECT * FROM locations WHERE location_id = %s"
        data = (int(location_id), )
        cur.execute(query, data)

        location = cur.fetchall()[0]
        cur.close()

        if location[1] != session["user_id"]:
            session["error_massage"] = "Only the person who uploaded the location can make chnages to it"
            return redirect("/apology")
        
        location_data = {
            "location_id" : location[0],
            "location_name" : location[2],
            "description" : location[3],
            "latitude" : location[4],
            "longitude" : location[5],
        }

        return render_template("edit_location.html", location_data=location_data)
    

@app.route("/edit_location_function", methods=["POST"])
def edit_location_function():
    location_id = request.form.get(location_id)
    description = request.form.get(description)
    latitude = request.form.get(latitude)
    longitude = request.form.get(longitude)

    if len(description) > 6000:
        session["error_massage"] = "Description must be less then 6000 characters long"
        return redirect("/apology")
    
    #TODO DO THE UPDATE LOCATIOIN QUREY

    return redirect("view", location_id=location_id)
    

# View
@app.route("/view")
def view():
    
    location_id = request.args.get("location_id")

    if not location_id:
        session["error_massage"] = "Must provide a valid location ID"
        return redirect("/apology")
    
    cur = db.cursor(buffered=True)

    try:
        query = "SELECT * FROM locations WHERE location_id = %s"
        data = (int(location_id), )
        cur.execute(query, data)

        if cur.rowcount == 0:
            session["error_massage"] = "The location you are requesting does not exist"
            cur.close()
            return redirect("/apology")
        location_data = cur.fetchall()[0] 
        cur.close()
    
    except:
        session["error_massage"] = "The location you are requesting does not exist"
        return redirect("/apology")

    cur = db.cursor(buffered=True)
    
    query = "SELECT * FROM data WHERE location_id = %s ORDER BY date_submitted DESC"
    data = (int(location_id), )
    cur.execute(query, data)

    if cur.rowcount == 0:
        parameter_data = None
        date = None
    
    else:
        data_tupe = cur.fetchall()[0]
        cur.close()
        date = data_tupe[3]
        parameter_data = [
            ("Ph" , data_tupe[4]),
            ("BOD" , data_tupe[5]),
            ("COD" , data_tupe[6]),
            ("Temperature" , data_tupe[7]),
            ("Ammonia" , data_tupe[8]),
            ("Arsenic" , data_tupe[9]),
            ("Calcium" , data_tupe[10]),
            ("EC" , data_tupe[11]),
            ("Coliform" , data_tupe[12]),
            ("Hardness" , data_tupe[13]),
            ("Lead" , data_tupe[14]),
            ("Nitrogen" , data_tupe[15]),
            ("Sodium" , data_tupe[16]),
            ("Sulfate" , data_tupe[17]),
            ("Tss" , data_tupe[18]),
            ("Turbidity" , data_tupe[19])
        ]    

    session["location_id"] = location_data[0]
    return render_template("view.html", location_data=location_data, parameter_data=parameter_data, date=date)


# Support
@app.route("/support") # All the supports that a user has submited
def support():
    # return all the support ticket submitted
    return render_template("support.html")


@app.route("/support_form", methods=["GET", "POST"]) # Support form and support form input handaling
def submit_support():
    if request.method == "GET":
        return render_template("support_form.html")

    if request.method == "POST":
        return "YOUR SUPPORT IS SUBMITTED (TODO)"


@app.route("/support_view") # Users view of support ticket and masseging
def support_view(): 
    return render_template("support_view.html")


# Support : Admin page
@app.route("/view_support_ticket_admin") # Admins view of all the supports that a users of the site has submitted
def view_support_ticket_admin():
    return render_template("view_support_ticket_admin.html")


# Admis view of the support ticket and messging also a closing buttion
@app.route("/support_view_admin")
def support_view_admin():
    return render_template("support_view_admin.html")


@app.route("/add_data",  methods=["GET", "POST"])
def add_data():
    if request.method == "GET":
        return render_template("add_data.html")
    
    if request.method == "POST":        
        user_id = session.get("user_id")
        location_id = session.get("location_id")
    
        ph = request.form.get("ph")
        bod = request.form.get("bod")
        cod = request.form.get("cod")
        temperature = request.form.get("temperature")
        ammonia = request.form.get("ammonia")
        arsenic = request.form.get("arsenic")
        calcium = request.form.get("calcium")
        ec = request.form.get("ec")
        coliform = request.form.get("coliform")
        hardness = request.form.get("hardness")
        lead_pb = request.form.get("lead_pb")
        nitrogen = request.form.get("nitrogen")
        sodium = request.form.get("sodium")
        sulfate = request.form.get("sulfate")
        tss = request.form.get("tss")
        turbidity = request.form.get("turbidity")

        cur = db.cursor(buffered=True)

        query = "INSERT INTO data (location_id, user_id, ph, bod, cod, temperature, ammonia, arsenic, calcium, ec, coliform, hardness, lead_pb, nitrogen, sodium, sulfate, tss, turbidity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (location_id, user_id, ph, bod, cod, temperature, ammonia, arsenic, calcium, ec, coliform, hardness, lead_pb, nitrogen, sodium, sulfate, tss, turbidity)

        cur.execute(query, data)

        db.commit()
        cur.close()

        return redirect(url_for("view", location_id=location_id))


@app.route("/all_location_data")
def all_location_data():
    location_id = session["location_id"]

    cur = db.cursor(buffered=True)

    query = "SELECT * FROM data WHERE location_id = %s ORDER BY date_submitted DESC"
    data = (int(location_id), )
    cur.execute(query, data)

    location_data = cur.fetchall()
    cur.close()

    return render_template("all_location_data.html", location_data=location_data)


@app.route("/view_data")
def view_data():
    location_id = session.get("location_id")
    data_id = request.args.get("data_id")

    try:
        cur = db.cursor(buffered=True)

        query = "SELECT * FROM locations WHERE location_id = %s LIMIT 1"
        data = (int(location_id), )
        cur.execute(query, data)

        location_data = cur.fetchall()[0]
        cur.close()

        cur = db.cursor(buffered=True)

        query = "SELECT * FROM data WHERE data_id = %s AND location_id = %s LIMIT 1"
        data = (int(data_id), int(location_id))
        cur.execute(query, data)

        data_tupe = cur.fetchall()[0]
        cur.close()

        date = data_tupe[3]
        parameter_data = [
            ("Ph" , data_tupe[4]),
            ("BOD" , data_tupe[5]),
            ("COD" , data_tupe[6]),
            ("Temperature" , data_tupe[7]),
            ("Ammonia" , data_tupe[8]),
            ("Arsenic" , data_tupe[9]),
            ("Calcium" , data_tupe[10]),
            ("EC" , data_tupe[11]),
            ("Coliform" , data_tupe[12]),
            ("Hardness" , data_tupe[13]),
            ("Lead" , data_tupe[14]),
            ("Nitrogen" , data_tupe[15]),
            ("Sodium" , data_tupe[16]),
            ("Sulfate" , data_tupe[17]),
            ("Tss" , data_tupe[18]),
            ("Turbidity" , data_tupe[19])
        ] 


    except:
        session["error_massage"] = "API abuse or SQL erro please contact the admins"
        return redirect("/apology")

    return render_template("view.html", location_data=location_data, parameter_data=parameter_data, date=date)


@app.route("/compare_between_data", methods=["GET", "POST"])
def compare_between():
    if request.method == "GET":
        location_id = session.get("location_id")

        cur = db.cursor(buffered=True)

        query = "SELECT * FROM data WHERE location_id = %s ORDER BY date_submitted DESC"
        data = (int(location_id), )
        cur.execute(query, data)

        data_list = cur.fetchall()
        cur.close()

        return render_template("compare_between.html", data_list=data_list)
    
    if request.method == "POST":
        location_id = session.get("location_id")
        data_id_1 = request.form.get("data_id_1")
        data_id_2 = request.form.get("data_id_2")

        compare_in = request.form.get("compare_in")

        # Getting location data
        cur = db.cursor(buffered=True)

        query = "SELECT * FROM locations WHERE location_id = %s"
        data = (int(location_id), )

        cur.execute(query, data)
        location_data = cur.fetchall()[0]
        cur.close()

        # Getting data for data_id_1
        cur = db.cursor(buffered=True)

        query = "SELECT * FROM data WHERE data_id = %s"
        data = (int(data_id_1), )

        cur.execute(query, data)
        data_tupe = cur.fetchall()[0]
        cur.close()

        # Getting data for data_id_2
        cur = db.cursor(buffered=True)

        query = "SELECT * FROM data WHERE data_id = %s"
        data = (int(data_id_2), )

        cur.execute(query, data)
        data_tupe_2 = cur.fetchall()[0]
        cur.close()
        date = [data_tupe[3], data_tupe_2[3]]
      
        if compare_in == "table":
            parameter_data = [
            ("Ph" , data_tupe[4], data_tupe_2[4]),
            ("BOD" , data_tupe[5], data_tupe_2[5]),
            ("COD" , data_tupe[6], data_tupe_2[6]),
            ("Temperature" , data_tupe[7], data_tupe_2[7]),
            ("Ammonia" , data_tupe[8], data_tupe_2[8]),
            ("Arsenic" , data_tupe[9], data_tupe_2[9]),
            ("Calcium" , data_tupe[10], data_tupe_2[10]),
            ("EC" , data_tupe[11], data_tupe_2[11]),
            ("Coliform" , data_tupe[12], data_tupe_2[12]),
            ("Hardness" , data_tupe[13], data_tupe_2[13]),
            ("Lead" , data_tupe[14], data_tupe_2[14]),
            ("Nitrogen" , data_tupe[15], data_tupe_2[15]),
            ("Sodium" , data_tupe[16], data_tupe_2[16]),
            ("Sulfate" , data_tupe[17], data_tupe_2[17]),
            ("Tss" , data_tupe[18], data_tupe_2[18]),
            ("Turbidity" , data_tupe[19], data_tupe_2[19])
            ]

            return render_template("table_compare.html", location_data=location_data , parameter_data=parameter_data, date=date)
        
        if compare_in == "graph":
            #TODO
            # Missing 4 paramiters, add them later
            location_1_data = {
            "ph": data_tupe[4],
            "temp": data_tupe[7],
            "bod": data_tupe[5],
            "cod": data_tupe[6],
            "calcium": data_tupe[10],
            "coliform": data_tupe[12],
            "hardness": data_tupe[13],
            "lead": data_tupe[14],
            "nitrogen": data_tupe[15],
            "sodium": data_tupe[16],
            "tss": data_tupe[18],
            "turbidity": data_tupe[19]
            }

            location_2_data = {
            "ph": data_tupe_2[4],
            "temp": data_tupe_2[7],
            "bod": data_tupe_2[5],
            "cod": data_tupe_2[6],
            "calcium": data_tupe_2[10],
            "coliform": data_tupe_2[12],
            "hardness": data_tupe_2[13],
            "lead": data_tupe_2[14],
            "nitrogen": data_tupe_2[15],
            "sodium": data_tupe_2[16],
            "tss": data_tupe_2[18],
            "turbidity": data_tupe_2[19]
            }
            date_dic = {
                "left" : date[0],
                "right" : date[1]
            }
            return render_template("graph_compare.html", location_1_data=location_1_data, location_2_data=location_2_data, date_dic=date_dic)
