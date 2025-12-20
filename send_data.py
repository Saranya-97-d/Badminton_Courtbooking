from db import courts_col, coaches_col, equipment_col

# Clear old data (optional for testing)
courts_col.delete_many({})
coaches_col.delete_many({})
equipment_col.delete_many({})

# ---------- COURTS ----------
courts_col.insert_many([
    {"court_id": "indoor_1", "type": "indoor"},
    {"court_id": "indoor_2", "type": "indoor"},
    {"court_id": "outdoor_1", "type": "outdoor"},
    {"court_id": "outdoor_2", "type": "outdoor"}
])

# ---------- COACHES ----------
coaches_col.insert_many([
    {"coach_id": "coach_1", "active": True},
    {"coach_id": "coach_2", "active": True},
    {"coach_id": "coach_3", "active": True}
])

# ---------- EQUIPMENT ----------
equipment_col.insert_many([
    {"item": "racket", "quantity": 5},
    {"item": "shoes", "quantity": 5}
])

print("✅ Seed data inserted successfully")
