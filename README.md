# Gym Auto Booker UPV
A tool to automatically reserve Gym sessions on the Politechnic University Of Valencia Gym.

## Scripts
### auto_booker.py
With this script you can schedule the program to run
whenever you want. It is used to reserve the gym sessions in
Saturday mornings, where the bookings open for the next week.
It runs only in the console, so no need of graphical interface.
I made this one to run in a server, so it doesn't need to be
interacting with the computer, which means I don't have to
worry about having my computer on while it runs.

### visual_auto_booker.py
This script is the same as the previous one, but it has a
graphical interface, I made this one firstly to test the code
and know what the program was doing.
You can run it in your computer and see how it works.

### taken_sessions_booker.py
This is the last one, I made it so in the middle of the week,
when the gym sessions are already booked, you can run it
if you want to reserve a session that is already taken.
It basically tries to reserve a session that is already taken
so if at any moment someone cancels their session, you can reserve
it automatically.
