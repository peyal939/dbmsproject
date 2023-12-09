import mysql.connector 

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="01617277318",
    database="test"
)

cur = db.cursor()

cur.execute("SELECT * FROM locations")

print(cur.fetchall()[1][3])
