import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# User credentials
USER = ""
PASSWORD = ""

# Desired sessions
SESSIONS = [2]
base_session_number = 1

# URLs
URL_LOGIN = 'https://cas.upv.es/cas/login?service=https%3A%2F%2Fwww.upv.es%2Fpls%2Fsoalu%2Fsic_intracas.app_intranet%3FP_CUA%3Dmiupv'
BOOKING_URL = 'https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus=V&p_tipoact=6846&p_codacti=21809&p_vista=intranet&p_idioma=c'

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=chrome_options)

def login(driver):
    driver.get(URL_LOGIN)
    # Explicit wait for login elements
    wait = WebDriverWait(driver, 5)
    user = wait.until(ec.presence_of_element_located((By.ID, 'username')))
    user.send_keys(USER)
    password = driver.find_element(By.ID, 'password')
    password.send_keys(PASSWORD)
    password.submit()
    time.sleep(2)
    if "cas/login?" in driver.current_url:
        raise Exception("Auth error.")

# The base code is the value of the parameter "p_codgrupo_mat" on the first available session
# of the week. With this code and knowing the session number, the rest of codes can be calculated.
def get_base_code(driver):
    driver.get(BOOKING_URL)
    link = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//a[contains(@href, "p_codgrupo_mat")]')))
    url = link.get_attribute('href')
    base_code = url.split('p_codgrupo_mat=')[1].split('&')[0]

    link_text = link.text
    match = re.search(r'MUS(\d{3})', link_text)
    if not match:
        raise ValueError("Base session number not found in the link text.")
    global base_session_number
    base_session_number = int(match.group(1))

    return base_code[:14]

def reserve_hour(driver, session_code, session):
    driver.get(
        f'https://intranet.upv.es/pls/soalu/sic_depact.HSemActMatri?'
        f'p_campus=V&p_codacti=21549&p_codgrupo_mat={session_code}'
        f'&p_vista=intranet&p_tipoact=6799&p_idioma=c'
    )
    try:
        WebDriverWait(driver, 2).until(
            ec.presence_of_element_located((By.XPATH, f'//*[contains(text(), "MUSCULACIÓN 0{session}")]')))
        return True
    except TimeoutException:
        return False

def main():
    driver = setup_driver()
    try:
        login(driver)
        base = get_base_code(driver)
        print(f"Obtained base: {base}")

        for num_session in SESSIONS:
            session_code = hex(int(base, 16) + num_session - base_session_number)[2:].upper()
            print(f"Booking MUS{num_session:03d} ({session_code})...")
            if reserve_hour(driver, session_code, num_session):
                print("Reserved Successfully!")
                SESSIONS.remove(num_session)
            else:
                print(f"Error in the booking process of the session: MUS{num_session}")
                print("The session is probably still taken. Trying again in 30 seconds...")
            time.sleep(3)

    finally:
        driver.quit()

print("Script started. Trying to reserve the taken sessions...")
while len(SESSIONS) > 0:
    main()
    time.sleep(30)
print("All sessions have been reserved.")