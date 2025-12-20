from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

PRICING_CONFIG = {
    "base_price_per_hour": 300,
    "indoor_premium_per_hour": 200,
    "peak_hours": {
        "start": 18,
        "end": 21,
        "multiplier": 1.5
    },
    "weekend_multiplier": 1.2,
    "equipment": {
        "racket": 100,
        "shoes": 150
    },
    "coach_price_per_hour": 400
}
@app.route('/price', methods=['POST'])
def calculate_price():
    data = request.get_json()

    court_type = data.get("court_type")   
    start_time = data.get("start_time")  
    date = data.get("date")              
    hours = data.get("hours")
    equipment = data.get("equipment", []) 
    coach = data.get("coach")             

    if not court_type or not start_time or not date or not hours:
        return jsonify({"error": "Missing required fields"}), 400

    total = PRICING_CONFIG["base_price_per_hour"]

    # Indoor premium
    if court_type == "indoor":
        total += PRICING_CONFIG["indoor_premium_per_hour"]

    # Peak hours check
    start_hour = int(start_time.split(":")[0])
    peak = PRICING_CONFIG["peak_hours"]
    if peak["start"] <= start_hour < peak["end"]:
        total *= peak["multiplier"]

    # Weekend check
    booking_date = datetime.strptime(date, "%Y-%m-%d")
    if booking_date.weekday() >= 5:  # Saturday / Sunday
        total *= PRICING_CONFIG["weekend_multiplier"]

    # Equipment pricing
    equipment_cost = 0
    for item in equipment:
        equipment_cost += PRICING_CONFIG["equipment"].get(item, 0)

    # Coach pricing
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

if __name__ == "__main__":
    app.run(port=5000, debug=True)
