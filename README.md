A full-stack Badminton Court Booking Application built with Flask and MongoDB for the backend and React with Vite for the frontend. The system supports court booking, equipment rental, coach booking, dynamic price calculation, and concurrency-safe reservations.
Project Structure:

Badminton_Courtbooking/
│
├── booking.py            # Flask backend
├── db.py                 # MongoDB connection & collections
│
├── my-react-app/         # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
│
└── README.md

**note**
requirements
Flask==3.0.0
flask-cors==4.0.0
pymongo==4.6.1

I am also planning to use  containerize the application  using Docker , allowing all services to run in isolated and consistent environments for easier development and deployment.but for now to run this we should packages present in requirements.txt.
and also For database handling, MongoDB is used as the primary persistent data store to manage courts, bookings, coaches, and equipment data. Redis can additionally be used as an in-memory data store to handle concurrency control, temporary booking locks, and caching of frequently accessed data. Using Redis helps prevent double booking scenarios and improves performance during high-traffic booking requests.
