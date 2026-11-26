
import os
import csv
import time
import re

from urllib.parse import unquote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

# ==========================================
# TC-TEL-07 - CALL BUTTON (MICROSIP)
# ==========================================

# TEST ACCOUNT CREDENTIALS

EMAIL = "dranheirdejesus@gmail.com"
PASSWORD = "ABCabc123!"

# TEST DATA

LEAD_NAME = "Only Drans"
LEAD_PHONE = "0491570006"

URL = "https://sortrleaddistribution-client.onrender.com/"

TIMEOUT = 120

# ==========================================
# EVIDENCE FOLDER
# ==========================================

EVIDENCE_FOLDER = "TC-TEL-07_Evidence"

os.makedirs(EVIDENCE_FOLDER, exist_ok=True)

# ==========================================
# CONFIGURE CHROME
# ==========================================

options = webdriver.ChromeOptions()

options.add_argument("--start-maximized")
options.add_argument("--force-device-scale-factor=0.8")

driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, TIMEOUT)

driver.set_page_load_timeout(TIMEOUT)
driver.set_script_timeout(TIMEOUT)
driver.implicitly_wait(0)

# ==========================================
# TEST VARIABLES
# ==========================================

results = []

test_start = time.monotonic()

deadline = None

current_step = "Precondition"

precondition_passed = False
precondition_timeout = False

actual_phone = ""
call_href = ""

call_link_clicked = False
phone_verified = False

# ==========================================
# TIMER FUNCTIONS
# ==========================================

def start_timer():

    global deadline

    start = time.monotonic()

    deadline = start + TIMEOUT

    return start


def remaining_time():

    if deadline is None:

        return TIMEOUT

    remaining = deadline - time.monotonic()

    if remaining <= 0:

        raise TimeoutException(
            f"Execution exceeded {TIMEOUT} seconds."
        )

    return remaining


def check_timer():

    remaining_time()


def step_wait():

    return WebDriverWait(
        driver,
        remaining_time(),
        poll_frequency=0.25
    )


# ==========================================
# SCREENSHOT FUNCTION
# ==========================================

def screenshot(filename):

    path = os.path.join(
        EVIDENCE_FOLDER,
        filename
    )

    try:

        if driver.save_screenshot(path):

            print(f"Screenshot saved: {path}")

    except Exception as error:

        print(f"Screenshot error: {error}")


# ==========================================
# NORMALIZE AUSTRALIAN PHONE NUMBER
# ==========================================

def normalize_phone(number):

    number = re.sub(
        r"[^0-9]",
        "",
        str(number)
    )

    # Convert Australian international format
    # 61491570006 into 0491570006.

    if number.startswith("61") and len(number) == 11:

        number = "0" + number[2:]

    return number


# ==========================================
# PRECONDITION - AUTOMATIC LOGIN
# ==========================================

def login():

    print("\nOpening application...")

    driver.get(URL)

    print("Application opened successfully.")

    print("\nLogging in...")

    email_field = step_wait().until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                'input[type="email"]'
            )
        )
    )

    email_field.clear()
    email_field.send_keys(EMAIL)

    print("Email entered.")

    password_field = step_wait().until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                'input[type="password"]'
            )
        )
    )

    password_field.clear()
    password_field.send_keys(PASSWORD)

    print("Password entered.")

    login_button = step_wait().until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[normalize-space()='Log In']"
            )
        )
    )

    login_button.click()

    print("Login button clicked.")

    print("Waiting for Dashboard...")

    step_wait().until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[normalize-space()='DASHBOARD']"
            )
        )
    )

    print("------------------------------------------")
    print("LOGIN: PASSED")
    print("Dashboard is displayed.")
    print("------------------------------------------")

    screenshot(
        "Precondition_Login_Success.png"
    )


# ==========================================
# PRECONDITION - OPEN ASSIGNED LEADS
# ==========================================

def open_assigned_leads():

    print("\nOpening Assigned Leads page...")

    leads_link = step_wait().until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//li[contains(@class,'ps-menuitem-root')]"
                "[.//*[normalize-space()='Leads']]"
            )
        )
    )

    leads_link.click()

    step_wait().until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[normalize-space()='ASSIGNED LEADS']"
            )
        )
    )

    print("Assigned Leads page opened successfully.")

    screenshot(
        "Precondition_Assigned_Leads.png"
    )


# ==========================================
# FIND TARGET LEAD ROW
# ==========================================

def find_target_row():

    return step_wait().until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[@role='row']"
                f"[.//*[@title='{LEAD_NAME}' "
                f"or normalize-space()='{LEAD_NAME}']]"
            )
        )
    )


# ==========================================
# STEP 1 - LOCATE LEAD IN ASSIGNED LEADS
# ==========================================

def locate_lead():

    global actual_phone

    print("\nSearching for target lead...")

    print(f"Target Lead: {LEAD_NAME}")
    print(f"Target Phone Number: {LEAD_PHONE}")

    search_box = step_wait().until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                'input[placeholder="Search"]'
            )
        )
    )

    search_box.clear()
    search_box.send_keys(LEAD_NAME)

    print("Search term entered.")

    target_row = find_target_row()

    if not target_row.is_displayed():

        raise AssertionError(
            "The target lead is not visible."
        )

    # Find the correct phone number
    # inside the selected lead row.

    cells = target_row.find_elements(
        By.CSS_SELECTOR,
        "[role='gridcell'], td"
    )

    actual_phone = ""

    for cell in cells:

        cell_value = cell.text.strip()

        if not re.fullmatch(
            r"[+0-9()\s-]+",
            cell_value
        ):

            continue

        if normalize_phone(cell_value) == normalize_phone(LEAD_PHONE):

            actual_phone = cell_value

            break

    if not actual_phone:

        raise AssertionError(
            "Target lead found, but the phone "
            "number does not match the test data."
        )

    driver.execute_script(
        "arguments[0].scrollIntoView("
        "{block:'center', inline:'center'});",
        target_row
    )

    print("------------------------------------------")
    print("TARGET LEAD FOUND")
    print(f"Lead Name: {LEAD_NAME}")
    print(f"Expected Phone: {LEAD_PHONE}")
    print(f"Actual Phone: {actual_phone}")
    print("Phone number matched.")
    print("------------------------------------------")

    screenshot(
        "Step_01_Lead_Found.png"
    )

    return (
        "Target lead successfully located "
        "with the correct phone number."
    )


# ==========================================
# STEP 2 - CLICK MICROSIP CALL BUTTON
# ==========================================

def click_call_button():

    global call_href
    global call_link_clicked
    global phone_verified

    print("\nLocating MicroSIP Call link...")

    target_row = find_target_row()

    # Use the exact locator from the
    # original working MicroSIP code.
    #
    # Locate the link inside the target row
    # instead of searching the entire page.

    call_link = step_wait().until(
        lambda d: target_row.find_element(
            By.CSS_SELECTOR,
            'a[aria-label="Call lead with MicroSIP"]'
        )
    )

    call_href = (
        call_link.get_attribute("href")
        or ""
    )

    print("MicroSIP Call link located.")
    print(f"Call Link: {call_href}")

    # ======================================
    # VERIFY CALLTO PROTOCOL
    # ======================================

    if not call_href.lower().startswith("callto:"):

        raise AssertionError(
            "The Call link does not use "
            "the callto protocol."
        )

    print("Callto protocol verified.")

    # ======================================
    # VERIFY PHONE NUMBER
    # ======================================

    linked_phone = unquote(
        call_href.split(":", 1)[1]
    ).strip()

    if not re.fullmatch(
        r"[+0-9()\s-]+",
        linked_phone
    ):

        raise AssertionError(
            f"Unexpected Call link format: {call_href}"
        )

    normalized_expected = normalize_phone(
        LEAD_PHONE
    )

    normalized_actual = normalize_phone(
        linked_phone
    )

    print(f"Expected Phone: {LEAD_PHONE}")
    print(f"Call Link Phone: {linked_phone}")

    if normalized_expected != normalized_actual:

        raise AssertionError(
            "The Call link contains an incorrect "
            "phone number. The link was not clicked."
        )

    phone_verified = True

    print("------------------------------------------")
    print("PHONE NUMBER VERIFIED")
    print(f"Expected Number: {normalized_expected}")
    print(f"Actual Number: {normalized_actual}")
    print("------------------------------------------")

    # ======================================
    # SCROLL CALL LINK INTO VIEW
    # ======================================

    driver.execute_script(
        "arguments[0].scrollIntoView("
        "{block:'center', inline:'center'});",
        call_link
    )

    step_wait().until(
        EC.element_to_be_clickable(
            call_link
        )
    )

    screenshot(
        "Step_02_Before_Call_Click.png"
    )

    # ======================================
    # CLICK MICROSIP CALL LINK
    # ======================================

    print("\nClicking MicroSIP Call icon...")

    call_link.click()

    call_link_clicked = True

    print("MicroSIP Call link clicked successfully.")

    screenshot(
        "Step_02_After_Call_Click.png"
    )

    print("------------------------------------------")
    print("CALL LINK ACTIVATION VERIFIED")
    print(f"Protocol: callto:")
    print(f"Phone Number: {LEAD_PHONE}")
    print("MicroSIP dial pad requires visual verification.")
    print("------------------------------------------")

    return (
        "Correct MicroSIP Call link clicked. "
        "The external dial pad must be visually verified."
    )


# ==========================================
# RECORD TEST RESULTS
# ==========================================

def record_result(
    step,
    description,
    status,
    details,
    elapsed
):

    results.append({
        "Step": step,
        "Test Scenario": description,
        "Lead Name": LEAD_NAME,
        "Expected Phone Number": LEAD_PHONE,
        "Actual Phone Number": actual_phone,
        "Call Link": call_href,
        "Status": status,
        "Details": details,
        "Execution Time (Seconds)": round(
            elapsed,
            2
        )
    })

    print("------------------------------------------")
    print(f"STEP {step}: {status}")
    print(f"Details: {details}")
    print(f"Execution Time: {elapsed:.2f} seconds")
    print(f"Time Limit: {TIMEOUT} seconds")
    print("------------------------------------------")

    screenshot(
        f"Step_{step:02d}_{status.replace(' ', '_')}.png"
    )


# ==========================================
# EXECUTE TEST STEP WITH TIMER
# ==========================================

def execute_step(
    step,
    description,
    action
):

    global current_step
    global deadline

    current_step = (
        f"Step {step}: {description}"
    )

    start = start_timer()

    status = "PASSED"
    details = ""

    print()
    print("==========================================")
    print(current_step)
    print(f"TIME LIMIT: {TIMEOUT} SECONDS")
    print("==========================================")

    try:

        details = action()

        check_timer()

        if step == 2:

            status = "PARTIALLY VERIFIED"

    except TimeoutException:

        status = "FAILED"

        details = (
            f"TIMEOUT: Step did not execute "
            f"within {TIMEOUT} seconds."
        )

        print()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"STEP {step}: FAILED")
        print("REASON: EXECUTION TIMEOUT")
        print(f"TIME LIMIT: {TIMEOUT} SECONDS")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    except Exception as error:

        status = "FAILED"

        details = str(error)

    finally:

        elapsed = time.monotonic() - start

        if elapsed >= TIMEOUT:

            status = "FAILED"

            details = (
                f"TIMEOUT: Execution exceeded "
                f"{TIMEOUT} seconds."
            )

        record_result(
            step,
            description,
            status,
            details,
            elapsed
        )

        deadline = None

    if status == "FAILED":

        raise RuntimeError(
            f"Step {step} failed: {details}"
        )


# ==========================================
# MAIN TEST EXECUTION
# ==========================================

try:

    print()
    print("==========================================")
    print("TC-TEL-07")
    print("CALL BUTTON - MICROSIP")
    print(f"LEAD NAME: {LEAD_NAME}")
    print(f"PHONE NUMBER: {LEAD_PHONE}")
    print(f"TIMEOUT: {TIMEOUT} SECONDS")
    print("==========================================")

    # ======================================
    # PRECONDITION 1 - LOGIN
    # ======================================

    current_step = "Precondition: Login"

    start_timer()

    login()

    check_timer()

    # ======================================
    # PRECONDITION 2 - ASSIGNED LEADS
    # ======================================

    current_step = (
        "Precondition: Assigned Leads"
    )

    start_timer()

    open_assigned_leads()

    check_timer()

    precondition_passed = True

    deadline = None

    # ======================================
    # STEP 1 - LOCATE LEAD
    # ======================================

    execute_step(
        1,
        "Locate Lead in Assigned Leads",
        locate_lead
    )

    # ======================================
    # STEP 2 - CLICK CALL ICON
    # ======================================

    execute_step(
        2,
        "Click MicroSIP Call Icon",
        click_call_button
    )

    screenshot(
        "Final_Browser_Result.png"
    )


# ==========================================
# TIMEOUT ERROR HANDLER
# ==========================================

except TimeoutException:

    precondition_timeout = True

    print()
    print("==========================================")
    print("TC-TEL-07: FAILED")
    print("------------------------------------------")
    print(f"Failed at: {current_step}")
    print("Reason: EXECUTION TIMEOUT")
    print(f"Time Limit: {TIMEOUT} seconds")
    print("Current URL:", driver.current_url)
    print("==========================================")

    screenshot(
        "TC-TEL-07_Timeout.png"
    )


# ==========================================
# GENERAL ERROR HANDLER
# ==========================================

except Exception as error:

    print()
    print("==========================================")
    print("TC-TEL-07: EXECUTION STOPPED")
    print("------------------------------------------")
    print(f"Stopped at: {current_step}")
    print("Error Type:", type(error).__name__)
    print("Error Details:", error)
    print("==========================================")

    screenshot(
        "TC-TEL-07_Execution_Stopped.png"
    )


# ==========================================
# FINAL TEST SUMMARY
# ==========================================

finally:

    deadline = None

    total_execution_time = (
        time.monotonic() - test_start
    )

    print()
    print("==========================================")
    print("TC-TEL-07: FINAL TEST SUMMARY")
    print("==========================================")

    for result in results:

        print(
            f"Step {result['Step']}: "
            f"{result['Test Scenario']}"
        )

        print(f"Result: {result['Status']}")
        print(f"Details: {result['Details']}")

        print(
            f"Execution Time: "
            f"{result['Execution Time (Seconds)']:.2f} "
            "seconds"
        )

        print("------------------------------------------")

    passed = sum(
        result["Status"] == "PASSED"
        for result in results
    )

    failed = sum(
        result["Status"] == "FAILED"
        for result in results
    )

    partial = sum(
        result["Status"] == "VERIFIED"
        for result in results
    )

    timed_out = sum(
        result["Status"] == "FAILED"
        and "TIMEOUT" in result["Details"]
        for result in results
    )

    if precondition_timeout:

        timed_out += 1

    not_executed = 2 - len(results)

    print()
    print("==========================================")
    print("TOTAL TEST RESULTS")
    print("==========================================")

    print(
        "Precondition: "
        + (
            "PASSED"
            if precondition_passed
            else "NOT SATISFIED"
        )
    )

    print("Total Test Steps: 2")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Partially Verified: {partial}")
    print(f"Timeout Failures: {timed_out}")
    print(f"Not Executed: {not_executed}")

    print("------------------------------------------")

    print(f"Lead Name: {LEAD_NAME}")
    print(f"Expected Phone Number: {LEAD_PHONE}")
    print(f"Actual Phone Number: {actual_phone or 'N/A'}")
    print(f"MicroSIP Call Link: {call_href or 'N/A'}")

    print(
        "Phone Number Verified: "
        + ("YES" if phone_verified else "NO")
    )

    print(
        "Call Link Clicked: "
        + ("YES" if call_link_clicked else "NO")
    )

    print(
        "Total Execution Time: "
        f"{total_execution_time:.2f} seconds"
    )

    print("------------------------------------------")

    if precondition_timeout or failed > 0:

        final_result = "FAILED"

    elif not precondition_passed:

        final_result = "BLOCKED"

    elif partial > 0:

        final_result = "VERIFIED"

    elif passed == 2:

        final_result = "PASSED"

    else:

        final_result = "NOT FULLY VERIFIED"

    print(f"FINAL RESULT: {final_result}")

    if call_link_clicked:

        print()
        print("MANUAL VERIFICATION:")
        print("Check that MicroSIP opens with:")
        print(LEAD_PHONE)

    # ======================================
    # EXPORT CSV TEST REPORT
    # ======================================

    csv_path = os.path.join(
        EVIDENCE_FOLDER,
        "TC-TEL-07_Test_Results.csv"
    )

    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "Step",
                "Test Scenario",
                "Lead Name",
                "Expected Phone Number",
                "Actual Phone Number",
                "Call Link",
                "Status",
                "Details",
                "Execution Time (Seconds)"
            ]
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print(f"Test Results: {csv_path}")
    print(f"Evidence Folder: {EVIDENCE_FOLDER}")
    print("==========================================")

    try:

        input(
            "\nPress Enter to close the browser..."
        )

    finally:

        driver.quit()
