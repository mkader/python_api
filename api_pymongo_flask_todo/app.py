# https://stackabuse.com/integrating-mongodb-with-flask-using-flask-pymongo
# Integrating MongoDB with Flask Using Flask-PyMongo
# There are several Flask extensions for integrating MongoDB, here using the Flask-PyMongo extension.
# Flask installed, pip install flask
# set up Flask-PyMongo, which is a wrapper around the PyMongo python package.
# PyMongo is a low-level wrapper around MongoDB, it uses commands similar to MongoDB CLI commands for: Creating, Accessing & Modifying data
# install Flask-PyMongo, pip install Flask-PyMongo
# The Flask-PyMongo extension provides a low-level API (very similar to the official MongoDB language) for communicating with MongoDB instance.
# The extension also provides several helper methods so we can avoid having to write too much boilerplate code.
# In this article, integrate MongoDB with our Flask app, performed some CRUD operations, and work with files with MongoDB using GridFS.

# Connecting to a MongoDB Database Instance with Flask, importing Flask and Flask-PyMongo into our app:
from flask_pymongo import PyMongo
import flask

# create a Flask app object:
app = flask.Flask(__name__)

# use to initialize our MongoDB client. The PyMongo Constructor (imported from flask_pymongo) accepts our Flsk app object, and a database URI string.
mongodb_client = PyMongo(app, uri="mongodb://mongodbuser:MongoDb123!@cluster0-shard-00-00.oek74.mongodb.net:27017,cluster0-shard-00-01.oek74.mongodb.net:27017,cluster0-shard-00-02.oek74.mongodb.net:27017/python_api_db?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
db = mongodb_client.db

# The URI string could also be assigned to the key MONGO_URI in app.config
#app.config["MONGO_URI"] = "mongodb://mongodbuser:..."
#mongodb_client = PyMongo(app)
#db = mongodb_client.db

# Create Documents - Adding New Items to the Database, use the db.colection.insert_one() method
# ----------------
@app.route("/add_one")
def add_one():
    db.todos.insert_one({'title': "todo title", 'body': "todo body"})
    return flask.jsonify(message="success")

#  create many entries at once using the db.colection.insert_many() method
@app.route("/add_many")
def add_many():
    db.todos.insert_many([
        {'_id': 1, 'title': "todo title one ", 'body': "todo body one "},
        {'_id': 2, 'title': "todo title two", 'body': "todo body two"},
        {'_id': 3, 'title': "todo title three", 'body': "todo body three"},
        {'_id': 1, 'title': "todo title four", 'body': "todo body four"},
        {'_id': 4, 'title': "todo title five", 'body': "todo body five"},
        {'_id': 5, 'title': "todo title six", 'body': "todo body six"},
        ])
    return flask.jsonify(message="success")
    
#.BulkWriteError: batch op errors occurred - Error will be thrown if any duplicate record add, meaning that only records up to duplicate will be inserted, and everything after the duplicate will be lost (so in this case record duplicate "1" throws error, record 4 and 5 won't insert).
#Insert only valid and unique records in our list, we will have to set the ordered parameter of the insert_many() method to false and then catch the BulkWriteError exception:

from pymongo.errors import BulkWriteError

@app.route("/add_many_ordered")
def add_many_ordered():
    try:
        todo_many = db.todos.insert_many([
            {'_id': 1, 'title': "todo title one ", 'body': "todo body one "},
            {'_id': 8, 'title': "todo title two", 'body': "todo body two"},
            {'_id': 2, 'title': "todo title three", 'body': "todo body three"},
            {'_id': 9, 'title': "todo title four", 'body': "todo body four"},
            {'_id': 10, 'title': "todo title five", 'body': "todo body five"},
            {'_id': 5, 'title': "todo title six", 'body': "todo body six"},
        ], ordered=False)
    except BulkWriteError as e:
        return flask.jsonify(message="duplicates encountered and ignored",
                             details=e.details,
                             inserted=e.details['nInserted'],
                             duplicates=[x['op'] for x in e.details['writeErrors']])

    return flask.jsonify(message="success", insertedIds=todo_many.inserted_ids)

''' 
# This approach will insert all of the valid documents into the MongoDB collection. Additionally, it'll log the details of the failed additions and print it back to the user.
# response 
{
    "details": {
        "nInserted": 2,
        "nMatched": 0,
        "nModified": 0,
        "nRemoved": 0,
        "nUpserted": 0,
        "upserted": [],
        "writeConcernErrors": [],
        "writeErrors": [
            {                 "code": 11000,
                "errmsg": "E11000 duplicate key error collection: python_api_db.todos index: _id_ dup key: { _id: 1 }",
                "index": 0,
                "keyPattern": {                     "_id": 1                 },
                "keyValue": {                     "_id": 1                 },
                "op": {                     "_id": 1,                     "body": "todo body one ",                     "title": "todo title one "                 }             },
            {                 "code": 11000,
                "errmsg": "E11000 duplicate key error collection: python_api_db.todos index: _id_ dup key: { _id: 8 }",
                "index": 1,
                "keyPattern": {                     "_id": 1                 },
               ...            },
	...
        ]
    },
    "duplicates": [
        {             "_id": 1,             "body": "todo body one ",             "title": "todo title one "         },
        {             "_id": 8,             "body": "todo body two",             "title": "todo title two"         },
	...
    ],
    "inserted": 2,
    "message": "duplicates encountered and ignored"
}
'''

# Read Documents - Retrieving Data From the Database
# --------------
# Flask-PyMongo provides several methods (extended from PyMongo) and some helper methods for retrieving data from the database.
# To retrieve all the documents from the todos collection, use the db.collection.find() method. the find_one() method returns one document, given its ID.
@app.route("/")
def home():
    todos = db.todos.find()
    return flask.jsonify([todo for todo in todos])

# The find() method can also take an optional filter parameter. This filter parameter is represented with a dictionary
# Query document where the `id` field is `3` {"id":3}
# Query document where both `id` is `3` and `title` is `Special todo` {"id":3, "title":"Special todo"}
# Query using special operator - Greater than Or Equal To, denoted with the dollar sign and name ($gte) {"id" : {$gte : 5}}
# Some other special operators include the $eq, $ne, $gt, $lt, $lte and $nin operators.
@app.route("/get_todo/<int:todoId>")
def insert_one(todoId):
    todo = db.todos.find_one({"_id": todoId})
    return flask.jsonify(todo)

# request to http://localhost:5000/get_todo/5, the default Flask server port 5000, but it can be easily changed while creating a Flask app object
# Flask-PyMongo provides a helper function, the find_one_or_404() method which will raise a 404 error if the requested resource was not found.

# Update and Replace Documents - use the update_one() or the replace_one() method to change the value of an existing entity.
# replace_one() has the following arguments:
#   filter - A query which defines which entries will be replaced.
#   replacement - Entries that will be put in their place when replaced.
#   {} - A configuration object which has a few options, of which well be focusing on - upsert.
# upsert, when set to true will insert replacement as a new document if there are no filter matches in the database. And if there are matches, then it puts replacement in its stead. 
#  upsert if false and you try updating a document that doesn't exist, nothing will happen.
import datetime
import json

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    #raise TypeError("Unknown type")

@app.route("/replace_todo/<int:todoId>")
def replace_one(todoId):
    result = db.todos.replace_one({'_id': todoId}, {'title': "modified title2"})
    #return flask.jsonify(result.raw_result), getting error  => TypeError: Object of type 'Timestamp' is not JSON serializable
    return json.dumps(result.raw_result, default=datetime_handler)

@app.route("/update_todo/<int:todoId>")
def update_one(todoId):
    result = db.todos.update_one({'_id': todoId}, {"$set": {'title': "updated title"}})
    return json.dumps(result.raw_result, default=datetime_handler)

# find_one_and_update() and find_one_and_replace() - that will update an entry and return that entry:
@app.route("/replace1_todo/<int:todoId>")
def replace1_one(todoId):
    todo = db.todos.find_one_and_replace({'_id': todoId}, {'title': "modified title"})
    return flask.jsonify(todo)

@app.route("/update1_todo/<int:todoId>")
def update1_one(todoId):
    result = db.todos.find_one_and_update({'_id': todoId}, {"$set": {'title': "updated title"}})
    return flask.jsonify(result)

# bulk updates with the update_many() method, it find and update all entries with the title "todo title two" and response{ "n": 1, "nModified": 1, "ok": 1.0, "updatedExisting": true }
# if no update then "n": 0 
@app.route('/update_many')
def update_many():
    todo = db.todos.update_many({'title' : 'todo title two'}, {"$set": {'body' : 'updated body'}})
    return json.dumps(todo.raw_result, default=datetime_handler)

# Deleting Documents - deleting a single or a collection of entries using the delete_one() and the delete_many() methods
# -----------------
@app.route("/delete_todo/<int:todoId>", methods=['DELETE'])
def delete_todo(todoId):
    todo = db.todos.delete_one({'_id': todoId})
    return json.dumps(todo.raw_result, default=datetime_handler)

# alternatively use the find_one_and_delete() method that deletes and returns the deleted item, to avoid using the unhandy result object:
@app.route("/delete1_todo/<int:todoId>", methods=['DELETE'])
def delete1_todo(todoId):
    todo = db.todos.find_one_and_delete({'_id': todoId})
    if todo is not None:
        return json.dumps(todo.raw_result)
    return "ID does not exist"
    
# delete in bulk, using the delete_many() method:
# output if deleted "n": 2, if not record deleted then "n": 0 = > {"n": 2, "opTime": {"ts": null, "t": 67},...}
@app.route('/delete_many', methods=['DELETE'])
def delete_many():
    todo = db.todos.delete_many({'title': 'todo title two'})
    return json.dumps(todo.raw_result, default=datetime_handler)

# Saving and Retrieving Files
# ---------------------------
# MongoDB allows us to save binary data to its database using the GridFS specification.
# Flask-PyMongo provides the save_file() method for saving a file to GridFS and the send_file() method for retrieving files from GridFS.
from flask import request
@app.route("/save_file", methods=['POST', 'GET'])
def save_file():
    upload_form = """<h1>Save file</h1>
                     <form method="POST" enctype="multipart/form-data">
                     <input type="file" name="file" id="file">
                     <br><br>
                     <input type="submit">
                     </form>"""
                     
    if request.method=='POST':
        if 'file' in request.files:
            file = request.files['file']
            mongodb_client.save_file(file.filename, file)
            return json.dumps({"file name": file.filename})
    return upload_form
    
# retrieve the file or raise a 404 error if the file was not found
@app.route("/get_file/<filename>")
def get_file(filename):
    return mongodb_client.send_file(filename)

app.run(debug=True)