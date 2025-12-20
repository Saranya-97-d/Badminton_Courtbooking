from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from db import bookings_col, courts_col, coaches_col

app = Flask(__name__)
CORS(app)

# PRICING rules
PRICING_CONFIG = {
    "base_price_per_hour": 300,
    "indoor_premium_per_hour": 200,
    "peak_hours": {"start": 18, "end": 21, "multiplier": 1.5},
    "weekend_multiplier": 1.2,
    "equipment": {"racket": 100, "shoes": 150},
    "coach_price_per_hour": 400
}

# checking Overlapping
def is_overlapping(existing_start_time, existing_hours, start, hours):
    """Check if two bookings overlap"""
    existing_start = int(existing_start_time.split(":")[0])
    existing_end = existing_start + existing_hours
    return start < existing_end and (start + hours) > existing_start

def find_available_coach(date, start_hour, hours):
    """Find a coach not booked at the given date/time"""
    for c in coaches_col.find({"active": True}):
        clash = False
        for b in bookings_col.find({"coach": c["coach_id"], "date": date}):
            if is_overlapping(b["start_time"], b["hours"], start_hour, hours):
                clash = True
                break
        if not clash:
            return c["coach_id"]
    return None

# PRICE API
@app.route("/price", methods=["POST"])
def calculate_price():
    data = request.get_json()

    court_type = data.get("court_type")
    start_time = data.get("start_time")
    date = data.get("date")
    hours = data.get("hours")
    equipment = data.get("equipment", [])
    coach = data.get("coach", False)

    if not court_type or not start_time or not date or not hours:
        return jsonify({"error": "Missing required fields"}), 400

    total = PRICING_CONFIG["base_price_per_hour"]

    if court_type == "indoor":
        total += PRICING_CONFIG["indoor_premium_per_hour"]

    start_hour = int(start_time.split(":")[0])
    peak = PRICING_CONFIG["peak_hours"]
    if peak["start"] <= start_hour < peak["end"]:
        total *= peak["multiplier"]

    booking_date = datetime.strptime(date, "%Y-%m-%d")
    if booking_date.weekday() >= 5:  # Saturday or Sunday
        total *= PRICING_CONFIG["weekend_multiplier"]

    equipment_cost = sum(PRICING_CONFIG["equipment"].get(i, 0) for i in equipment)
    coach_cost = PRICING_CONFIG["coach_price_per_hour"] if coach else 0

    grand_total = (total + equipment_cost + coach_cost) * hours

    return jsonify({
        "hours": hours,
        "court_type": court_type,
        "base_hour_price": round(total, 2),
        "equipment_cost": equipment_cost * hours,
        "coach_cost": coach_cost * hours,
        "total_price": round(grand_total, 2)
    })

# BOOKING API 
@app.route("/book", methods=["POST"])
def book():
    data = request.get_json()

    court_type = data["court_type"]
    date = data["date"]
    start_time = data["start_time"]
    hours = data["hours"]
    equipment = data.get("equipment", [])
    coach_needed = data.get("coach", False)

    start_hour = int(start_time.split(":")[0])

    
    court = courts_col.find_one({"type": court_type})
    if not court:
        return jsonify({"error": "No court available"}), 409

    
    for b in bookings_col.find({"court": court["court_id"], "date": date}):
        if is_overlapping(b["start_time"], b["hours"], start_hour, hours):
            return jsonify({"error": "Court already booked"}), 409

    
    coach_id = None
    if coach_needed:
        coach_id = find_available_coach(date, start_hour, hours)
        if not coach_id:
            return jsonify({"error": "No coach available"}), 409

    bookings_col.insert_one({
        "court": court["court_id"],
        "date": date,
        "start_time": start_time,
        "hours": hours,
        "equipment": equipment,
        "coach": coach_id
    })

    return jsonify({"message": "Booking confirmed"}), 201

# GET ALL BOOKINGS
@app.route("/bookings", methods=["GET"])
def get_bookings():
    all_bookings = list(bookings_col.find({}, {"_id": 0}))
    return jsonify(all_bookings)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
