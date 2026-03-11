# GymAutoBooker — UPV Gym Session Auto-Reservation

Automatically reserve gym sessions at the **Polytechnic University of Valencia (UPV)** intranet. Includes multiple approaches — lightweight HTTP requests and Selenium-based browser automation — to cover different use cases: scheduled weekly booking, visual debugging, and sniping taken sessions.

---

## Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Scripts](#-scripts)
  - [Requests — taken\_sessions\_booker.py](#requests--taken_sessions_bookerpy)
  - [Selenium — auto\_booker.py](#selenium--auto_bookerpy)
  - [Selenium — visual\_auto\_booker.py](#selenium--visual_auto_bookerpy)
  - [Selenium — taken\_sessions\_booker.py](#selenium--taken_sessions_bookerpy)
- [How It Works](#-how-it-works)
- [Disclaimer](#-disclaimer)

---

## Features

- **Scheduled booking** — Automatically reserves sessions every Saturday when the new week opens.
- **Taken-session sniping** — Continuously retries booking fully-booked sessions until a spot opens up.
- **Two implementations** — A fast, lightweight `requests`-based version and a `selenium`-based version.
- **Headless & visual modes** — Run headless on a server or with a visible browser for debugging.

---

## Project Structure

```
GymAutoBooker/
├── README.md
├── Requests/
│   └── taken_sessions_booker.py   # Lightweight HTTP-only session sniper
└── Selenium/
    ├── auto_booker.py             # Headless scheduled weekly booker
    ├── visual_auto_booker.py      # Visual (non-headless) scheduled weekly booker
    └── taken_sessions_booker.py   # Headless taken-session sniper
```

---

## Prerequisites

- **Python 3.8+**
- A valid **UPV intranet account** (CAS login)
- For Selenium scripts: **Google Chrome** and a compatible **ChromeDriver**

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/<your-username>/GymAutoBooker.git
   cd GymAutoBooker
   ```

2. **Install dependencies:**

   For the **Requests** version:
   ```bash
   pip install requests
   ```

   For the **Selenium** versions:
   ```bash
   pip install selenium schedule
   ```

---

## Configuration

Each script contains the following variables at the top that you need to fill in:

| Variable   | Description                                                                             |
|------------|-----------------------------------------------------------------------------------------|
| `USER`     | Your UPV CAS username.                                                                  |
| `PASSWORD` | Your UPV CAS password.                                                                  |
| `SESSIONS` | List of session numbers to book (e.g., `[2, 9, 10]` for MUS002, MUS009, MUS010).       |

### Requests version — environment variable support

The `Requests/taken_sessions_booker.py` script also reads sessions from the `SESSIONS` environment variable (comma-separated):

```bash
# Example: book sessions 2 and 5
export SESSIONS="2,5"
python Requests/taken_sessions_booker.py
```

If the environment variable is not set, it defaults to session `2`.

---

## Scripts

### Requests — `taken_sessions_booker.py`

> **Location:** `Requests/taken_sessions_booker.py`

A lightweight, pure-HTTP implementation that **does not require a browser**. It uses Python's `requests` library to authenticate via the UPV CAS portal and attempt to book sessions that are already taken.

```bash
python Requests/taken_sessions_booker.py
```

- Retries every **30 seconds** until all desired sessions are reserved.
- Best suited for running on a **server or headless environment** with minimal resource usage.

---

### Selenium — `auto_booker.py`

> **Location:** `Selenium/auto_booker.py`

A **headless** Selenium script that schedules automatic booking every **Saturday at 10:01 AM (Europe/Madrid)**, which is when the UPV gym opens bookings for the next week.

```bash
python Selenium/auto_booker.py
```

- Runs indefinitely, executing the booking routine on schedule.
- Ideal for a **server or always-on machine**.

---

### Selenium — `visual_auto_booker.py`

> **Location:** `Selenium/visual_auto_booker.py`

Same as `auto_booker.py` but opens a **visible Chrome window** so you can watch the automation in real time.

```bash
python Selenium/visual_auto_booker.py
```

- Useful for **debugging and testing** the booking flow.
- Also scheduled for every Saturday at 10:01 AM.

---

### Selenium — `taken_sessions_booker.py`

> **Location:** `Selenium/taken_sessions_booker.py`

A **headless** Selenium script that continuously tries to book sessions that are already full, hoping to snag a spot when someone cancels.

```bash
python Selenium/taken_sessions_booker.py
```

- Retries every **30 seconds** until all desired sessions are reserved.
- The browser-based counterpart of `Requests/taken_sessions_booker.py`.

---

## How It Works

1. **Authentication** — The script logs in to the UPV CAS portal using your credentials and follows the redirect chain into the intranet.

2. **Base code discovery** — On the gym booking page, the first available session link contains a `p_codgrupo_mat` parameter. This hexadecimal code serves as the **base code**. The session number (e.g., MUS001, MUS002, …) is extracted from the link text.

3. **Code calculation** — Each session's booking code is derived by simple hex arithmetic:
   ```
   session_code = base_code + (desired_session - base_session_number)
   ```

4. **Reservation** — The script navigates to (or sends a GET request to) the booking URL with the calculated code. Success is confirmed by checking for a confirmation message in the response.

---

## Disclaimer

This project is intended for **personal and educational use only**. Use it responsibly and in accordance with the UPV's terms of service. The authors are not responsible for any misuse or consequences arising from the use of this tool.
