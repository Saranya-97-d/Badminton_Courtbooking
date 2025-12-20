from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["court_booking"]

courts_col = db["courts"]
coaches_col = db["coaches"]
equipment_col = db["equipment"]
bookings_col = db["bookings"]
