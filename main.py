from flask import Flask, render_template, redirect, url_for, request, flash
import urllib.request, json 
from flask import Flask
from forms import MovieSubmit, RegistrationForm, LoginForm, MovieDelete, ProfileForm
from forms import EmailConfirm, PasswordChange, PasswordReset
import psycopg2
import bcrypt
from urllib.request import Request, urlopen
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import smtplib
import databaseconn


#Flask app and key config declaration
app = Flask(__name__)
app.config['SECRET_KEY'] = '7CA5293D0810257F680B2A6CAC9EB291B5405E4D4F42B9A1E26EDE9BAB50BE72'


#Database Conn details
hostname = databaseconn.hostname
database = databaseconn.database
dbusername = databaseconn.dbusername
dbpwd = databaseconn.dbpwd
dbport_id = databaseconn.dbport_id
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

#Home Page
@app.route("/")
@app.route("/home", methods=['POST' , 'GET'])
def home():
    global searchvalue, pop_mov_data, pop_tv_data, theatreq, upcomingreq

    searchvalue = ''

    hold = False
    cut_data = ""
    cut_theatr_data = ""
    cut_tv_data = ""
    cut_upcoming_data = ""
    if hold == True:

        req = Request('https://imdb-api.com/en/API/MostPopularMovies/k_10ri6dyy', headers={'User-Agent': 'Mozilla/5.0'})
        pop_mov_data = json.loads(urlopen(req).read())
        cut_data = pop_mov_data["items"][0:5]

        tvreq = Request('https://imdb-api.com/en/API/MostPopularTVs/k_10ri6dyy', headers={'User-Agent': 'Mozilla/5.0'})
        pop_tv_data = json.loads(urlopen(tvreq).read())
        cut_tv_data = pop_tv_data["items"][0:5]

        theatreq = Request('https://imdb-api.com/en/API/InTheaters/k_10ri6dyy', headers={'User-Agent': 'Mozilla/5.0'})
        theatr_data = json.loads(urlopen(theatreq).read())
        cut_theatr_data = theatr_data["items"][0:5]

        upcomingreq = Request('https://imdb-api.com/en/API/ComingSoon/k_10ri6dyy', headers={'User-Agent': 'Mozilla/5.0'})
        upcoming_data = json.loads(urlopen(upcomingreq).read())
        cut_upcoming_data = upcoming_data["items"][0:5]
    
    
    return render_template('home.html', signedin = signedin, data1 = cut_data, data2 = cut_tv_data, data3 = cut_theatr_data, 
    data4 = cut_upcoming_data, usernames = usernames, usersid = usersid )


#Most Popular Movies Page
@app.route("/popular-movies", methods=['GET'])
def popularmovies():

    global pop_mov_data
    data = pop_mov_data["items"]

    return render_template('popular_movies.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#Most Popular TV Page
@app.route("/popular-tv", methods=['GET'])
def populartv():

    global pop_tv_data
    data = pop_tv_data["items"]

    return render_template('popular_tv.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#In theatres Page
@app.route("/in-theatres", methods=['GET'])
def intheatres():

    global theatreq
    data = theatreq["items"]

    return render_template('in_theatres.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#Coming soon page
@app.route("/coming-soon", methods=['GET'])
def comingsoon():

    global upcomingreq
    data = upcomingreq["items"]

    return render_template('coming_soon.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#Top250 Page
@app.route("/top250", methods=['GET'])
def top250():

    req = Request('https://imdb-api.com/en/API/Top250Movies/k_10ri6dyy', headers={'User-Agent': 'Mozilla/5.0'})
    data = json.loads(urlopen(req).read())
    data = data["items"]

    return render_template('top250.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#Top250 TV shows Page
@app.route("/top250tv", methods=['GET'])
def top250tv():

    req = Request('https://imdb-api.com/en/API/Top250TVs/k_10ri6dyy', headers={'User-Agent': 'Mozilla/5.0'})
    data = json.loads(urlopen(req).read())
    data = data["items"]

    return render_template('top250tv.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


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
        cursor.execute("SELECT * FROM watchlist WHERE movieid = %(hold_mov)s AND usersid = %(hold_id)s", {"hold_mov": movieid}, {"hold_id": stringuser}  )

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
        
        insert = "INSERT INTO watchlist(movieid, moviename, movieimage, movieType, movieyear, usersID) VALUES(%(hold_id)s,%(hold_name)s,%(hold_image)s,%(hold_Type)s,%(hold_year)s,%(hold_ids)s)"
        
        data = {"hold_id": movieID}, {"hold_name": movieName}, {"hold_image": movieImage}, {"hold_Type": movieType}, {"hold_year": movieYear}, {"hold_ids": stringuser}
        
        cursor.execute(insert, data)

        flash(f'{movieName} has been added to your watchlist!', 'success') 

    return render_template('movie.html', movies = data, form = form, signedin = signedin, usernames = usernames, usersid = usersid, add = add)


#Watchlist
@app.route("/watchlist", methods=['GET'])
def watchlist():
    if signedin == False:
        return redirect(url_for('login'))
    fkuser_id = str(usersid)
    
    cursor.execute("SELECT * FROM watchlist WHERE usersid = %(hold_id)s", {"hold_id": fkuser_id})

    wlist = cursor.fetchall()
    return render_template('watchlist.html', signedin = signedin, usernames = usernames, usersid = usersid, wlist = wlist )


#Watchlist movie page
@app.route("/watchlist/movie/<string:movieid>", methods = ['GET', 'POST'])
def watchlist_movie(movieid):
    with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&i=' + movieid) as url:
        data = json.loads(url.read().decode())
    
    form = MovieDelete()

    stringuser = str(usersid)
    strmovie = str(movieid)

    if form.validate_on_submit():
        cursor.execute("DELETE FROM watchlist WHERE movieid = %(hold_mov)s AND usersid = %(hold_id)s", {"hold_mov": strmovie}, {"hold_id": stringuser}  )

        return redirect(url_for('watchlist'))


    return render_template('watchlist_movie.html', movies = data, form = form, signedin = signedin, usernames = usernames, usersid = usersid)


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

        cursor.execute("SELECT * FROM users WHERE username = %(hold_username)s", {"hold_id": username})
        if cursor.rowcount > 0:
            flash(f'This username is already taken', 'warning')
            return redirect(url_for('register', data = user, signedin = signedin, usernames = usernames, usersid = usersid))

        else:
            cursor.execute("SELECT * FROM users WHERE email = %(hold_email)s", {"hold_id": email})

            if cursor.rowcount > 0:
                flash(f'This email is already associated to another account!', 'warning')
                return redirect(url_for('register', data = user, signedin = signedin, usernames = usernames, usersid = usersid))
        
            else:
                insert = "INSERT INTO users(username,pwd,email,firstname,lastname) VALUES(%(hold_username)s,%(hold_pwd)s,%(hold_email)s,%(hold_firstname)s,%(hold_lastname)s)"
        
                data = ({"hold_username": username}, {"hold_pwd": pwd}, {"hold_email": email}, {"hold_firstname": firstname}, {"hold_lastname": lastname})
        
                cursor.execute(insert, data)

                cursor.execute("SELECT * FROM users WHERE username = %(hold_username)s AND email = %(hold_email)s", {"hold_username":username }, {"hold_email": email}  )

                account = cursor.fetchone()

                signedin = True
                usernames = username
                usersid = account[0]

                flash(f'Account created for {username}!', 'success')

                return redirect(url_for('home', data = user, signedin = signedin, usernames = usernames, usersid = usersid))
    return render_template('register.html', title='Register', form=form, signedin = signedin, usernames = usernames)


#Profile Page
@app.route("/profile/<int:usersid>", methods=['GET', 'POST'])
def profile(usersid):
    if signedin == False:
        return redirect(url_for('login'))
    
    else:
        usernameid = str(usersid)
        cursor.execute("SELECT * FROM users WHERE userid = %(hold_id)s", {"hold_id": usernameid})
        account = cursor.fetchone() 

    form = ProfileForm()

    if form.validate_on_submit():

        if form.submit.data:
            
            script = ("DELETE FROM watchlist WHERE usersid = %(hold_id)s", {"hold_id": usernameid})
            secscript = ("DELETE FROM users WHERE usersid = %(hold_id)s", {"hold_id": usernameid})
            cursor.execute(script)
            cursor.execute(secscript)
            return redirect(url_for('logout'))

        elif form.submit2.data:
            script2 = ("DELETE FROM watchlist WHERE usersid = %(hold_id)s", {"hold_id": usernameid})
            cursor.execute(script2)

    return render_template('profile.html', signedin = signedin, usernames = usernames, usersid = usersid, form = form, account = account )


#Password Change Page
@app.route("/change-password", methods=['GET', 'POST'])
def password_change():
    if signedin == False:
        return redirect(url_for('login'))
    
    form = PasswordChange()

    if form.validate_on_submit():
        usernameid = str(usersid)
        script = ("SELECT * FROM users WHERE userid = %(hold_id)s", {"hold_id": usernameid})
        cursor.execute(script)
        account = cursor.fetchone()
        hashedpw = bcrypt.checkpw(form.old_password.data.encode('utf-8'), account[2].encode('utf-8'))

        if account and hashedpw:
            new_hashedpw = bcrypt.hashpw(form.new_password.data.encode('utf-8'),bcrypt.gensalt())
            new_unhashedpw = new_hashedpw.decode('utf-8')

            update_script = "UPDATE users SET pwd = %(hold_pwd)s WHERE userid = %(hold_id)s"
            data = ({"hold_pwd": new_unhashedpw},{"hold_id": usernameid})
            cursor.execute(update_script, data)

            return redirect(url_for('profile', usersid = usersid))

    return render_template('password_change.html', form = form , signedin = signedin, usernames = usernames, usersid = usersid )


#Verify the reset token function
def verify_reset_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        user_id = s.loads(token)['user_id']
    except:
        return None

    struser = str(user_id)
    script = ("SELECT * FROM users WHERE userid = %(hold_id)s", {"hold_id": struser})

    cursor.execute(script)
    account = cursor.fetchone()
    return account


#Email Confirm Page
@app.route("/confirm-email", methods=['GET', 'POST'])
def confirm_email():
    expires_sec=1800
    if signedin == True:
        return redirect(url_for('home'))
    
    form = EmailConfirm()

    if form.validate_on_submit():
        user_email = form.email.data
        script = ("SELECT * FROM users WHERE email = %(hold_email)s", {"hold_id": user_email})
        cursor.execute(script)
        account = cursor.fetchone()

        if cursor.rowcount == 0:
            flash(f'This email is not associated with any account', 'warning')
            redirect(url_for('confirm_email'))
        
        else:
            account_id = account[0]

            s = Serializer(app.config['SECRET_KEY'], expires_sec)
            token = s.dumps({'user_id': account_id}).decode('utf-8')

            message = f"""
            Subject: Filmcore Account Password Reset

            Click on the link below to change your password. This link will expire in 30mins
            
            {url_for('reset_password', token=token, _external=True)}
            
            If you did not request this link, please ignore this email.
            
            Thanks 
            Filmcore Support
            """
            
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(databaseconn.emailcon, databaseconn.passwordcon)

            server.sendmail(
                "service.firmcore@gmail.com", 
                [user_email], 
                message 
            )
            server.quit()
            
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('login'))

    return render_template('confirm_email.html', signedin = signedin, usernames = usernames, usersid = usersid, form = form )


#Reset Password Page
@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    global signedin, usernames, usersid
    if signedin == True:
        return redirect(url_for('home'))

    user = verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('home'))
    form = PasswordReset()
    if form.validate_on_submit():
        hashedpw = bcrypt.hashpw(form.password.data.encode('utf-8'),bcrypt.gensalt())
        unhashedpw = hashedpw.decode('utf-8')

        userids = str(user[0])
        
        update_script = "UPDATE users SET pwd = %(hold_pwd)s WHERE userid = %(hold_id)s"
        data = ({"hold_pwd": unhashedpw},{"hold_id": userids})
        cursor.execute(update_script, data)


        signedin = True
        usernames = user[1]
        usersid = user[0]

        return redirect(url_for('home', data = user, signedin = signedin, usernames = usernames, usersid = usersid))
    return render_template('password_reset.html', form=form)


#Login Page
@app.route("/login", methods=['GET', 'POST'])
def login():
    global signedin
    if signedin == True:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        scriptvalues = form.email.data
        script = ("SELECT * FROM users WHERE email = %(hold_email)s", {"hold_id": scriptvalues})
        cursor.execute(script)
        account = cursor.fetchone()
        hashedpw = bcrypt.checkpw(form.password.data.encode('utf-8'), account[2].encode('utf-8'))
        
        if account and hashedpw:
            global usernames, usersid
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
    global signedin, usernames, usersid
    if signedin == False:
        return redirect(url_for('home'))
    else:
        signedin = False
        usernames = ""
        usersid = ''
    return redirect(url_for('home'))


#Flask run method
if __name__ == '__main__':
    app.run(debug=True)

