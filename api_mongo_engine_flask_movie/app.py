# creating a simple movie API that allows us to perform CRUD operations
# install pip install flask

# Flask-MongoEngine
# MongoEngine is an ODM (Object Document Mapper) that maps models (classes) to MongoDB documents, making it easy to create and manipulate documents programatically from code.
# pip install flask-mongoengine

# Connecting to a MongoDB Database Instance ngine, to connect Flask app with a MongoDB instance.
# importing Flask and Flask-MongoEngine into our app:
from flask import Flask
from flask_mongoengine import MongoEngine
from flask import Response, request, jsonify

# create the Flask app object
app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    #'host': 'mongodb+srv://mongodbuser:MongoDb123!@cluster0.oek74.mongodb.net/python_api_db?retryWrites=true&w=majority',
    'host': 'mongodb://mongodbuser:MongoDb123!@cluster0-shard-00-00.oek74.mongodb.net:27017,cluster0-shard-00-01.oek74.mongodb.net:27017,cluster0-shard-00-02.oek74.mongodb.net:27017/python_api_db?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority'
    }
    
# initialize a MongoEngine object OR use the init_app() method of the MongoEngine object for the initialization: db = MongoEngine() db.init_app(app)
db = MongoEngine(app)

# Creating Model Classes, MongoEngine uses Python classes to represent documents in our database.
# MongoEngine provides several types of documents classes: 
# Document - a document that has it's own collection in the database
# EmbeddedDocument - a document that doesn't have it's own collection in the database but is embedded into another document:
# DynamicDocument - a document whose fields are added dynamically
# DynamicEmbeddedDocument - This has all the properties of DynamicDocument and EmbeddedDocument  

# Fields are:
# StringField() for string values
# IntField() for int values
# ListField() for a list
# FloatField() for floating point values
# ReferenceField() for referencing other documents
# EmbeddedDocumentField() for embedded documents etc.
# FileField() for storing files (more on this later)

# Apply modifiers in these fields, such as: required, default, unique, primary_key, ...

# EmbeddedDocument - a document that doesn't have it's own collection in the database but is embedded into another document:
class Imdb(db.EmbeddedDocument):
    imdb_id = db.StringField()
    rating = db.DecimalField()
    votes = db.IntField()

# DynamicDocument - a document whose fields are added dynamically    
class Director(db.DynamicDocument):
    pass

# DynamicEmbeddedDocument - This has all the properties of DynamicDocument and EmbeddedDocument      
class Cast(db.DynamicEmbeddedDocument):
    pass

# Document - a document that has it's own collection in the database
class Movie(db.Document):
    title = db.StringField(required=True)
    year = db.IntField()
    rated = db.StringField()
    director = db.ReferenceField(Director)
    cast = db.EmbeddedDocumentListField(Cast)
    poster = db.FileField()
    imdb = db.EmbeddedDocumentField(Imdb)

# Accessing Documents
#---------------------
# get all the movies in the db, localhost:5000/movies/, return JSON:[ { "_id": { "$oid": "600eb604b076cdbc347e2b99"}, "cast": [], "rated": "5", "title": "Movie 1", "year": 1998 },..]
@app.route('/movies')
def  get_movies():
    movies = Movie.objects()
    return  jsonify(movies), 200  

# Flask-MongoEngine allows us to paginate the results very easily:
# The Movie.objects.paginate(page=page, per_page=limit) returns a Pagination object which contains the list of movies in its .items property, iterating through the property
@app.route('/movies/pagination')
def get_movies_pagination():
    page = int(request.args.get('page',1))
    limit = int(request.args.get('limit',5))
    movies = Movie.objects.paginate(page=page, per_page=limit)
    return jsonify([movie for movie in movies.items]), 200

# Getting One Document, by passing the id as a parameter to the Movie.objects(id=id) method, return a set of all movies whose id matches the parameter 
# and first() returns the first Movie object in the queryset, if there are multiple ones. localhost:5000/movies/600eb604b076cdbc347e2b99
@app.route('/movies/<id>')
def get_one_movie(id: str):
    movie = Movie.objects(id=id).first()
    return jsonify(movie), 200

@app.route('/movies-year/<year>')
def get_movie_byyear(year):
    movies = Movie.objects(year=year)
    return jsonify(movies), 200  

# https://www.programmersought.com/article/87625414003/ 
# Raise a 404_NOT_FOUND error if no document matches the provided id. Flask-MongoEngine has got us covered with its first_or_404() and get_or_404() custom querysets
@app.route('/movies/notfound/<id>')
def get_one_movie_404_error(id: str):
    movie = Movie.objects(id=id).first_or_404()
    return jsonify(movie), 200
    
# Creating/Saving Documents, save() method on our model
#---------------------------------------------------------
# **body unpacks the body dictionary into the Movie object as named parameters. For example if body = {"title": "Movie Title", "year": 2015},
# Then Movie(**body) is the same as Movie(title="Movie Title", year=2015)
# request to $ curl -X POST -H "Content-Type: application/json" -d '{"title": "Spider Man 3", "year": 2009, "rated": "5"}' localhost:5000/movies/
# It will save and return the document: { "_id": { "$oid": "600eb604b076cdbc347e2b99"}, "cast": [], "rated": "5", "title": "Spider Man 3", "year": 2009 }
@app.route('/movies/', methods=["POST"])
def add_movie():
    body = request.get_json()
    movie = Movie(**body).save()
    return jsonify(movie), 201

# Creating Documents with EmbeddedDocuments - To add an embedded document, first create the document to embed, then assign it to the appropriate field in our movie model:
# $ curl -X POST -H "Content-Type: application/json" -d '{"title": "Spider", "year": 2016, "rated": "no"}' localhost:5000/movies-embed/
# save and return the newly added document with the embedded document: { "_id": { "$oid": "..."}, "cast": [], "imdb": { "imdb_id": "12340mov", "rating": 4.2, "votes": 7 }, "rated": ...}
@app.route('/movies-embed/', methods=["POST"])
def add_movie_embed():
    # Created Imdb object
    imdb = Imdb(imdb_id="12340mov", rating=4.2, votes=7.9)
    body = request.get_json()
    # Add object to movie and save
    movie = Movie(imdb=imdb, **body).save()
    return jsonify(movie), 201

# Creating Dynamic Documents
# No fields were defined in the model, provide any arbitrary set of fields to dynamic document object.
# Put in any number of fields of any type. You don't even have to have the field types be uniform between multiple documents.
# request curl -X POST -H "Content-Type: application/json" -d '{"name": "James Cameron", "age": 57}' localhost:5000/director/
# response { "_id": {"$oid": "6029111e184c2ceefe175dfe"},"age": 57, name": "James Cameron" }

# There are a few ways to achieve this:
# Approach 1: create the document object with all the fields to add as though a request
@app.route('/director/app1/', methods=['POST'])
def add_dir_app1():
    body = request.get_json()
    director = Director(**body).save()
    return jsonify(director), 201

# Approach 2: create the object first, then add the fields using the dot notation and call the save method.
@app.route('/director/app2/', methods=['POST'])
def add_dir_app2():
    body = request.get_json()
    director = Director()
    director.name = body.get("name")
    director.age = body.get("age")
    director.save()
    return jsonify(director), 201

# Approach 3: use the Python setattr() method:
@app.route('/director/app3/', methods=['POST'])
def add_dir_app3():
    body = request.get_json()
    director = Director()
    setattr(director, "name", body.get("name"))
    setattr(director, "age", body.get("age"))
    director.save()
    return jsonify(director), 201

# Updating Documents, retrieve the persistent document from the db, update its fields and call the update() method on the modified object in memory
#---------------------
# request $ curl -X PUT -H "Content-Type: application/json" -d '{"year": 2016}' localhost:5000/movies/600eb609b076cdbc347e2b9a/
# return the id of the updated document: "600eb609b076cdbc347e2b9a"
@app.route('/movies/<id>', methods=['PUT'])
def update_movie(id):
    body = request.get_json()
    movie = Movie.objects(id=id).first_or_404()
    movie.update(**body)
    return jsonify(str(movie.id)), 200

# Update many documents at once using the update() method. query the db for the documents to update, given some condition, and call the update method on the resulting Queryset:
# $ curl -X PUT -H "Content-Type: application/json" -d '{"year": 2016}' localhost:5000/movies_many/2010/
# return a list of IDs of the updated documents: { "60123af478a2c347ab08c32b", "60123b0989398f6965f859ab", "60123bfe2a91e52ba5434630", "602919f67e80d573ad3f15e4" ]
@app.route('/movies_many/<year>', methods=['PUT'])
def update_movie_many(year):
    body = request.get_json()
    movies = Movie.objects(year=year)
    updated_movies = [str(movie.id) for movie in movies]
    movies.update(**body)
    return jsonify(updated_movies), 200

# Deleting Documents
#--------------------
# request $ curl -X DELETE -H "Content-Type: application/json" -d '{"year": 2016}' localhost:5000/movies/600eb609b076cdbc347e2b9a/
# return the id of the delete document: "600eb609b076cdbc347e2b9a"
@app.route('/movies/<id>', methods=['DELETE'])
def delete_movie(id):
    movie = Movie.objects.get_or_404(id=id)
    movie.delete()
    return jsonify(str(movie.id)), 200

@app.route('/movies/delete-by-year/<year>/', methods=['DELETE'])
def delete_movie_by_year(year):
    movies = Movie.objects(year=year)
    deleted_movies = [str(movie.id) for movie in movies]
    movies.delete()
    return jsonify([str(movie.id) for movie in movies]), 200

# Working with Files
# ------------------
# Creating and Storing Files
# MongoEngine makes it very easy to interface with the MongoDB GridFS for storing and retrieving files. MongoEngine achieves this through its FileField().
# Upload a file to MongoDB GridFS using MongoEngine
# response with an id referencing the image: { "_id": { ... }, "cast": [], "poster": { "$oid": "60123e4d2628f541032a08fe" }, "title": "movie with poster", "year": 2021 }
# JSON response, the file is actually saved as a separate MongoDB document, and we just have a database reference to it.
@app.route('/movies_with_poster', methods=['POST'])
def add_movie_with_image():
    # 1 get image file
    image = request.files['file']
    # 2 create movie object
    movie = Movie(title = "movie with poster", year=2021)
    # 3 Unlike other fields, can't assign a value to the FileField() using the regular assignment operator, instead, use the put() method to send our image. 
    #The put() method takes as arguments the file to be uploaded (this must be a file-like object or a byte stream), the filename, and optional metadata.
    movie.poster.put(image, filename=image.filename)
    # 4
    movie.save()
    # 5
    return jsonify(movie), 201
    
#Retrieving Files - put() a file into a FileField(), read() it back into memory, once we've got an object containing that field. Then retrieve files from MongoDB documents:
from io import BytesIO 
from flask.helpers import send_file

@app.route('/movies_with_poster/<id>/', methods=['GET'])
def get_movie_image(id):
    
    # 1 retrieved the movie document containing an image
    movie = Movie.objects.get_or_404(id=id)
    # 2 saved the image as a string of bytes to the image variable, it contains got the filename and content type
    image = movie.poster.read()
    content_type = movie.poster.content_type
    filename = movie.poster.filename
    # 3 Using Flask's send_file() helper method, try to send the file to the user but since the image is a bytes object, 
    #   throws AttributeError: 'bytes' object has no attribute 'read' as send_file() is expecting a file-like object, not bytes.
    return send_file(
        # 4 To solve this problem, use the BytesIO() class from the io module to decode the bytes object back into a file-like object that send_file() can send.
        BytesIO(image), 
        attachment_filename=filename, 
        mimetype=content_type), 200

# Deleting Files - Deleting documents containing files will not delete the file from GridFS, as they're stored as separate objects.
# To delete the documents and their accompanying files, first delete the file before deleting the document.
# FileField() also provides a delete() method, use to simply delete it from the database and file system, before we go ahead with the deletion of the object itself

@app.route('/movies_with_poster/<id>/', methods=['DELETE'])
def delete_movie_image(id):
    movie = Movie.objects.get_or_404(id=id)
    movie.poster.delete()
    movie.delete()
    return "", 204

app.run(debug=True) 


