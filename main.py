from flask import Flask, render_template, redirect, url_for, request
import urllib.request, json 
from flask import Flask
from flask.helpers import flash
from forms import RegistrationForm, LoginForm
import psycopg2
import bcrypt
import requests

hostname = 'localhost'
database = 'filmlibrary'
username = 'postgres'
pwd = 'CharFutur144'
port_id = '5432'
conn_error = False

#Varible declaration
signedin = False
usernames = ""
searchvalue = ''
movieid = ""


#Database Connection String
try:
    con = psycopg2.connect(host = hostname, dbname = database, user = username, password = pwd, port = port_id)

    cursor = con.cursor()

    cursor.close()
    con.close()

except Exception as error:
    conn_error = True
    print('Connection to database is faulty')

#flask app and key config declaration
app = Flask(__name__)
app.config['SECRET_KEY'] = '7CA5293D0810257F680B2A6CAC9EB291B5405E4D4F42B9A1E26EDE9BAB50BE72'


#Home Page
@app.route("/")
@app.route("/home", methods=['POST' , 'GET'])
def home():
    return render_template('home.html' )


#Search Results Page
@app.route("/search", methods = ['POST', 'GET'])
def search():
    searchresult = request.form.get("searches")
    searchvalue= '=' + searchresult
    with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&s' + searchvalue) as url:
        data = json.loads(url.read().decode())    
    return render_template('search.html', posts = data )


#Movie Page
@app.route("/movie/<string:movieid>", methods = ['GET'])
def movie(movieid):
    with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&i=' + movieid) as url:
        data = json.loads(url.read().decode())
    return render_template('movie.html', movies = data)


#Registration Page
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        
        hashedpw = bcrypt.hashpw(form.password.data.encode('utf-8'),bcrypt.gensalt())

        unhashedpw = hashedpw.decode('utf-8')

        user = {"username":form.username.data, "email":form.email.data, "password":unhashedpw}
        headers = {
            'Content-Type' : 'application/json'
        }
        requests.post(headers = headers, data = json.dumps(user))
        flash(f'Account created for {form.username.data}!', 'success')

        return redirect(url_for('home', data = user))
    return render_template('register.html', title='Register', form=form, signedin = signedin, usernames = usernames)


#Login Page
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cursor.execute("SELECT * FROM users WHERE email = ?" , form.email.data )
        account = cursor.fetchone()
        print(account)
        hashedpw = bcrypt.checkpw(form.password.data.encode('utf-8'), account[2].encode('utf-8'))
        
        if account and hashedpw:
            global signedin, usernames
            signedin = True
            usersid = account[0]
            usernames = account[1]
            return redirect(url_for('home'))
            
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', title='Login', form=form, signedin = signedin)


#Logout Function
@app.route("/logout", methods=['GET'])
def logout():
    global signedin
    signedin = False
    return redirect(url_for('home'))


#Flask run method
if __name__ == '__main__':
    app.run(debug=True)

