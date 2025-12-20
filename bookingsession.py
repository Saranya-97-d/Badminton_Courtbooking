from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

from db import bookings_col, equipment_col

app = Flask(__name__)
CORS(app)

# ---------------- PRICING CONFIG ---------------- #

PRICING_CONFIG = {
    "base_price_per_hour": 300,
    "indoor_premium": 200,
    "peak_hours": {"start": 18, "end": 21, "multiplier": 1.5},
    "weekend_multiplier": 1.2,
    "equipment_price": {"racket": 100, "shoes": 150},
    "coach_price_per_hour": 400
}

# ---------------- HELPER FUNCTIONS ---------------- #

def overlaps(existing_start, existing_end, start, end):
    return existing_start < end and start < existing_end


def equipment_available(item, date, start, end):
    total = equipment_col.find_one({"name": item})["total_quantity"]

    used = bookings_col.count_documents({
        "date": date,
        "equipment": item,
        "start_hour": {"$lt": end},
        "end_hour": {"$gt": start}
    })

    return used < total


def coach_available(date, start, end):
    coaches = ["coach_1", "coach_2", "coach_3"]

    for coach in coaches:
        busy = bookings_col.count_documents({
            "coach": coach,
            "date": date,
            "start_hour": {"$lt": end},
            "end_hour": {"$gt": start}
        })
        if busy == 0:
            return coach

    return None

# ---------------- PRICE API ---------------- #

@app.route("/price", methods=["POST"])
def price():
    data = request.get_json()

    court_type = data["court_type"]
    start_time = data["start_time"]
    date = data["date"]
    hours = data["hours"]
    equipment = data.get("equipment", [])
    coach = data.get("coach")

    start_hour = int(start_time.split(":")[0])

    total = PRICING_CONFIG["base_price_per_hour"]

    if court_type == "indoor":
        total += PRICING_CONFIG["indoor_premium"]

    peak = PRICING_CONFIG["peak_hours"]
    if peak["start"] <= start_hour < peak["end"]:
        total *= peak["multiplier"]

    booking_date = datetime.strptime(date, "%Y-%m-%d")
    if booking_date.weekday() >= 5:
        total *= PRICING_CONFIG["weekend_multiplier"]

    equipment_cost = sum(PRICING_CONFIG["equipment_price"].get(i, 0) for i in equipment)
    coach_cost = PRICING_CONFIG["coach_price_per_hour"] if coach else 0

    grand_total = (total + equipment_cost + coach_cost) * hours

    return jsonify({
        "total_price": round(grand_total, 2),
        "base_hour_price": round(total, 2),
        "equipment_cost": equipment_cost * hours,
        "coach_cost": coach_cost * hours
    })

# ---------------- BOOKING API ---------------- #

@app.route("/book", methods=["POST"])
def book():
    data = request.get_json()

    date = data["date"]
    start_hour = int(data["start_time"].split(":")[0])
    hours = data["hours"]
    end_hour = start_hour + hours

    equipment = data.get("equipment", [])
    wants_coach = data.get("coach")

    # Equipment check
    for item in equipment:
        if not equipment_available(item, date, start_hour, end_hour):
            return jsonify({"error": f"{item} not available"}), 409

    # Coach auto assign
    coach = None
    if wants_coach:
        coach = coach_available(date, start_hour, end_hour)
        if not coach:
            return jsonify({"error": "No coach available"}), 409

    # Save booking
    bookings_col.insert_one({
        "court": data["court_type"],
        "date": date,
        "start_hour": start_hour,
        "end_hour": end_hour,
        "equipment": equipment,
        "coach": coach
    })

    return jsonify({
        "message": "Booking confirmed",
        "coach_assigned": coach
    }), 201

# ---------------- VIEW BOOKINGS ---------------- #

@app.route("/bookings", methods=["GET"])
def bookings():
    data = list(bookings_col.find({}, {"_id": 0}))
    return jsonify(data)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(port=5000)
