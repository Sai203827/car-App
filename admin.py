from flask import *
import os
import mysql.connector
from otp import genotp
app=Flask(__name__)
mydb=mysql.connector.connect(host='localhost',user='root',password='admin',db='car')
@app.route('/',methods=['GET','POST'])
def admin_home():
    if request.method=="POST":
        name=request.form['name']
        carno=request.form['carno']
        year=request.form['year']
        category=request.form['category']
        model=request.form['model']
        milage=request.form['milage']
        price=request.form['price']
        desc=request.form['desc']
        image=request.files['image']
        cursor=mydb.cursor()
        id1=genotp()
        filename=id1+'.jpg'
        cursor.execute('insert into cars(carname,carno,caryear,category,carmodel,milage,price,description,carimage) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',[id1,name,carno,year,category,model,milage,price,desc,image])
        mydb.commit()
        
        print(filename)
        path=r"E:\car\project\carrental1"
        image.save(os.path.join(path,filename))
        print('success')
    return render_template('cars.html')
@app.route('/homepage/')
def rentingpage():
    cursor=mydb.cursor()
    cursor.execute("select * from cars")
    items=cursor.fetchall()
    return render_template('rentingpage.html',items=items)
app.run()
