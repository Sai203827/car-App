from flask import Flask,request,redirect,render_template,url_for,flash,session,send_file
import mysql.connector
from flask_mysqldb import MySQL
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_session import Session
from otp import genotp
from cmail import sendmail
import random
import stripe
from tokenreset import token
import os
from io import BytesIO
stripe.api_key='sk_test_51N0NrXSJwdQx8caK7N1qOMe4uYYL9VmVpRwIpZuN4vmCEJBJ92P6pe6hIZX7NK9HptfNQBbJaCy3nB0Gq7j9hXxI00igK2ZeMv'
app=Flask(__name__)
db=os.environ['RDS_DB_NAME']
user=os.environ['RDS_USERNAME']
password=os.environ['RDS_PASSWORD']
host=os.environ['RDS_HOSTNAME']
port=os.environ['RDS_PORT']
mydb=mysql.connector.connect(host=host,user=user,password=password,db=db,port=port)
#mydb=mysql.connector.connect(host='localhost',user='root',password='admin',db='db_name')
with mysql.connector.connect(host=host,user=user,password=password,db=db,port=port) as conn:
    cursor=conn.cursor()
    cursor.execute('CREATE TABLE if not exists admin (mobile varchar(50) primary key, password varchar(50),email varchar(50))')
    cursor.execute('CREATE TABLE if not exists cars(carid varchar(8) primary key,carname varchar(50),carno varchar(50),caryear  varchar(50),category varchar(50), carmodel varchar(50), milage varchar(50),price varchar(50),description tinytext, mobile varchar(50))')
    cursor.execute('CREATE TABLE if not exists register (emailid varchar(50), username varchar(20),mobile varchar(10) primary key,dob date, password varchar(50), filename varchar(50), licencecard longblob)')
    cursor.execute('CREATE TABLE if not exists rent (rentid int auto_increment,carid varchar(30), carname char(30),check_in varchar(50), check_out varchar(50),total_price int, mobile varchar(50), qty int,foreign key(carid) references cars(carid) on update cascade on delete cascade,foreign key(mobile) refernces register(mobile)')
   
mydb=mysql.connector.connect(host='localhost',user='root',password='admin',db='car')
Session(app)
mysql=MySQL(app)
@app.route('/')
def main():
    return render_template('main.html')
@app.route('/admin1',methods=['GET','POST'])
def admin1():
    return render_template('admin.html')
@app.route('/registration',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        emailid=request.form['emailid']
        username=request.form['username']
        mobile=request.form['mobile']
        dob=request.form['dob']
        password=request.form['password']
        licencecard=request.files['licencecard']
        filename=licencecard.filename

        cursor=mysql.connection.cursor()
        cursor.execute('select mobile from register')
        data=cursor.fetchall()
        cursor.execute('SELECT emailid from register')
        edata=cursor.fetchall()
        #print(data)
        if (mobile,) in data:
            flash('User already already exists')
            return render_template('SignUp.html')
        if (licencecard,) in edata:
            flash('Email id already already exists')
            return render_template('SignUp.html')
        cursor.close()
        otp=genotp()
        subject='Thanks for registering to the application'
        body=f'Use this otp to register {otp}'
        sendmail(emailid,subject,body)
        session['filedata']=licencecard.read()
        return render_template('otp.html',otp=otp,emailid=emailid,username=username,mobile=mobile,dob=dob,password=password,filename=filename)

    else:

        return render_template('SignUp.html') 
    return render_template('SignUp.html')
@app.route('/login',methods=['GET','POST'])
def login():
    
    if session.get('user'):
        return redirect(url_for('home'))
    
    if request.method=='POST':
        mobile=request.form['mobile']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from register where mobile=%s and password=%s',[mobile,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid mobile or password')
            return render_template('login.html')
        else:   
            session['user']=mobile
            return redirect(url_for('home'))
        
    return render_template('login.html')


@app.route('/admin',methods=['GET','POST'])
def admin():
    if session.get('admin'):
        return render_template('admin.html')
    if request.method=='POST':
        mobile=request.form['mobile']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from admin where mobile=%s and password=%s',[mobile,password])
        count=cursor.fetchone()[0]
        print(count)
        if count==0:
            flash('Invalid roll no or password')
            return render_template('login.html',data=count)
        else:
            session['user']=mobile
            return redirect(url_for('admin1'))
    return render_template('login.html')
@app.route('/addcars',methods=['GET','POST'])
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
        cursor.execute('insert into cars(carid,carname,carno,caryear,category,carmodel,milage,price,description) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',[id1,name,carno,year,category,model,milage,price,desc])
        mydb.commit()
        
        print(filename)
        path=r"E:\car\project\carrental1\static"
        image.save(os.path.join(path,filename))
        print('success')
    return render_template('cars.html')
@app.route('/rental',methods=['POST','GET'])
def rental():
    cursor=mydb.cursor()
    cursor.execute("select * from cars")
    items=cursor.fetchall()
    return render_template('rentingpage.html',items=items)

'''@app.route('/rent',methods=['POST','GET'])
def rent():
    return redirect(url_for('pay'))'''
@app.route('/location/<carid>',methods=['POST','GET'])
def location(carid):
    if session.get('user'):
       cursor=mydb.cursor()
       cursor.execute("select carname,price from cars  where carid=%s",[carid])
       carname,price=cursor.fetchone()

       return render_template('location.html',carid=carid,carname=carname,price=price)
    else:
        return redirect(url_for('login'))
@app.route('/homepage/')
def homepage():
    cursor=mydb.cursor()
    cursor.execute("select * from cars")
    items=cursor.fetchall()
    return redirect(url_for('rental',items=items))
@app.route('/home')
def home():
    if session.get('user'):
        return render_template('home.html')
    else:
        #implement flash
        return redirect(url_for('login'))
@app.route('/home2')
def home2():
   if session.get('user'):
        return render_template('home2.html')
   else:
        return redirect(url_for('home'))
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/logout')   
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('main'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))
@app.route('/otp/<otp>/<emailid>/<username>/<mobile>/<dob>/<password>/<filename>',methods=['GET','POST'])
def otp(otp,emailid,username,mobile,dob,password,filename):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            licencecard=session['filedata']
            lst=[emailid,username,mobile,dob,password,filename,licencecard]
            query='insert into register values(%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,emailid=emailid,username=username,mobile=mobile,dob=dob,password=password,filename=filename)
@app.route('/forgetpassword',methods=['GET','POST'])
def forget():
    if request.method=='POST':
        mobile=request.form['mobile']
        cursor=mysql.connection.cursor()
        cursor.execute('select mobile from register')
        data=cursor.fetchall()
        if (mobile,) in data:
            cursor.execute('select emailid from register where mobile=%s',[mobile])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the passwword using-{request.host+url_for("createpassword",token=token(mobile,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user id'
    return render_template('forgot.html')

@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        mobile=s.loads(token)['user']
        if request.method=='POST':
            npass=request.form['npassword']
            cpass=request.form['cpassword']
            if npass==cpass:
                cursor=mysql.connection.cursor()
                cursor.execute('update register set password=%s where mobile=%s',[npass,mobile])
                mysql.connection.commit()
                return 'Password reset Successfull'
            else:
                return 'Password mismatch'
        return render_template('newpassword.html')
    except:
        return 'Link expired try again'
@app.route('/booking')
def booking():
    return render_template('booking.html')
@app.route('/edit')
def edit():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from cars')
        cars=cursor.fetchall()
        cursor.close()
        print(cars)  
        return render_template('edit.html', cars=cars)
    return render_template('edit.html')

'''@app.route('/view/<carid>')
def view(carid):
    cursor=mysql.connection.cursor()
    cursor.execute('select carname,carno,caryear,category,carmodel,milage,price,description from cars where carid=%s',[carid])
    data=cursor.fetchone()
    return render_template('cars.html',data=data)
@app.route('/update/<carid>',methods=['GET','POST'])
def update(carid):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select carname,carno,caryear,category,carmodel,milage,price,description from notes where carid=%s',[carid])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
                carname=request.form['carname']
                carno=request.form['carno']
                caryear=request.form['caryear']
                category=request.form['category']
                carmodel=request.form['carmodel']
                milage=request.form['milage']
                price=request.form['price']
                description=request.form['description']

                cursor=mysql.connection.cursor()
                cursor.execute('update notes set carname=%s,carno=%s,caryear=%s,category=%s,carmodel=%s,milage=%s,price=%s,description=%s where carid=%s',[carname,carno,caryear,category,carmodel,milage,price,description])
                mysql.connection.commit()
                cursor.close()
                flash('Notes updated successfully')
                return redirect(url_for('edit'))
                
        return render_template('edit.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/delete/<carid>')
def delete(carid):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from cars where carid=%s',[carid])
    mysql.connection.commit()
    cursor.close()
    flash('Notes deleted successfully')
    return redirect(url_for('edit'))'''
@app.route('/bookings', methods=['POST','GET'])
def bookings():
    if session.get('user'):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM rent")
        rent = cursor.fetchall()
        return render_template('bookings.html', rent=rent)
    return render_template('bookings.html')
@app.route('/pay/',methods=['POST'])
def pay():
    if session.get('user'):
        carid=request.form['carid']
        carname=request.form['carname']
        check_in=request.form['check_in']
        check_out=request.form['check_out']
        price=int(request.form['price'])
        qty=1
        total_price=price*qty
        checkout_session=stripe.checkout.Session.create(
            success_url=url_for('success',carid=carid,carname=carname,price=price,check_in=check_in,check_out=check_out,qty=qty,total_price=total_price,_external=True),
            line_items=[
                {
                    'price_data': {
                        'product_data': {
                            'name': carname,
                        },
                        'unit_amount': price*100,
                        'currency': 'inr',
                    },
                    'quantity': qty,
                },
                ],
            mode="payment",)
        return redirect(checkout_session.url)
    else:
        return redirect(url_for('login'))
@app.route('/success/<carid>/<carname>/<check_in>/<check_out>/<qty>/<total_price>')
def success(carid,carname,check_in,check_out,qty,total_price):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into rent(carid,carname,check_in,check_out,qty,total_price,mobile) values(%s,%s,%s,%s,%s,%s,%s)',[carid,carname,check_in,check_out,qty,total_price,session.get('user')])
        mydb.commit()
        return 'Order Placed'
    return redirect(url_for('login'))
app.run(use_reloader=True,debug=True)

