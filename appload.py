from tools.load_data import load_all

default_config = {'MONGODB_SETTINGS': {
    'host': 'mongodb+srv://mongodbuser:MongoDb123!@cluster0.oek74.mongodb.net/python_api_db?retryWrites=false&w=majority'},
    'JWT_SECRET_KEY': 'changeThisKeyFirst'}

load_all(default_config)