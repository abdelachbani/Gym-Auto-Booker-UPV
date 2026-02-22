import html
import re
import time
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests

# User credentials
USER = ""
PASSWORD = ""

# Desired sessions
SESSIONS = [2]
base_session_number = 1

# URLs
URL_LOGIN = 'https://cas.upv.es/cas/login?service=https%3A%2F%2Fwww.upv.es%2Fpls%2Fsoalu%2Fsic_intracas.app_intranet%3FP_CUA%3Dmiupv'
BOOKING_URL = 'https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus=V&p_tipoact=6846&p_codacti=21809&p_vista=intranet&p_idioma=c'

class LoginFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_form = False
        self.done = False
        self.form_action = ""
        self.inputs = {}

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        attrs_dict = dict(attrs)
        if tag == "form" and not self.in_form:
            self.in_form = True
            self.form_action = attrs_dict.get("action", "")
            return
        if tag == "input" and self.in_form:
            name = attrs_dict.get("name")
            if name:
                self.inputs[name] = attrs_dict.get("value", "")

    def handle_endtag(self, tag):
        if tag == "form" and self.in_form:
            self.in_form = False
            self.done = True

def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0 Safari/537.36",
    })
    return session

def login(session):
    response = session.get(URL_LOGIN, timeout=10)
    response.raise_for_status()

    parser = LoginFormParser()
    parser.feed(response.text)
    if not parser.form_action:
        raise Exception("Login form not found.")

    payload = dict(parser.inputs)
    payload.update({
        "username": USER,
        "password": PASSWORD,
    })

    post_url = urljoin(response.url, parser.form_action)
    response = session.post(post_url, data=payload, timeout=10, allow_redirects=True)
    response.raise_for_status()
    if "cas/login" in response.url:
        raise Exception("Auth error.")

# The base code is the value of the parameter "p_codgrupo_mat" on the first available session
# of the week. With this code and knowing the session number, the rest of codes can be calculated.
def get_base_code(session):
    response = session.get(BOOKING_URL, timeout=10)
    response.raise_for_status()

    match_link = re.search(
        r'<a[^>]+href=["\']([^"\']*p_codgrupo_mat=[^"\']+)["\'][^>]*>(.*?)</a>',
        response.text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match_link:
        raise ValueError("Base session link not found.")

    url = html.unescape(match_link.group(1))
    link_text = re.sub(r"<[^>]+>", "", match_link.group(2))
    base_code = url.split('p_codgrupo_mat=')[1].split('&')[0]

    match = re.search(r'MUS(\d{3})', link_text)
    if not match:
        raise ValueError("Base session number not found in the link text.")
    global base_session_number
    base_session_number = int(match.group(1))

    return base_code[:14]

def reserve_hour(session, session_code, session_number):
    url = (
        'https://intranet.upv.es/pls/soalu/sic_depact.HSemActMatri?'
        f'p_campus=V&p_codacti=21549&p_codgrupo_mat={session_code}'
        '&p_vista=intranet&p_tipoact=6799&p_idioma=c'
    )
    response = session.get(url, timeout=10)
    response.raise_for_status()
    text = response.text

    pattern = rf"MUSCULACI.{0,8}0{session_number}"
    return re.search(pattern, text, re.IGNORECASE) is not None

def main():
    session = create_session()
    try:
        login(session)
        base = get_base_code(session)
        print(f"Obtained base: {base}")

        for num_session in list(SESSIONS):
            session_code = hex(int(base, 16) + num_session - base_session_number)[2:].upper()
            print(f"Booking MUS{num_session:03d} ({session_code})...")
            if reserve_hour(session, session_code, num_session):
                print("Reserved Successfully!")
                SESSIONS.remove(num_session)
            else:
                print(f"Error in the booking process of the session: MUS{num_session}")
                print("The session is probably still taken. Trying again in 30 seconds...")
            time.sleep(3)
    except ValueError as e:
        print(f"Error: {e}")
        print("There is probably no available sessions to get the base number from. Retrying in 30 seconds...")
    finally:
        session.close()

print("Script started. Trying to reserve the taken sessions...")
while len(SESSIONS) > 0:
    main()
    time.sleep(30)
print("All sessions have been reserved.")