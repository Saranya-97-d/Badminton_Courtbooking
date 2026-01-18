import React, { useState, useEffect } from "react";
import "./App.css";
import "./index.css"
function App() {
  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [hours, setHours] = useState(1);
  const [courtType, setCourtType] = useState("");
  const [equipmentCount, setEquipmentCount] = useState({ racket: 0, shoes: 0 });
  const [coach, setCoach] = useState(false);
  const [priceData, setPriceData] = useState(null);
  const [bookingMessage, setBookingMessage] = useState("");

  const equipmentArray = [];
  Object.keys(equipmentCount).forEach((item) => {
    for (let i = 0; i < equipmentCount[item]; i++) {
      equipmentArray.push(item);
    }
  });

  useEffect(() => {
    if (!courtType || !date || !startTime) return;

    fetch("http://localhost:5000/price", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        court_type: courtType,
        date,
        start_time: startTime,
        hours,
        equipment: equipmentArray,
        coach
      })
    })
      .then((res) => res.json())
      .then(setPriceData)
      .catch(console.error);
  }, [courtType, date, startTime, hours, equipmentCount, coach]);

  const changeHours = (val) => {
    setHours((prev) => Math.max(1, prev + val));
  };

  const changeEquipment = (item, delta) => {
    setEquipmentCount((prev) => ({
      ...prev,
      [item]: Math.max(0, prev[item] + delta)
    }));
  };

  const handleBooking = () => {
    if (!priceData) return;

    fetch("http://localhost:5000/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        court_type: courtType,
        date,
        start_time: startTime,
        hours,
        equipment: equipmentArray,
        coach
      })
    })
      .then((res) => res.json())
      .then((res) =>
        setBookingMessage(res.message || res.error || "Booking failed")
      )
      .catch(console.error);
  };

  return (
    <div className="container">
      <div className="card">
        <h3>Badminton Booking</h3>

        <div className="row">
          <label>Sport</label>
          <input type="text" value="Badminton" disabled />
        </div>

        <div className="row">
          <label>Date</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>

        <div className="row">
          <label>Start Time</label>
          <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
        </div>

        <div className="row">
          <label>Duration</label>
          <div className="controls">
            <button className="icon-btn" onClick={() => changeHours(-1)}>−</button>
            <span>{hours} Hr</span>
            <button className="icon-btn" onClick={() => changeHours(1)}>+</button>
          </div>
        </div>

        <div className="row">
          <label>Court</label>
          <select value={courtType} onChange={(e) => setCourtType(e.target.value)}>
            <option value="">-- Select Court --</option>
            <option value="indoor">Indoor Court</option>
            <option value="outdoor">Outdoor Court</option>
          </select>
        </div>

        <div className="row">
          <label>Racket</label>
          <div className="controls">
            <button className="icon-btn" onClick={() => changeEquipment("racket", -1)}>−</button>
            <span>{equipmentCount.racket}</span>
            <button className="icon-btn" onClick={() => changeEquipment("racket", 1)}>+</button>
          </div>
        </div>

        <div className="row">
          <label>Shoes</label>
          <div className="controls">
            <button className="icon-btn" onClick={() => changeEquipment("shoes", -1)}>−</button>
            <span>{equipmentCount.shoes}</span>
            <button className="icon-btn" onClick={() => changeEquipment("shoes", 1)}>+</button>
          </div>
        </div>

        <div className="checkbox-row">
          <input type="checkbox" checked={coach} onChange={(e) => setCoach(e.target.checked)} />
          <label>Coach</label>
        </div>

        {priceData && (
          <div className="price-box">
            <p>Base: ₹{priceData.base_hour_price}</p>
            <p>Equipment: ₹{priceData.equipment_cost}</p>
            <p>Coach: ₹{priceData.coach_cost}</p>
            <strong>Total: ₹{priceData.total_price}</strong>
          </div>
        )}

        <button
          className={`book-btn ${priceData ? "active" : ""}`}
          onClick={handleBooking}
          disabled={!priceData}
        >
          Add To Cart
        </button>

        {bookingMessage && <p className="message">{bookingMessage}</p>}
      </div>
    </div>
  );
}

export default App;
