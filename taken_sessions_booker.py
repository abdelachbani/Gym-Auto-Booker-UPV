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
BOOKING_URL = 'https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus=V&p_tipoact=6799&p_codacti=21549&p_vista=intranet&p_idioma=c'

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Adds timeout settings to prevent read timeout errors
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(20)
    return driver

def login(driver):
    try:
        driver.get(URL_LOGIN)
        user = driver.find_element(By.NAME, 'username')
        user.send_keys(USER)
        password = driver.find_element(By.NAME, 'password')
        password.send_keys(PASSWORD)
        password.submit()
        time.sleep(2)
        if "cas/login?" in driver.current_url:
            raise Exception("Auth error.")
    except Exception as e:
        print(f"Login error: {str(e)}")
        driver.quit()
        return False
    return True

# The base code is the value of the parameter "p_codgrupo_mat" on the first available session
# of the week. With this code and knowing the session number, the rest of codes can be calculated.
def get_base_code(driver):
    try:
        driver.get(BOOKING_URL)
        link = WebDriverWait(driver, 20).until(
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
    except Exception as e:
        print(f"Error getting base code: {str(e)}")
        return None

def reserve_hour(driver, session_code, session):
    try:
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
    except Exception as e:
        print(f"Error in reserve_hour: {str(e)}")
        return False

def main():
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        driver = None
        try:
            driver = setup_driver()
            if not login(driver):
                continue

            base = get_base_code(driver)
            if not base:
                continue

            print(f"Obtained base: {base}")

            for num_session in SESSIONS[:]:  # Create a copy to iterate
                session_code = hex(int(base, 16) + num_session - base_session_number)[2:].upper()
                print(f"Booking MUS{num_session:03d} ({session_code})...")
                if reserve_hour(driver, session_code, num_session):
                    print("Reserved Successfully!")
                    SESSIONS.remove(num_session)
                else:
                    print(f"Error in the booking process of the session: MUS{num_session}")
                    print("The session is probably still taken. Trying again in 30 seconds...")
                time.sleep(1)

            break

        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            retry_count += 1
            time.sleep(5)

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

print("Script started. Trying to reserve the taken sessions...")
while len(SESSIONS) > 0:
    main()
    time.sleep(30)
print("All sessions have been reserved.")