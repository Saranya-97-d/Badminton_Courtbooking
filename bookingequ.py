from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from collections import Counter
from db import bookings_col, courts_col, coaches_col, equipment_col

app = Flask(__name__)
CORS(app)

# OPERATING HOURS  #
OPEN_TIME = "06:00"
CLOSE_TIME = "23:00"

#  PRICING CONFIG  #
PRICING_CONFIG = {
    "base_price_per_hour": 300,
    "indoor_premium_per_hour": 200,
    "peak_hours": {"start": 18, "end": 21, "multiplier": 1.5},
    "weekend_multiplier": 1.2,
    "equipment": {"racket": 100, "shoes": 150},
    "coach_price_per_hour": 400
}

# TIME HELPERS  #
def time_to_minutes(time_str):
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def is_overlapping(existing_start_time, existing_hours, new_start_time, new_hours):
    existing_start = time_to_minutes(existing_start_time)
    existing_end = existing_start + (existing_hours * 60)

    new_start = time_to_minutes(new_start_time)
    new_end = new_start + (new_hours * 60)

    return new_start < existing_end and new_end > existing_start


def is_within_operating_hours(start_time, hours):
    start = time_to_minutes(start_time)
    end = start + (hours * 60)

    return (
        start >= time_to_minutes(OPEN_TIME)
        and end <= time_to_minutes(CLOSE_TIME)
    )

# -COACH LOGIC #
def find_available_coach(date, start_time, hours):
    for c in coaches_col.find({"active": True}):
        clash = False
        for b in bookings_col.find({"coach": c["coach_id"], "date": date}):
            if is_overlapping(b["start_time"], b["hours"], start_time, hours):
                clash = True
                break
        if not clash:
            return c["coach_id"]
    return None

# EQUIPMENT LOGIC #
def equipment_available(item, date, start_time, hours, requested_qty):
    eq_doc = equipment_col.find_one({"item": item})
    if not eq_doc:
        return False

    total = eq_doc["quantity"]
    used = 0

    for b in bookings_col.find({"date": date}):
        if is_overlapping(b["start_time"], b["hours"], start_time, hours):
            used += b.get("equipment", []).count(item)

    return used + requested_qty <= total

# PRICE API #
@app.route("/price", methods=["POST"])
def calculate_price():
    data = request.get_json()

    court_type = data.get("court_type")
    start_time = data.get("start_time")
    date = data.get("date")
    hours = data.get("hours")
    equipment_list = data.get("equipment", [])
    coach = data.get("coach", False)

    if not court_type or not start_time or not date or not hours:
        return jsonify({"error": "Missing required fields"}), 400

    if not is_within_operating_hours(start_time, hours):
        return jsonify({
            "error": f"Bookings allowed only between {OPEN_TIME} and {CLOSE_TIME}"
        }), 400

    total = PRICING_CONFIG["base_price_per_hour"]
    if court_type == "indoor":
        total += PRICING_CONFIG["indoor_premium_per_hour"]

    start_hour = int(start_time.split(":")[0])
    peak = PRICING_CONFIG["peak_hours"]
    if peak["start"] <= start_hour < peak["end"]:
        total *= peak["multiplier"]

    booking_date = datetime.strptime(date, "%Y-%m-%d")
    if booking_date.weekday() >= 5:
        total *= PRICING_CONFIG["weekend_multiplier"]

    equipment_counts = Counter(equipment_list)
    equipment_cost = sum(
        PRICING_CONFIG["equipment"].get(k, 0) * v
        for k, v in equipment_counts.items()
    )

    coach_cost = PRICING_CONFIG["coach_price_per_hour"] if coach else 0
    grand_total = (total + equipment_cost + coach_cost) * hours

    return jsonify({
        "base_hour_price": round(total, 2),
        "equipment_cost": equipment_cost * hours,
        "coach_cost": coach_cost * hours,
        "total_price": round(grand_total, 2)
    })

# BOOK API #
@app.route("/book", methods=["POST"])
def book():
    data = request.get_json()

    court_type = data["court_type"]
    date = data["date"]
    start_time = data["start_time"]
    hours = data["hours"]
    equipment_list = data.get("equipment", [])
    coach_needed = data.get("coach", False)

    if not is_within_operating_hours(start_time, hours):
        return jsonify({
            "error": f"Court open only from {OPEN_TIME} to {CLOSE_TIME}"
        }), 409

    court = courts_col.find_one({"type": court_type})
    if not court:
        return jsonify({"error": "No court available"}), 409

    for b in bookings_col.find({"court": court["court_id"], "date": date}):
        if is_overlapping(b["start_time"], b["hours"], start_time, hours):
            return jsonify({"error": "Court already booked"}), 409

    equipment_counts = Counter(equipment_list)
    for item, qty in equipment_counts.items():
        if not equipment_available(item, date, start_time, hours, qty):
            return jsonify({"error": f"Not enough {item} available"}), 409

    coach_id = None
    if coach_needed:
        coach_id = find_available_coach(date, start_time, hours)
        if not coach_id:
            return jsonify({"error": "No coach available"}), 409

    bookings_col.insert_one({
        "court": court["court_id"],
        "date": date,
        "start_time": start_time,
        "hours": hours,
        "equipment": equipment_list,
        "coach": coach_id
    })

    return jsonify({"message": "Booking confirmed", "coach_assigned": coach_id}), 201

#  GET BOOKINGS  #
@app.route("/bookings", methods=["GET"])
def get_bookings():
    return jsonify(list(bookings_col.find({}, {"_id": 0})))

# RUN APP #
if __name__ == "__main__":
    app.run(port=5000, debug=True)
