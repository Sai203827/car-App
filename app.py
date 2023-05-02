from flask import Flask,request,redirect,render_template,url_for,flash,session,send_file
import mysql.connector
from flask_mysqldb import MySQL
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_session import Session
from otp import genotp
from cmail import sendmail
import random
from flask_login import LoginManager, login_required
import stripe
from tokenreset import token
import os
from io import BytesIO
stripe.api_key='sk_test_51N0NrXSJwdQx8caK7N1qOMe4uYYL9VmVpRwIpZuN4vmCEJBJ92P6pe6hIZX7NK9HptfNQBbJaCy3nB0Gq7j9hXxI00igK2ZeMv'
app=Flask(__name__)
app.secret_key='*67@hjyjhk'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Sai $123'
app.config['MYSQL_DB']='car-rental'
login_manager = LoginManager()
login_manager.init_app(app)
mydb=mysql.connector.connect(host='localhost',user='root',password='admin',db='car')
Session(app)
mysql=MySQL(app)

@app.route('/')
def main():
    return render_template('main.html')
@app.route('/admin1',methods=['GET','POST'])
def admin1():
    return render_template('dashboard.html')
@app.route('/dashuserdetails')
@login_manager.user_loader
def load_user(mobile):
    # Fetch the user object from the database using the user_id
    return mobile.query.get(int(mobile))

def dashuserdetails():
    if session.get('user'):
        cursor=mydb.cursor()
        cursor.execute('select * from register')
        user=cursor.fetchall()
        cursor.close()
        print(user)  
        return render_template('dashuserdetails.html', user=user)
    return render_template('dashuserdetails.html')
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

        cursor=mydb.cursor()
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
        cursor=mydb.cursor()
        cursor.execute('select count(*) from register where mobile=%s and password=%s',[mobile,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid mobile or password')
            return render_template('login.html')
        else:   
            session['user']=mobile
            return redirect(url_for('home'))
        
    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@app.route('/dashuser', methods=['POST','GET'])
def dashuser():
    return render_template('dashusers.html')
@app.route('/admin',methods=['GET','POST'])
def admin():
    if session.get('admin'):
        return render_template('dashboard.html')
    if request.method=='POST':
        mobile=request.form['mobile']
        password=request.form['password']
        cursor=mydb.cursor()
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
    return render_template('dashusers.html')



@app.route('/rental',methods=['POST','GET'])
def rental():
    if session.get('user'):
        cursor=mydb.cursor()
        cursor.execute("select * from cars")
        items=cursor.fetchall()
        return render_template('rentingpage.html',items=items)
    else:
         return redirect(url_for('login'))
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
@app.route('/contact')
def contact():
    return render_template('contact.html')
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
            cursor=mydb.cursor()
            licencecard=session['filedata']
            lst=[emailid,username,mobile,dob,password,filename,licencecard]
            query='insert into register values(%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mydb.commit()
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
        cursor=mydb.cursor()
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
                cursor=mydb.cursor()
                cursor.execute('update register set password=%s where mobile=%s',[npass,mobile])
                mydb.commit()
                return 'Password reset Successfull'
            else:
                return 'Password mismatch'
        return render_template('newpassword.html')
    except:
        return 'Link expired try again'
@app.route('/booking')
def booking():
    return render_template('booking.html')
@app.route('/dashcartable')
def dashcartable():
    if session.get('user'):
        cursor=mydb.cursor()
        cursor.execute('select * from cars')
        cars=cursor.fetchall()
        cursor.close()
        print(cars)  
        return render_template('dashcartable.html', cars=cars)
    return render_template('dashcartable.html')

@app.route('/view/<carid>')
def view(carid):
    cursor=mydb.cursor()
    cursor.execute('select carname,carno,caryear,category,carmodel,milage,price,description from cars where carid=%s',[carid])
    data=cursor.fetchone()
    return render_template('cars.html',data=data)
@app.route('/update/<carid>',methods=['GET','POST'])
def update(carid):
    if session.get('user'):
        cursor=mydb.cursor()
        cursor.execute('select carname,carno,caryear,category,carmodel,milage,price,description from cars where carid=%s',[carid])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
              name=request.form['name']
              carno=request.form['carno']
              year=request.form['year']
              category=request.form['category']
              model=request.form['model']
              milage=request.form['milage']
              price=request.form['price']
              desc=request.form['desc']
              cursor=mydb.cursor()
              cursor.execute('update cars set carname=%s,carno=%s,caryear=%s,category=%s,carmodel=%s,milage=%s,price=%s,description=%s where carid=%s',[name,carno,year,category,model,milage,price,desc,carid])
              mydb.commit()
              cursor.close()
              flash('Notes updated successfully')
              return redirect(url_for('dashuser'))
                
        return render_template('dashusers.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/delete/<carid>')
def delete(carid):
    cursor=mydb.cursor()
    cursor.execute('delete from cars where carid=%s',[carid])
    mydb.commit()
    cursor.close()
    flash('Notes deleted successfully')
    return redirect(url_for('dashcartable'))
@app.route('/dashpayment', methods=['POST','GET'])
@app.route('/deleteuser/<mobile>')
def deleteuser(mobile):
    cursor=mydb.cursor()
    cursor.execute('delete from register where mobile=%s',[mobile])
    mydb.commit()
    cursor.close()
    flash('user deleted successfully')
    return redirect(url_for('dashuserdetails'))
@app.route('/dashpayment', methods=['POST','GET'])
def dashpayment():
    if session.get('user'):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM rent")
        rent = cursor.fetchall()
        return render_template('dashpayment.html', rent=rent)
    return render_template('dashpayment.html')
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

