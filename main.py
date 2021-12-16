from flask import Flask, render_template, redirect, url_for, request
import urllib.request, json 
from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = '7CA5293D0810257F680B2A6CAC9EB291B5405E4D4F42B9A1E26EDE9BAB50BE72'

searchvalue = ''
movieid = ""

@app.route("/")
@app.route("/home", methods=['POST' , 'GET'])
def home():
    return render_template('home.html' )


@app.route("/search", methods = ['POST', 'GET'])
def search():
    searchresult = request.form.get("searches")
    searchvalue= '=' + searchresult
    with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&s' + searchvalue) as url:
        data = json.loads(url.read().decode())    
    return render_template('search.html', posts = data )


@app.route("/movie/<string:movieid>", methods = ['GET'])
def movie(movieid):
    with urllib.request.urlopen('http://www.omdbapi.com?apikey=f720dfee&i=' + movieid) as url:
        data = json.loads(url.read().decode())
    return render_template('movie.html', movies = data)


if __name__ == '__main__':
    app.run(debug=True)

