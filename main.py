#Module Import
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


#Database Connection details. Linked to databaseconn.py
hostname = databaseconn.hostname
database = databaseconn.database
dbusername = databaseconn.dbusername
dbpwd = databaseconn.dbpwd
dbport_id = databaseconn.dbport_id


#Global Varible declaration
signedin = False
usernames = ""
usersid = ''
searchvalue = ''
movieid = ""

#Database Connection String and declaring auto commit
try:
    con = psycopg2.connect(host = hostname, dbname = database, user = dbusername, password = dbpwd, port = dbport_id)
    con.autocommit = True

except Exception as error:
    flash("Database connection faulty", 'warning')


#Home Page
@app.route("/")
@app.route("/home", methods=['POST' , 'GET'])
def home():
    global searchvalue

    #Calling home page api results
    req = Request('https://imdb-api.com/en/API/MostPopularMovies/k_40mu5e3m', headers={'User-Agent': 'Mozilla/5.0'})
    pop_mov_data = json.loads(urlopen(req).read())
    cut_data = pop_mov_data["items"][0:5]

    #Most Popular TV shows
    tvreq = Request('https://imdb-api.com/en/API/MostPopularTVs/k_40mu5e3m', headers={'User-Agent': 'Mozilla/5.0'})
    pop_tv_data = json.loads(urlopen(tvreq).read())
    cut_tv_data = pop_tv_data["items"][0:5]

    searchvalue = ''
    
    return render_template('home.html', signedin = signedin, data1 = cut_data, usernames = usernames, usersid = usersid, 
    data2 = cut_tv_data)


#Most Popular Movies Page
@app.route("/popular-movies", methods=['GET'])
def popularmovies():

    #Popular Movies API call. Items collection trimmed from results
    try:
        req = Request('https://imdb-api.com/en/API/MostPopularMovies/k_40mu5e3m', headers={'User-Agent': 'Mozilla/5.0'})
        pop_mov_data = json.loads(urlopen(req).read())
        data = pop_mov_data["items"]
    
    except Exception:
        return redirect(url_for('catch'))

    return render_template('popular_movies.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#Most Popular TV Page
@app.route("/popular-tv", methods=['GET'])
def populartv():

    #Popular TV API call. Items collection trimmed from results
    try:
        tvreq = Request('https://imdb-api.com/en/API/MostPopularTVs/k_40mu5e3m', headers={'User-Agent': 'Mozilla/5.0'})
        pop_tv_data = json.loads(urlopen(tvreq).read())
        data = pop_tv_data["items"]

    except Exception:
        return redirect(url_for('catch'))

    return render_template('popular_tv.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#In theatres Page
@app.route("/in-theatres", methods=['GET'])
def intheatres():

    #In theatres API call. Items collection trimmed from results
    try:
        theatdata = Request('https://imdb-api.com/en/API/InTheaters/k_40mu5e3m', headers={'User-Agent': 'Mozilla/5.0'})
        theatreq = json.loads(urlopen(theatdata).read())
        data = theatreq["items"]

    except Exception:
        return redirect(url_for('catch'))

    return render_template('in_theatres.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#Coming soon page
@app.route("/coming-soon", methods=['GET'])
def comingsoon():

    #Coming soon API call. Items collection trimmed from results
    try:
        upcomingreq = Request('https://imdb-api.com/en/API/ComingSoon/k_40mu5e3m', headers={'User-Agent': 'Mozilla/5.0'})
        upcoming_data = json.loads(urlopen(upcomingreq).read())
        data = upcoming_data["items"]

    except Exception:
        return redirect(url_for('catch'))

    return render_template('coming_soon.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#Top250 Page
@app.route("/top250", methods=['GET'])
def top250():

    #Top250 Movies API call. Items collection trimmed from results
    try:
        req = Request('https://imdb-api.com/en/API/Top250Movies/k_40mu5e3m', headers={'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urlopen(req).read())
        data = data["items"]
    
    except Exception:
        return redirect(url_for('catch'))    

    return render_template('top250.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#Top250 TV shows Page
@app.route("/top250tv", methods=['GET'])
def top250tv():

    #Top 250 tv shows API call. Items collection trimmed from results
    try:
        req = Request('https://imdb-api.com/en/API/Top250TVs/k_40mu5e3m', headers={'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urlopen(req).read())
        data = data["items"]
    
    except Exception:
        return redirect(url_for('catch'))      

    return render_template('top250tv.html', data = data, signedin = signedin, usernames = usernames, usersid = usersid )


#Search Results Page
@app.route("/search", methods = ['POST', 'GET'])
def search():
    global searchvalue

    #Catching erroneous searchvalue values
    try:
        if searchvalue != '':
            pass

        elif searchvalue == ' ':
            return redirect(url_for('home'))

    #Retrieving searchvalue and removing blank spaces    
        else:
            if searchvalue == '':
                searchvalue = request.form.get("searches")
            if ' ' in searchvalue:
                searchvalue = str(searchvalue).replace(' ', '_')

        if searchvalue == '':
            return redirect(url_for('home'))

    #Keyword Search API call
        with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&s=' + searchvalue) as url:
            data = json.loads(url.read().decode())

    #No results found alert
        if data['Response'] == "False":
            flash("No results found", 'warning')
    
    except Exception:
        return redirect(url_for('catch')) 

    #Removing _ from searchvalue to be displayed
    if '_' in searchvalue:
        displaysearch = str(searchvalue).replace('_', ' ') 
    else:
        displaysearch = searchvalue
 

    return render_template('search.html', posts = data, signedin = signedin, usernames = usernames, usersid = usersid, searchvalue = searchvalue, 
    displaysearch = displaysearch )


#Movie Page
@app.route("/movie/<string:movieid>", methods = ['GET', 'POST'])
def movie(movieid):
    headers = {
        "X-RapidAPI-Host": "utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com",
        "X-RapidAPI-Key": "ecd4a37478msh4fa35a0a8658b6bp14334cjsnfa15424a5067"
        }
    
    try:
    #ID search API call
        with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&i=' + movieid) as url:
            data = json.loads(url.read().decode())

            ratings = data["Ratings"]

    #Catching retrieving movies with a Rotten Tomatoes score
        rt_rating = "N/A"

        for i in ratings:
            if i['Source'] == "Rotten Tomatoes":
                rt_rating = i['Value']
    
    except Exception:
        return redirect(url_for('catch'))
    
    #Variables for Platform Check
    except_chk = False
    replacement_data = {
        "display_name": "NOT AVAILABLE FOR THIS MOVIE/TV", "id": "n/a", "url": "", "name": "", "icon": ""
        }

    try:
    #Platform availability API           
        req = Request('https://utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com/idlookup?source=imdb&country=uk&source_id=' + movieid, headers = headers)
        platform_data = json.loads(urlopen(req).read())

    #Accessing locations records inside api response
        collection = platform_data["collection"]
        locations = collection["locations"]    
    
    #Error occurs, replacement data is shown
    except Exception:
        locations = replacement_data
        except_chk = True

    stringuser = str(usersid)

    #Checking if the movie is found in the logged in users watchlist
    try:
        if usersid != '':
            cursor = con.cursor()
            cursor.execute("SELECT * FROM watchlist WHERE movieid = %(hold_mov)s AND usersid = %(hold_id)s", {"hold_mov": movieid , "hold_id": stringuser}  )
            
            if cursor.rowcount > 0:
                add = True
                cursor.close()

            else:
                if cursor.rowcount == 0:
                    add = False
                    cursor.close()
                    
        else:
            if usersid == '':
                add = True

    #Assigning values from ID search API call to variables
        movieName = data['Title']
        movieImage = data['Poster']
        movieType = data['Type']
        movieYear = data['Year']
        movieID = movieid

    
    except Exception:
        return redirect(url_for('catch'))

    form = MovieSubmit()
    
    #Inserting a movie into a users watchlist
    try:
        if form.validate_on_submit():
            cursor = con.cursor()
            cursor.execute("INSERT INTO watchlist(movieid, moviename, movieimage, movieType, movieyear, usersID) VALUES(%(hold_id)s,%(hold_name)s,%(hold_image)s,%(hold_Type)s,%(hold_year)s,%(hold_ids)s)", 
            {"hold_id": movieID, "hold_name": movieName, "hold_image": movieImage, "hold_Type": movieType, "hold_year": movieYear, "hold_ids": stringuser} )
            cursor.close()
            flash("Movie added to watchlist", 'success')
            add = True

    except Exception:
        return redirect(url_for('catch')) 

    return render_template('movie.html', movies = data, platform = locations, rt_rating = rt_rating, 
    form = form, signedin = signedin, usernames = usernames, usersid = usersid, add = add, except_chk = except_chk)


#Watchlist
@app.route("/watchlist", methods=['GET'])
def watchlist():
    if signedin == False:
        return redirect(url_for('login'))

    #Return the users watchlist based on userid    
    try:
        fkuser_id = str(usersid)
        cursor = con.cursor()
        cursor.execute("SELECT * FROM watchlist WHERE usersid = %(hold_id)s", {"hold_id": fkuser_id})
        wlist = cursor.fetchall()
        cursor.close()

    except Exception:
        return redirect(url_for('catch'))

    
    return render_template('watchlist.html', signedin = signedin, usernames = usernames, usersid = usersid, wlist = wlist )


#Watchlist movie page
@app.route("/watchlist/movie/<string:movieid>", methods = ['GET', 'POST'])
def watchlist_movie(movieid):
    #User must be logged in to access this page
    if signedin == False:
        return redirect(url_for('login'))

    headers = {
        "X-RapidAPI-Host": "utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com",
        "X-RapidAPI-Key": "ecd4a37478msh4fa35a0a8658b6bp14334cjsnfa15424a5067"
        }
    
    try:
    #ID search API call
        with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&i=' + movieid) as url:
            data = json.loads(url.read().decode())

            ratings = data["Ratings"]

    #Catching retrieving movies with a Rotten Tomatoes score
        rt_rating = "N/A"

        for i in ratings:
            if i['Source'] == "Rotten Tomatoes":
                rt_rating = i['Value']
    
    except Exception:
        return redirect(url_for('catch'))

    #Variables for Platform Check
    except_chk = False
    replacement_data = {
        "display_name": "NOT AVAILABLE FOR THIS MOVIE/TV", "id": "n/a", "url": "", "name": "", "icon": ""
        }

    #Platform availability API  
    try:        
        req = Request('https://utelly-tv-shows-and-movies-availability-v1.p.rapidapi.com/idlookup?source=imdb&country=uk&source_id=' + movieid, headers = headers)
        platform_data = json.loads(urlopen(req).read())
    
        collection = platform_data["collection"]
        locations = collection["locations"]    
    
    #Error occurs, replacement data is shown
    except Exception:
        locations = replacement_data
        except_chk = True
    
    form = MovieDelete()

    stringuser = str(usersid)
    strmovie = str(movieid)

    try:
    #Deleting a movie from a users watchlist
        if form.validate_on_submit():
            cursor = con.cursor()
            cursor.execute("DELETE FROM watchlist WHERE movieid = %(hold_mov)s AND usersid = %(hold_id)s", {"hold_mov": strmovie, "hold_id": stringuser}  )
            cursor.close()
            flash('Movie Deleted from watchlist!', 'success')
            return redirect(url_for('watchlist'))

    except Exception:
        return redirect(url_for('catch'))

    return render_template('watchlist_movie.html', movies = data, form = form, signedin = signedin, usernames = usernames, 
    usersid = usersid, platform = locations, rt_rating = rt_rating,except_chk = except_chk)


#Registration Page
@app.route("/register", methods=['GET', 'POST'])
def register():
    global signedin, usernames, usersid
    #User must be logged in to access this page
    if signedin == True:
        return redirect(url_for('login'))
        
    form = RegistrationForm()
    try:
        if form.validate_on_submit():
        #Hashing password and storing it in utf8 format 
            hashedpw = bcrypt.hashpw(form.password.data.encode('utf-8'),bcrypt.gensalt())
            unhashedpw = hashedpw.decode('utf-8')
        
            #Fetching and storing data from form fields
            username = form.username.data
            pwd = unhashedpw
            email = form.email.data
            firstname = form.firstname.data
            lastname = form.lastname.data
            user = username, pwd, email, firstname, lastname

            #Checking to see if the username is already being used
            cursor = con.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %(hold_username)s", {"hold_username": username})
            
            if cursor.rowcount > 0:
                flash('This username is already taken', 'warning')
                cursor.close()
                return redirect(url_for('register', data = user, signedin = signedin, usernames = usernames, usersid = usersid))

            else:
                #Checking to see if the email is already being used
                
                cursor.execute("SELECT * FROM users WHERE email = %(hold_email)s", {"hold_email": email})

                if cursor.rowcount > 0:
                    flash('This email is already associated to another account!', 'warning')
                    cursor.close()
                    return redirect(url_for('register', data = user, signedin = signedin, usernames = usernames, usersid = usersid))

                #Inserting the users registration data into the users table
                else:
                    
                    insert = "INSERT INTO users(username,pwd,email,firstname,lastname) VALUES(%(hold_username)s,%(hold_pwd)s,%(hold_email)s,%(hold_firstname)s,%(hold_lastname)s)"
            
                    data = ({"hold_username": username, "hold_pwd": pwd, "hold_email": email, "hold_firstname": firstname, "hold_lastname": lastname})
            
                    cursor.execute(insert, data)

                    #Selecting the new account from the users table and using this account to sign in
                    cursor.execute("SELECT * FROM users WHERE username = %(hold_username)s AND email = %(hold_email)s", {"hold_username":username , "hold_email": email}  )

                    account = cursor.fetchone()

                    signedin = True
                    usernames = username
                    usersid = account[0]

                    cursor.close()

                    flash(f'Account created for {usernames}!', 'success')

                    return redirect(url_for('home', data = user, signedin = signedin, usernames = usernames, usersid = usersid))
    
    except Exception:
        return redirect(url_for('catch')) 

    return render_template('register.html', title='Register', form=form, signedin = signedin, usernames = usernames)


#Profile Page
@app.route("/profile/<int:usersid>", methods=['GET', 'POST'])
def profile(usersid):
    #User must be logged in to access this page
    try:
        if signedin == False:
            return redirect(url_for('login'))
        
        #Finding logged in user account and returning profile information
        else:
            cursor = con.cursor()
            usernameid = str(usersid)
            cursor.execute("SELECT * FROM users WHERE userid = %(hold_id)s", {"hold_id": usernameid})
            account = cursor.fetchone() 
            cursor.close()

        form = ProfileForm()

        if form.validate_on_submit():

            #Delete account function, deletes watchlist first to conform with foreign key rules
            if form.submit.data:
                cursor = con.cursor() 
                cursor.execute("DELETE FROM watchlist WHERE usersid = %(hold_id)s", {"hold_id": usernameid})
                cursor.execute("DELETE FROM users WHERE userid = %(hold_id)s", {"hold_id": usernameid})
                cursor.close()

                flash("Account has been deleted, Goodbye!",'info')
                return redirect(url_for('logout'))

            #Clear Watchlist function
            elif form.submit2.data:
                cursor = con.cursor()
                cursor.execute("DELETE FROM watchlist WHERE usersid = %(hold_id)s", {"hold_id": usernameid})
                flash("Watchlist has been cleared!",'success')
                cursor.close()
                
    except Exception:
        return redirect(url_for('catch')) 

    return render_template('profile.html', signedin = signedin, usernames = usernames, usersid = usersid, form = form, account = account )


#Password Change Page
@app.route("/change-password", methods=['GET', 'POST'])
def password_change():
    #User must be logged in to access this page
    if signedin == False:
        return redirect(url_for('login'))
    
    form = PasswordChange()

    try:
        if form.validate_on_submit():

            #Retreieve user account information    
            usernameid = str(usersid)

            cursor = con.cursor()
            cursor.execute("SELECT * FROM users WHERE userid = %(hold_id)s", {"hold_id": usernameid})
            account = cursor.fetchone()
            cursor.close()

            pwd = account[2]

            #Check the old password form input and the account password record
            hashedpw = bcrypt.checkpw(form.old_password.data.encode('utf-8'), pwd.encode('utf-8'))

            if hashedpw == True:
                if account and hashedpw:
                    cursor = con.cursor()
                    #Hash the new password and store it in utf format.
                    new_hashedpw = bcrypt.hashpw(form.new_password.data.encode('utf-8'),bcrypt.gensalt())
                    new_unhashedpw = new_hashedpw.decode('utf-8')

                    #Update user record with the new valid data
                    update_script = "UPDATE users SET pwd = %(hold_pwd)s WHERE userid = %(hold_id)s"
                    data = ({"hold_pwd": new_unhashedpw ,"hold_id": usernameid})
                    cursor.execute(update_script, data)
                    cursor.close()

                    flash("Password Changed!", 'success')
                    return redirect(url_for('profile', usersid = usernameid))
                    
            else:
                flash("Old password is not correct",'warning')
    
    except Exception:
        return redirect(url_for('catch')) 

    return render_template('password_change.html', form = form , signedin = signedin, usernames = usernames, usersid = usersid )


#Verify the reset token function
def verify_reset_token(token):
    #Serialise secret key
    s = Serializer(app.config['SECRET_KEY'])
    try:
        user_id = s.loads(token)['user_id']
    except:
        return None

    #Return user information with the token
    try:
        struser = str(user_id)

        cursor = con.cursor()
        cursor.execute("SELECT * FROM users WHERE userid = %(hold_id)s", {"hold_id": struser})
        account = cursor.fetchone()
        cursor.close()

        return account

    except Exception:
        return redirect(url_for('catch'))


#Email Confirm Page
@app.route("/confirm-email", methods=['GET', 'POST'])
def confirm_email():
    #Token expiry time declaration
    expires_sec=1800

    #User cannot be logged in to access this page
    if signedin == True:
        return redirect(url_for('home'))
    
    form = EmailConfirm()
    
    if form.validate_on_submit():
        try:
            user_email = form.email.data

            #Check if email provided is linked to an account
            cursor = con.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %(hold_email)s", {"hold_email": user_email})
            account = cursor.fetchone()

            if cursor.rowcount == 0:
                flash('This email is not associated with any account', 'warning')
            
            else:
                account_id = account[0]

                #Serialise secret key, expiry time provided. Compose a token consisting of the seralised key, along with a payload of the users account id
                s = Serializer(app.config['SECRET_KEY'], expires_sec)
                token = s.dumps({'user_id': account_id}).decode('utf-8')

                #Email format sent to the users account
                message = f"""
                Subject: Filmcore Account Password Reset

                Click on the link below to change your password. This link will expire in 30mins
                
                {url_for('reset_password', token=token, _external=True)}
                
                If you did not request this link, please ignore this email.
                
                Thanks 
                Filmcore Support
                """
            
                #Email server, login, recipient, sender (service.firmcore@gmail.com) and message declared.
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(databaseconn.emailcon, databaseconn.passwordcon)

                server.sendmail(
                    "service.firmcore@gmail.com", 
                    [user_email], 
                    message 
                )
                server.quit()
            
                flash('An email has been sent with instructions to reset your password.', 'info')
                return redirect(url_for('home'))
    
            cursor.close()
        except Exception:
            return redirect(url_for('catch'))            
        

    return render_template('confirm_email.html', signedin = signedin, usernames = usernames, usersid = usersid, form = form )


#Reset Password Page
@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    global signedin, usernames, usersid
    #User cannot be logged in to access this page
    if signedin == True:
        return redirect(url_for('home'))

    #Call verify reset token function with the token
    user = verify_reset_token(token)

    #Expiry message if token is invalid or exceeded half an hour time limit
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('home'))
        

    form = PasswordReset()

    if form.validate_on_submit():
        try:
            #Hash password field and encode it to utf8
            hashedpw = bcrypt.hashpw(form.password.data.encode('utf-8'),bcrypt.gensalt())
            unhashedpw = hashedpw.decode('utf-8')

            userids = str(user[0])
            
            #Update user record with the updated password
            cursor = con.cursor()
            update_script = "UPDATE users SET pwd = %(hold_pwd)s WHERE userid = %(hold_id)s"
            data = ({"hold_pwd": unhashedpw, "hold_id": userids})
            cursor.execute(update_script, data)
            cursor.close()

            #Redirect user to login page
            flash("Password has been reset!", 'success')
            return redirect(url_for('login'))
        
        except Exception:
            return redirect(url_for('catch'))

    return render_template('password_reset.html', form=form)


#Login Page
@app.route("/login", methods=['GET', 'POST'])
def login():
    #User cannot be logged in to access this page
    global signedin
    if signedin == True:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        try:
            #Select user from user table based on email (email is unique)
            scriptvalues = form.email.data

            cursor = con.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %(hold_email)s", {"hold_email": scriptvalues})

            #Catch non-existant emails
            if cursor.rowcount > 0:
                account = cursor.fetchone()

                #Check the form password input with account data
                hashedpw = bcrypt.checkpw(form.password.data.encode('utf-8'), account[2].encode('utf-8'))
                
                #Log user in and redirect to homepage
                if account and hashedpw:
                    global usernames, usersid
                    signedin = True
                    usersid = account[0]
                    usernames = account[1]
                    return redirect(url_for('home'))

                #Unsuccessful login flash    
                else:
                    flash('Login Unsuccessful. Please check email or password', 'danger')

            else:
                if cursor.rowcount == 0:
                    flash('Login Unsuccessful. Please check email or password', 'danger')

            cursor.close()   
        except Exception:
            return redirect(url_for('catch'))
    
    return render_template('login.html', title='Login', form=form, signedin = signedin, usernames = usernames, usersid = usersid)


#Logout Function
@app.route("/logout", methods=['GET'])
def logout():
    #User must be logged in to access this page
    global signedin, usernames, usersid
    if signedin == False:
        return redirect(url_for('home'))
    else:
        #Reset user variables and log user out
        signedin = False
        usernames = ""
        usersid = ''
    return redirect(url_for('home'))


#Catch Page
@app.route("/error", methods=['GET'])
def catch():
    return render_template('catch.html')


#Flask run method
if __name__ == '__main__':
    app.run(debug=True)

