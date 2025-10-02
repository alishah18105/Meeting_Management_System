# 📌 Meeting Management System

A full-stack Flask + PostgreSQL web app that helps users **schedule, join, and manage meetings** efficiently. It provides a clean dashboard, role-based features, and an integrated calendar for better collaboration.

---

## 🚀 Features

* 🔑 **User Authentication**

  * Sign up with name, email, and password (passwords are securely hashed).
  * Login system to verify users and redirect them to the dashboard.

* 🏠 **Meeting Dashboard**

  * Sidebar menu with options: **Menu, Chat, Meeting, Tracking, Report, Calendar, Setting**.
  * Menu shows 4 cards: **Total Meetings, Room Availability, Reports, Calendar**.

* 📅 **Meetings**

  * **New Meeting**: Form to create a meeting with title, description, room, start/end time, and status.

    * Saved into `meetings` table.
    * Automatically creates a card under **Hosted By You**.

  * **Join Meeting**: Enter meeting ID to join.

    * Shows up under **Joined Meetings**.
  * **Schedule Meeting** and **Share Screen** (basic flow set, further work planned).

* 🔔 **Notifications** *(to be implemented)*

  * Will notify users about upcoming meetings.

* 📆 **Calendar View** 

  * Meetings will be displayed in a calendar for better visibility.

---

## 🛠️ Tech Stack

* **Frontend**: HTML, CSS, Bootstrap
* **Backend**: Python, Flask
* **Database**: PostgreSQL with SQLAlchemy ORM

---

## 🗄️ Database Schema

* `users` – stores user info (name, email, password)
* `organizer` – stores user ID of meeting creator
* `meetings` – stores meeting details (title, description, time, status, room)
* `participants` – links users to meetings they join
* `rooms` – meeting rooms with ID, name, capacity, time
* `notifications` – stores meeting related alerts 

---
## 📂 Project Structure

meeting-management-system/  
│── app.py                # Main Flask application entry point  
│── models.py             # Database models (SQLAlchemy ORM)  
│── requirements.txt      # Project dependencies  

├── templates/            # HTML templates  
│   ├── calendar.html  
│   ├── login.html  
│   ├── meeting.html  
│   ├── MeetingDashboard.html  
│   ├── menu.html
│   └── signup.html  

├── static/               # Static assets  
│   ├── css/  
│   │   └── style.css  
│   └── images/  
│       └── (project images)  

---

## ▶️ Getting Started

1. Clone the repository

   ```bash
   git clone https://github.com/your-username/meeting-management-system.git
   cd meeting-management-system
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Configure PostgreSQL database in `app.config`.

4. Run the app

   ```bash
   flask run
   ```

---

## 👥 Contributors  

| [<img src="https://github.com/alishah18105.png" width="100px;" alt="Syed Ali Sultan"/>](https://github.com/alishah18105) | [<img src="https://github.com/neharehan2005.png" width="100px;" alt="Neha Rehan"/>](https://github.com/neharehan2005) |
|:---:|:---:|
| **Syed Ali Sultan** | **Neha Rehan** |
