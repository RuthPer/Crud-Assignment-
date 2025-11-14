#By Ruth and Aayah
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

import secrets
import cs304dbi as dbi
import db_methods

def clean(input):
    """ A helper function that Converts 'None', 'null', or '' to real Python None for SQL."""
    if input is None:
        return None
    input = input.strip()
    return None if input.lower() in ('none', 'null', '') else input

# we need a secret_key to use flash() and sessions
app.secret_key = secrets.token_hex()

# configure DBI

# For Lookup, use 'wmdb'
# For CRUD and Ajax, use your personal db
# For project work, use your team db

print(dbi.conf('rp104_db'))

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    """
    Initail landing page
    """
    return render_template('main.html', page_title='Main Page')

@app.route('/about/')
def about():
    """
    The about page
    """
    return render_template('about.html', page_title='About Us')

@app.route('/insert/',methods=["GET","POST"])
def insert_movie():
    """
    This function will insert a new movie into the database, I f it is not a new
    movie then it will send the user to the update page
    """
    
    conn=dbi.connect()
    staff_id=10051
    if request.method =="POST":

        #Gets data from the form on the site
        title=request.form.get("movie-title")
        release=request.form.get("movie-release")
        tt=''
        data={"Movies TT":tt,"Title":title,"Release":release}

        # Try except to make sure the movie tt is an int
        try:
            tt=int(request.form.get("movie-tt"))
            data={"Movies TT":tt,"Title":title,"Release":release}

            if tt>0:
                #Displays data that is missing from input
                
                for item in data:
                    if data[item]=="":
                        flash(f"Missing Input: {item}")
                if "" not in [tt,title,release]:
                    result=db_methods.insert_movie(conn,tt,title,release,staff_id)
                    print(result)

                    #If movie already exsists in the databse redirect to update page
                    #If not then insert the movie and redirect to update page
                    if result==False:
                        flash(f"Error, did not insert movie with tt: {tt} already exsists in the Database!")
                        return redirect(url_for("update_movie",tt=tt))

                    else:
                        flash(f"Movie {title} was successfully inserted!")
                        return redirect(url_for("update_movie",tt=tt))
           
            else:

                #Displays data that is missing from input
                for item in data:
                    if data[item]=="":
                        flash(f"Missing Input: {item}")
                flash("Please Enter an none negative int for TT")
                
        except ValueError:
            #Displays data that is missing from input
            for item in data:
                    if data[item]=="":
                        flash(f"Missing Input: {item}")
            flash("Please Enter an int for TT")
            

        

    return render_template("form.html",page_title="Insert Movie")

@app.route("/update/<tt>",methods=["GET","POST"])
def update_movie(tt):
    """
    This method allows the users to see update movies values 
    """
    staff_id=10051
    conn=dbi.connect()
    movie_data=db_methods.get_movie(conn,tt)
    director=db_methods.get_director(conn,tt)

    if director==None:
        director="None Specified"
    else:
        director=director['name']

    #Gets data from the form on the site 
    if request.method =="POST":
        title = clean(request.form.get("movie-title"))

        # Try except to make sure the movie tt is an int
        try:
            movie_id = int(request.form.get("movie-tt"))
            release = clean(request.form.get("movie-release"))
            addedby = clean(request.form.get("movie-addedby"))
            director_id = clean(request.form.get("movie-director"))

            # Checks if the movie tt is a non-negative int
            if movie_id>0:
                current_tt=int(tt)
                new_tt=int(movie_id)
                print(tt)
                print(movie_id)

                #Checks what button the user 
                option= request.form.get("select_type")
                if option=="delete":
                    db_methods.delete_movie(conn,tt)
                    flash(f"Movie: {title} was deleted successfully!")
                    return redirect(url_for("index"))
                else:
                    # Checks if the new tt is different from the current tt
                    # If it is different it checks if the new tt already exsists in the database
                    if new_tt!=current_tt:
                        if db_methods.check_dups(conn,new_tt):
                            flash(f"Movie with tt: {new_tt} already exists")
                            return render_template("update.html",page_title="Update Page",
                                    movie=movie_data,
                                    direct=director)
                        else:
                            print("Test")
                            db_methods.update_movie(conn,title,current_tt,new_tt,release,addedby,director_id)
                    else:
                        print("Test")
                        db_methods.update_movie(conn,title,current_tt,new_tt,release,addedby,director_id)
                
                            
                    flash(f"Updated Movie: {title}")

                    #Grab Director Name again to update html
                    director=db_methods.get_director(conn,current_tt)
                    
                    print(director)
                    if director==None:
                        director="None Specified"
                        
                    else:
                        director=director['name']

                    movie_data={'tt': new_tt, 'title': title, 'release': release, 'director': director_id, 'addedby': addedby}
                    print(movie_data)

                    if current_tt==new_tt:
                        return render_template("update.html",page_title="Update Page",
                                    movie=movie_data,
                                    direct=director)
                    else:
                        return redirect(url_for('update_movie',tt=new_tt))
            else:
                flash("Please Enter an Non-negative int for TT")
        except ValueError:
            flash("Please Enter an int for MovieID")

    return render_template("update.html",page_title="Update Page",
                        movie=movie_data,
                        direct=director)

@app.route("/select/",methods=["GET","POST"])
def select_movie():
    """
    Selects all the movies in the database that are missing information in an column
    that are either missing the director or release date
    """
    conn=dbi.connect()
    movie_data=db_methods.select_movies(conn)
    print(movie_data)
    if movie_data==[]:
        flash("There are no current incomplete Movies found!")
    
    #Makes sure that a movie is selected if not flashes a message 
    if request.method =="POST" and request.form.get("menu-tt")== "":
        flash("Please select a movie ")
    elif request.method =="POST":
        tt=request.form.get("menu-tt")
        return redirect(url_for('update_movie',tt=tt))

    return render_template("select_movie.html",page_title="Select Incomplete Movies",
                            movies=movie_data)

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
