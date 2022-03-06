from flask import Flask, render_template, redirect, url_for, request, flash
import urllib.request, json 
from flask import Flask
from forms import MovieSubmit, RegistrationForm, LoginForm
import psycopg2
import bcrypt

hostname = 'filmcore.cuamqg1s0vh3.eu-west-2.rds.amazonaws.com'
database = 'filmcore'
dbusername = 'postgres'
dbpwd = 'filmcore'
dbport_id = '5432'
conn_error = False

#Varible declaration
signedin = False
usernames = ""
usersid = ''
searchvalue = ''
movieid = ""


#Database Connection String
try:
    con = psycopg2.connect(host = hostname, dbname = database, user = dbusername, password = dbpwd, port = dbport_id)
    con.autocommit = True

except Exception as error:
    conn_error = True
    print('Connection to database is faulty')

cursor = con.cursor()

#flask app and key config declaration
app = Flask(__name__)
app.config['SECRET_KEY'] = '7CA5293D0810257F680B2A6CAC9EB291B5405E4D4F42B9A1E26EDE9BAB50BE72'


#Home Page
@app.route("/")
@app.route("/home", methods=['POST' , 'GET'])
def home():
    global searchvalue
    searchvalue = ''
    if conn_error == True:
        flash(f'Database connection error' , 'warning')
    return render_template('home.html', signedin = signedin, usernames = usernames, usersid = usersid )


#Search Results Page
@app.route("/search", methods = ['POST', 'GET'])
def search():
    global searchvalue
    error = None

    if searchvalue != '':
        pass

    else:
        if searchvalue == '':
            searchvalue = request.form.get("searches")
        if ' ' in searchvalue:
            searchvalue = str(searchvalue).replace(' ', '_')

    with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&s=' + searchvalue) as url:
        data = json.loads(url.read().decode())

        if data['Response'] == "False":
            error = 'Invalid credentials'
            return render_template('home.html', signedin = signedin, usernames = usernames, usersid = usersid, error = error )

    if '_' in searchvalue:
        displaysearch = str(searchvalue).replace('_', ' ') 
    else:
        displaysearch = searchvalue

    return render_template('search.html', posts = data, signedin = signedin, usernames = usernames, usersid = usersid, searchvalue = searchvalue, 
    error = error, displaysearch = displaysearch )


#Movie Page
@app.route("/movie/<string:movieid>", methods = ['GET', 'POST'])
def movie(movieid):
    with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&i=' + movieid) as url:
        data = json.loads(url.read().decode())

    
    stringuser = str(usersid)

    if usersid != '':
        cursor.execute("SELECT * FROM watchlist WHERE movieid  ='" + movieid + "'AND usersid ='" + stringuser + "'")
        if cursor.rowcount > 0:
            add = True

        else:
            if cursor.rowcount == 0:
                
                add = False
                
    else:
        if usersid == '':
            add = True

    movieName = data['Title']
    movieImage = data['Poster']
    movieType = data['Type']
    movieYear = data['Year']
    movieID = movieid

    form = MovieSubmit()

    if form.validate_on_submit():
        cursor.execute("INSERT INTO watchlist(movieid, moviename, movieimage, movieType, movieyear, usersID) VALUES('" + movieID +  "','" + movieName + "', '" + movieImage + "', '" + movieType + "', '" + movieYear + "', '" + stringuser + "')")
        flash(f'{movieName} has been added to your watchlist!', 'success') 

    return render_template('movie.html', movies = data, form = form, signedin = signedin, usernames = usernames, usersid = usersid, add = add)



@app.route("/watchlist/movie/<string:movieid>", methods = ['GET', 'POST'])
def watchlist_movie(movieid):
    with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&i=' + movieid) as url:
        data = json.loads(url.read().decode())

    return render_template('watchlist_movie.html', movies = data, signedin = signedin, usernames = usernames, usersid = usersid)


#Registration Page
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashedpw = bcrypt.hashpw(form.password.data.encode('utf-8'),bcrypt.gensalt())
        unhashedpw = hashedpw.decode('utf-8')

        global signedin, usernames, usersid

        username = form.username.data
        pwd = unhashedpw
        email = form.email.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        user = username, pwd, email, firstname, lastname

        cursor.execute("SELECT * FROM users WHERE username ='" + username + "'")
        if cursor.rowcount > 0:
            flash(f'This username is already taken', 'warning')
            return redirect(url_for('register', data = user, signedin = signedin, usernames = usernames, usersid = usersid))

        else:
            cursor.execute("SELECT * FROM users WHERE email ='" + email + "'")
            if cursor.rowcount > 0:
                flash(f'This email is already associated to another account!', 'warning')
                return redirect(url_for('register', data = user, signedin = signedin, usernames = usernames, usersid = usersid))
        
            else:
                cursor.execute("INSERT INTO users(username,pwd,email,firstname,lastname)VALUES('" + username +  "','" + pwd + "', '" + email + "', '" + firstname + "', '" + lastname + "')")
                
                cursor.execute("SELECT * FROM users WHERE username ='" + username + "'AND email ='" + email + "'")
                account = cursor.fetchone()

                signedin = True
                usernames = username
                usersid = account[0]

                flash(f'Account created for {username}!', 'success')

                return redirect(url_for('home', data = user, signedin = signedin, usernames = usernames, usersid = usersid))
    return render_template('register.html', title='Register', form=form, signedin = signedin, usernames = usernames)


#Watchlist
@app.route("/watchlist", methods=['GET'])
def watchlist():
    if signedin == False:
        return redirect(url_for('login'))
    fkuser_id = str(usersid)
    cursor.execute("SELECT * FROM watchlist WHERE usersid ='" + fkuser_id + "'")
    wlist = cursor.fetchall()
    return render_template('watchlist.html', signedin = signedin, usernames = usernames, usersid = usersid, wlist = wlist )


#Profile Page
@app.route("/profile/<string:usernames>", methods=['GET'])
def profile(usernames):
    if signedin == False:
        return redirect(url_for('login'))
    
    else:
        cursor.execute("SELECT * FROM users WHERE userid='"+ usersid + "'")
        profiledetail = cursor.fetchone() 
        
        return render_template('profile.html', signedin = signedin, usernames = usernames, usersid = usersid, profiledetail = profiledetail )


#Login Page
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        scriptvalues = form.email.data
        script = "SELECT * FROM users WHERE email ='" + scriptvalues + "'"
        cursor.execute(script)
        account = cursor.fetchone()
        hashedpw = bcrypt.checkpw(form.password.data.encode('utf-8'), account[2].encode('utf-8'))
        
        if account and hashedpw:
            global signedin, usernames, usersid
            signedin = True
            usersid = account[0]
            usernames = account[1]
            return redirect(url_for('home'))
            
        else:
            flash(f'Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', title='Login', form=form, signedin = signedin, usernames = usernames, usersid = usersid)


#Logout Function
@app.route("/logout", methods=['GET'])
def logout():
    global signedin
    signedin = False
    return redirect(url_for('home'))


#Flask run method
if __name__ == '__main__':
    app.run(debug=True)

