from datetime import datetime
import time
import logging
import undetected_chromedriver as uc
from twocaptcha import TwoCaptcha
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.common.exceptions import NoSuchElementException
import gmail_helper as gmail

URL = "https://www.vfsglobal.ca/IRCC-AppointmentWave1/?q=shSA0YnE4pLF9Xzwon/x/CQ1P0LBKn66dLdNUfueK+wj/xwjQV05sWPtysuvzK33iLEPsMoeoCx0P5WTj7UF52YsUOWsPggpuCPlo4C6FYdk6EdnrxOuPzH4tfHLGzb8YqQmXrLHDnBMw5lHXC4nsckTHANsMEi0PLe2SeucS40="
LOGIN_TITLE = "VFS : Registered Login"
HOME_TITLE = "VFS : HOME PAGE"
SCHEDULE_APPOINTMENT_TITLE = "VFS : Schedule Appointment"
INCOMPLETE_APPLICATION_TITLE = "VFS : Track InComplete Application"
APPLICANT_LIST_TITLE = "VFS : Applicant List"
BOOKING_APPOINTMENT_TITLE = "VFS : Booking Appointment"
CLOUDFLARE_TITLE = "Just a moment..."
EXCEPTION_TITLE = "VFS : Exception Found"

EMAIL = "example@gmail.com"
PASSWORD = "qwerty123"
PHONE_NUMBER = "991234567"

logging.basicConfig(format='%(asctime)s %(levelname)s : %(message)s')
log = logging.getLogger()
log.setLevel(level='INFO')

two_captcha = TwoCaptcha('000')


def wait_user_input():
    log.warning('Press any key to continue.')
    input()


def main():
    options = uc.ChromeOptions()

    # setting profile
    options.user_data_dir = "C:\\Users\\danil\\Desktop\\bot-profile"

    # another way to set profile is the below (which takes precedence if both variants are used
    options.add_argument('--user-data-dir=C:\\Users\\danil\\Desktop\\bot-profile')

    # just some options passing in to skip annoying popups
    options.add_argument('--no-first-run --no-service-autorun --password-store=basic')

    # Interact in background fix
    # https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/708
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-backgrounding-occluded-windows")

    # Use CloudFlare WARP
    # options.add_argument("--proxy-server=socks5://127.0.0.1:1488")

    # options.headless = True
    # options.add_argument("--headless")

    driver = uc.Chrome(options=options)

    wait = WebDriverWait(driver, timeout=3 * 60)

    gmail_client = gmail.setup_gmail_client()
    gmail_wait = WebDriverWait(driver, timeout=4 * 60, poll_frequency=1.3)

    last_run = None
    fail_retry_count = 0

    while True:
        if fail_retry_count > 5:
            wait_user_input()
            fail_retry_count = 0

        now = datetime.now()

        after_work_hours = now.weekday() == 5 or now.weekday() == 6 or now.hour < 8 or now.hour >= 17
        if (after_work_hours and last_run is not None and ((now.timestamp() - last_run.timestamp()) < 90 * 60)) \
                or (not after_work_hours and (now.minute < 20 or 30 <= now.minute < 50) or (last_run is not None and now.timestamp() - last_run.timestamp() < 3 * 60)):
            time.sleep(1)
            continue

        last_run = now

        log.info("Attempt begin")

        try:
            skip_login = False
            if BOOKING_APPOINTMENT_TITLE in driver.title:
                try:
                    driver.find_element(By.CSS_SELECTOR, "#btnBack").click()
                    skip_login = APPLICANT_LIST_TITLE in driver.title
                except NoSuchElementException:
                    pass
            elif LOGIN_TITLE not in driver.title:
                driver.get(URL)

            if not skip_login:
                log.info("Using full action chain")

                # In case CloudFlare protection page triggered
                if CLOUDFLARE_TITLE in driver.title:
                    wait.until(ExpectedConditions.element_to_be_clickable((By.CSS_SELECTOR,
                                                                           "div#challenge-stage > #cf-challenge-hcaptcha-wrapper > div:not([style]) > .captcha-solver"))).click()

                email_el = driver.find_element(By.ID, "EmailId")
                email_el.clear()
                email_el.send_keys(EMAIL)
                password_el = driver.find_element(By.ID, "Password")
                password_el.clear()
                password_el.send_keys(PASSWORD)

                if driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha"):
                    wait.until(ExpectedConditions.element_to_be_clickable(
                        (By.CSS_SELECTOR, ".g-recaptcha > div > div.captcha-solver"))).click()
                    wait.until(ExpectedConditions.text_to_be_present_in_element_attribute(
                        (By.CSS_SELECTOR, ".g-recaptcha > div > div.captcha-solver"),
                        "data-state", "solved"))
                elif driver.find_elements(By.CSS_SELECTOR, ".customcapcha"):
                    wait.until(ExpectedConditions.presence_of_element_located((By.CSS_SELECTOR, "#CaptchaImage"))).screenshot("captcha.png")
                    result = two_captcha.normal("captcha.png")['code'].upper()
                    captcha_input_el = driver.find_element(By.CSS_SELECTOR, "#CaptchaInputText")
                    captcha_input_el.clear()
                    captcha_input_el.send_keys(result)

                driver.find_element(By.CSS_SELECTOR, "div.frm-button > input.submitbtn").click()

                if EXCEPTION_TITLE in driver.title:
                    log.error("VFS reported exception")
                    continue

                driver.find_element(By.CSS_SELECTOR,
                                    'div.leftpanel-links > ul.leftNav-ul > li > a[href=\"/IRCC-AppointmentWave1/Home/SearchAppointment?q=dePiaPfL2MJ7yDPEmQRU6buv0a4SqqvgSfMfLcEJhU/6UnikKwvVRTTaULbIYxyOyQzn4zK/139hZCYECOHJuw==\"]').click()

                driver.find_element(By.ID, "txtContactNumber").send_keys(PHONE_NUMBER)
                # Click Search button twice. First click removes focus from phone field, second clicks button.
                submit_btn = wait.until(ExpectedConditions.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'].submitbtn")))
                submit_btn.click()
                submit_btn.click()

                wait.until(ExpectedConditions.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                     "body > div.wrapper > div.main-container > div.rightpanel > div.frm-container > table > tbody > tr:nth-child(2) > td:nth-child(5) > a.btn"))).click()
            else:
                log.info("Using reduced action chain. Skipping login stage")

            if not after_work_hours:
                while now.minute < 27 or 30 < now.minute < 57 or now.second < 30:
                    now = datetime.now()
            wait.until(ExpectedConditions.element_to_be_clickable(
                (By.CSS_SELECTOR, "#ApplicantListForm > div.frm-button > input"))).click()
            if driver.find_elements(By.CSS_SELECTOR, "#OTPe"):
                log.info("OTP requested")

                log.info("Waiting for OTP")
                otp_code = gmail_wait.until(gmail.otp_message_to_be_present(gmail_client))
                log.info("Got OTP")

                driver.find_element(By.CSS_SELECTOR, "#OTPe").send_keys(otp_code)

                if not after_work_hours:
                    # FIXME: timings are incorrect frequently
                    time.sleep((60 if now.minute >= 30 else 30) * 60 - (now.minute * 60 + now.second))

                driver.find_element(By.CSS_SELECTOR, "#txtsub").click()
                log.info("Sent OTP")

            el = driver.find_element(By.CSS_SELECTOR, '#inline-popups > form > div.validation-summary-errors > ul > li')
            if not el.text:
                log.info("!!! Found available slots?")
            else:
                log.info(el.text)

            success = False

            calendar_header = driver.find_element(By.CSS_SELECTOR, "#calendar > table > tr > td.fc-header-center > span > h2")
            last_calendar_header_value = None
            cal_index = 3
            while cal_index:
                if last_calendar_header_value:
                    wait.until(lambda d: last_calendar_header_value != calendar_header.text)
                last_calendar_header_value = calendar_header.text

                available_dates = driver.find_elements(By.CSS_SELECTOR, "td.fc-day[style$='cursor: pointer;']")  # td.fc-day:not(.fc-other-month)

# FIXME: retry til has available dates and not successful
                while available_dates and not success:
                    log.info(f'Available dates ({last_calendar_header_value}): {" ".join(map(lambda date: date.text, available_dates))}')
                    available_dates[0].click()
                    time_band = driver.find_elements(By.CSS_SELECTOR, "input[name='selectedTimeBand']")
                    time_band[0].click()
                    driver.find_element(By.CSS_SELECTOR, "#btnConfirm").click()
                    alert = driver.switch_to.alert
                    alert.accept()
                    if BOOKING_APPOINTMENT_TITLE not in driver.title:
                        success = True
                        break
                    else:
                        available_dates = driver.find_elements(By.CSS_SELECTOR,
                                                               "td.fc-day[style$='cursor: pointer;']")  # td.fc-day:not(.fc-other-month)

# FIXME: click next only if not available dates
                driver.find_element(By.CSS_SELECTOR, "#calendar > table > tr > td.fc-header-right > span > span").click()
                cal_index -= 1

            now = datetime.now()
            driver.save_screenshot(f'screenshots/{now.strftime("%m-%d-%Y_%H-%M")}.png')
            fail_retry_count = 0
            log.info("Attempt finished successfully")

            if success:
                wait_user_input()
        except Exception:
            fail_retry_count += 1
            log.exception("Exception")


if __name__ == "__main__":
    main()
