♻️ Trashmandu: Smart Plastic Waste Management System
Trashmandu is a role-based plastic waste collection and recycling platform built using Django. It enables users to schedule plastic waste pickups, get paid based on the weight (e.g., Rs. 12/kg), and allows collectors and admins to manage operations through dedicated dashboards. The project aims to promote environmental responsibility and streamline waste management digitally in Nepal.

🌿 Features
🔹 Role-Based System
User:

Register & log in

Schedule plastic pickup with Google Maps location

Enter plastic weight

See pickup history and earnings

Collector:

Register with age and ID verification

Accept/reject pickup requests

View total pickups & earnings

Admin:

View and manage all user and collector activities

Assign requests manually to collectors

Dashboard for monitoring all operations

📦 Plastic Waste Value
Rs. 12 per kg of plastic collected (configurable)

🗺️ Google Maps Integration
Users can pin their exact pickup location

Admins and collectors view locations on map

🛠️ Tech Stack
Backend: Django (Python)

Frontend: HTML, CSS (Green eco-theme), Bootstrap

Database: SQLite3 (default, can be upgraded)

Map API: Google Maps API

Authentication: Role-based login (User / Collector / Admin)

Others: Email verification (Collector), file upload for citizenship proof

🚀 Getting Started
1. Clone the Repo
bash
Copy
Edit
git clone https://github.com/yourusername/trashmandu.git
cd trashmandu
2. Setup Environment
bash
Copy
Edit
python -m venv env
source env/bin/activate    # or env\Scripts\activate on Windows
pip install -r requirements.txt
3. Run the Server
bash
Copy
Edit
python manage.py migrate
python manage.py runserver
4. Access the App
Visit: http://127.0.0.1:8000/

📂 Project Structure
arduino
Copy
Edit
trashmandu/
├── userapp/
├── collectorapp/
├── adminapp/
├── templates/
│   ├── userapp/
│   ├── collectorapp/
│   ├── adminapp/
│   └── home.html
├── static/
├── db.sqlite3
├── manage.py
└── README.md
✅ What We Did
Designed a 3-role waste management system

Integrated map location-based pickup requests

Developed a beautiful green-themed UI

Implemented profit calculation (based on plastic weight)

Built a custom admin panel for full monitoring

🌍 Why Trashmandu?
Nepal generates over 2.7 tons of plastic waste daily, but recycling systems are disorganized. Trashmandu bridges this gap by:

Digitizing the pickup process

Encouraging recycling through payment incentives

Creating transparency between users, collectors, and administrators

🚧 Limitations
No mobile app version (yet)

Real-time tracking of collectors not available

Payment gateway (Fonepay/eSewa) integration is in progress

🔮 Future Scope
Add real-time tracking for collectors using GPS

Launch Android/iOS apps for broader access

Automate collector assignment using AI

Expand to other types of waste (e-waste, organic, etc.)

Integrate e-wallets for seamless transactions

🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss.

📜 License
MIT License © 2025 Anup Shrestha

🌱 Let’s Clean Green with Trashmandu ♻️
"Clean city, healthy life. Your plastic, our responsibility."

