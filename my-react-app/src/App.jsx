import React, { useState, useEffect } from "react";

function App() {
  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [hours, setHours] = useState(1);
  const [courtType, setCourtType] = useState("");
  const [equipmentCount, setEquipmentCount] = useState({ racket: 0, shoes: 0 });
  const [coach, setCoach] = useState(false);
  const [priceData, setPriceData] = useState(null);
  const [bookingMessage, setBookingMessage] = useState("");

  // Convert counts to array for backend
  const equipmentArray = [];
  Object.keys(equipmentCount).forEach((item) => {
    for (let i = 0; i < equipmentCount[item]; i++) {
      equipmentArray.push(item);
    }
  });

  // Fetch price whenever inputs change
  useEffect(() => {
    if (!courtType || !date || !startTime) return;

    const data = {
      court_type: courtType,
      date,
      start_time: startTime,
      hours,
      equipment: equipmentArray,
      coach
    };

    fetch("http://localhost:5000/price", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
      .then((res) => res.json())
      .then(setPriceData)
      .catch((err) => console.error(err));
  }, [courtType, date, startTime, hours, equipmentCount, coach]);

  // Adjust booking hours
  const changeHours = (val) => {
    setHours((prev) => Math.max(1, prev + val));
  };

  // Adjust equipment count
  const changeEquipment = (item, delta) => {
    setEquipmentCount((prev) => ({
      ...prev,
      [item]: Math.max(0, prev[item] + delta)
    }));
  };

  // Handle booking
  const handleBooking = () => {
    if (!courtType || !date || !startTime) return;

    const data = {
      court_type: courtType,
      date,
      start_time: startTime,
      hours,
      equipment: equipmentArray,
      coach
    };

    fetch("http://localhost:5000/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
      .then((res) => res.json())
      .then((res) => {
        if (res.message) setBookingMessage(res.message);
        else setBookingMessage(res.error || "Booking failed");
      })
      .catch((err) => console.error(err));
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h3>Badminton Booking</h3>

        <div style={styles.row}>
          <label>Sport</label>
          <input type="text" value="Badminton" disabled />
        </div>

        <div style={styles.row}>
          <label>Date</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>

        <div style={styles.row}>
          <label>Start Time</label>
          <input
            type="time"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
          />
        </div>

        <div style={styles.row}>
          <label>Duration</label>
          <div style={styles.duration}>
            <button onClick={() => changeHours(-1)}>−</button>
            <span>{hours} Hr</span>
            <button onClick={() => changeHours(1)}>+</button>
          </div>
        </div>

        <div style={styles.row}>
          <label>Court</label>
          <select
            value={courtType}
            onChange={(e) => setCourtType(e.target.value)}
          >
            <option value="">-- Select Court --</option>
            <option value="indoor">Indoor Court</option>
            <option value="outdoor">Outdoor Court</option>
          </select>
        </div>

        {/* Equipment selection with counts */}
        <div style={styles.row}>
          <label>Racket</label>
          <button onClick={() => changeEquipment("racket", -1)}>−</button>
          <span>{equipmentCount.racket}</span>
          <button onClick={() => changeEquipment("racket", 1)}>+</button>
        </div>
        <div style={styles.row}>
          <label>Shoes</label>
          <button onClick={() => changeEquipment("shoes", -1)}>−</button>
          <span>{equipmentCount.shoes}</span>
          <button onClick={() => changeEquipment("shoes", 1)}>+</button>
        </div>

        <div style={styles.row}>
          <label>
            <input
              type="checkbox"
              checked={coach}
              onChange={(e) => setCoach(e.target.checked)}
            />
            Coach
          </label>
        </div>

        {priceData && (
          <div style={styles.priceBox}>
            <p>Base: ₹{priceData.base_hour_price}</p>
            <p>Equipment: ₹{priceData.equipment_cost}</p>
            <p>Coach: ₹{priceData.coach_cost}</p>
            <strong>Total: ₹{priceData.total_price}</strong>
          </div>
        )}

        <button
          style={{
            ...styles.bookBtn,
            backgroundColor: priceData ? "#28a745" : "#ccc"
          }}
          onClick={handleBooking}
          disabled={!priceData}
        >
          Add To Cart
        </button>

        {bookingMessage && (
          <p style={{ marginTop: "10px" }}>{bookingMessage}</p>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    fontFamily: "Arial",
    display: "flex",
    justifyContent: "center",
    paddingTop: 40
  },
  card: {
    background: "#fff",
    padding: 20,
    width: 350,
    borderRadius: 8,
    boxShadow: "0 0 10px rgba(0,0,0,0.1)"
  },
  row: { marginBottom: 12, display: "flex", alignItems: "center", gap: "10px" },
  duration: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  priceBox: { background: "#f0f0f0", padding: 10, marginTop: 10 },
  bookBtn: { width: "100%", border: "none", padding: 10, marginTop: 10, color: "#fff", cursor: "pointer" }
};

export default App;
