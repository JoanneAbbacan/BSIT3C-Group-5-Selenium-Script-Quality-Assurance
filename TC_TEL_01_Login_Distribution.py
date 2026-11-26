
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import csv

# ==========================================
# TC-TEL-01: LOGIN X DISTRIBUTION
# ==========================================

# TELEMARKETER ACCOUNT

EMAIL = "dranheirdejesus@gmail.com"
PASSWORD = "ABCabc123!"

URL = "https://sortrleaddistribution-client.onrender.com/"

EXPECTED_LEAD_COUNT = 10

# ==========================================
# CONFIGURE CHROME WINDOW
# ==========================================

options = webdriver.ChromeOptions()

options.add_argument("--start-maximized")
options.add_argument("--force-device-scale-factor=0.8")

driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 120)

current_step = "Step 1: Open Log-In Page"

# ==========================================
# SCREENSHOT EVIDENCE FOLDER
# ==========================================

SCREENSHOT_FOLDER = "TC-TEL-01_Evidence"

os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def screenshot(filename):

    path = os.path.join(
        SCREENSHOT_FOLDER,
        filename
    )

    driver.save_screenshot(path)

    print(f"Screenshot saved: {path}")


def get_lead_rows():

    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "table tbody tr"
    )

    if not rows:

        rows = driver.find_elements(
            By.CSS_SELECTOR,
            '[role="rowgroup"] [role="row"]'
        )

    valid_rows = []

    for row in rows:

        if not row.is_displayed():
            continue

        cells = row.find_elements(
            By.CSS_SELECTOR,
            'td, [role="cell"], [role="gridcell"]'
        )

        if len(cells) < 2:
            continue

        if not row.text.strip():
            continue

        valid_rows.append(row)

    return valid_rows


try:

    print("===================================")
    print("TC-TEL-01: LOGIN X DISTRIBUTION")
    print("===================================")

    # ==========================================
    # STEP 1: OPEN THE LOG-IN PAGE
    # ==========================================

    current_step = "Step 1: Open Log-In Page"

    driver.get(URL)

    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input[type="email"]')
        )
    )

    print("STEP 1 PASSED: Log-In page opened.")

    screenshot("Step_01_Login_Page.png")

    # ==========================================
    # STEP 2: ENTER THE EMAIL
    # ==========================================

    current_step = "Step 2: Enter Email"

    email_field = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input[type="email"]')
        )
    )

    email_field.clear()
    email_field.send_keys(EMAIL)

    assert email_field.get_attribute("value") == EMAIL, (
        "Email input does not match."
    )

    print("STEP 2 PASSED: Email entered.")
    print(f"Email: {EMAIL}")

    # ==========================================
    # STEP 3: ENTER THE PASSWORD
    # ==========================================

    current_step = "Step 3: Enter Password"

    password_field = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input[type="password"]')
        )
    )

    password_field.clear()
    password_field.send_keys(PASSWORD)

    assert password_field.get_attribute("value") == PASSWORD, (
        "Password input does not match."
    )

    print("STEP 3 PASSED: Password entered.")

    # ==========================================
    # STEP 4: CLICK LOG IN
    # ==========================================

    current_step = "Step 4: Click Log In"

    login_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[normalize-space()='Log In']"
            )
        )
    )

    login_button.click()

    print("Log In button clicked.")
    print("Waiting for Telemarketer account to load...")

    # Wait for the Leads sidebar to become available

    leads_locator = (
        By.XPATH,
        "//li[contains(@class,'ps-menuitem-root')]"
        "[.//*[normalize-space()='Leads']]"
    )

    wait.until(
        EC.element_to_be_clickable(
            leads_locator
        )
    )

    print("STEP 4 PASSED: Login successful.")

    screenshot("Step_04_Login_Success.png")

    # ==========================================
    # STEP 5: CLICK LEADS IN THE SIDEBAR
    # ==========================================

    current_step = "Step 5: Open Leads List"

    leads_link = wait.until(
        EC.element_to_be_clickable(
            leads_locator
        )
    )

    leads_link.click()

    print("Leads sidebar clicked.")
    print("Waiting for assigned leads to load...")

    # Wait for the Leads table

    wait.until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                'table, [role="grid"]'
            )
        )
    )

    print("STEP 5 PASSED: Leads table displayed.")

    # ==========================================
    # STEP 6: COUNT THE ASSIGNED LEADS
    # ==========================================

    current_step = "Step 6: Count Assigned Leads"

    print()
    print("===================================")
    print("CHECKING LEAD DISTRIBUTION")
    print("===================================")

    # Allow time for the automatic distribution
    # and loading of assigned lead records.

    try:

        WebDriverWait(driver, 30).until(
            lambda d: len(get_lead_rows()) == EXPECTED_LEAD_COUNT
        )

    except TimeoutException:

        print("Expected lead count was not reached.")

    lead_rows = get_lead_rows()

    actual_lead_count = len(lead_rows)

    print(f"Expected Lead Count: {EXPECTED_LEAD_COUNT}")
    print(f"Actual Lead Count: {actual_lead_count}")

    distribution_passed = (
        actual_lead_count == EXPECTED_LEAD_COUNT
    )

    if distribution_passed:

        print("STEP 6 PASSED: Exactly 10 leads displayed.")

    else:

        print("STEP 6 FAILED: Incorrect lead count.")

    screenshot("Step_06_Lead_Count.png")

    # ==========================================
    # STEP 7: CHECK ASSIGNED LEAD DETAILS
    # ==========================================

    current_step = "Step 7: Check Assigned Lead Details"

    print()
    print("===================================")
    print("ASSIGNED LEAD RECORDS")
    print("===================================")

    # Retrieve the table column headers

    header_elements = driver.find_elements(
        By.CSS_SELECTOR,
        'table thead th, [role="columnheader"]'
    )

    headers = [
        header.text.strip()
        for header in header_elements
        if header.is_displayed()
    ]

    all_records = []

    details_passed = actual_lead_count > 0

    for index, row in enumerate(lead_rows, start=1):

        cells = row.find_elements(
            By.CSS_SELECTOR,
            'td, [role="cell"], [role="gridcell"]'
        )

        values = [
            cell.text.strip()
            for cell in cells
        ]

        all_records.append(values)

        print()
        print(f"LEAD NUMBER {index}")
        print("-----------------------------------")

        for column_index, value in enumerate(values):

            if column_index < len(headers):

                column_name = headers[column_index]

                if not column_name:

                    column_name = (
                        f"Column {column_index + 1}"
                    )

            else:

                column_name = (
                    f"Column {column_index + 1}"
                )

            print(f"{column_name}: {value}")

        # Check that the record contains visible data

        if not any(values):

            details_passed = False

            print("RECORD CHECK: FAILED")

        else:

            print("RECORD DISPLAY CHECK: PASSED")

    # ==========================================
    # EXPORT ASSIGNED LEAD RECORDS TO CSV
    # ==========================================

    csv_path = os.path.join(
        SCREENSHOT_FOLDER,
        "Assigned_Lead_Records.csv"
    )

    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        writer = csv.writer(csv_file)

        if headers:

            writer.writerow(headers)

        writer.writerows(all_records)

    print()
    print(f"Lead records exported to: {csv_path}")

    if details_passed:

        print("STEP 7 PASSED: Lead records contain visible data.")

    else:

        print("STEP 7 FAILED: Lead records are missing.")

    screenshot("Step_07_Assigned_Lead_Details.png")

    # ==========================================
    # FINAL TEST RESULT
    # ==========================================

    print()
    print("===================================")
    print("TC-TEL-01: FINAL TEST RESULT")
    print("===================================")

    print("Test Case: Login x Distribution")
    print(f"Account: {EMAIL}")
    print("Login: PASSED")
    print("Leads Navigation: PASSED")

    print(f"Expected Leads: {EXPECTED_LEAD_COUNT}")
    print(f"Actual Leads: {actual_lead_count}")

    if distribution_passed:

        print("Lead Distribution: PASSED")

    else:

        print("Lead Distribution: FAILED")

    if details_passed:

        print("Lead Record Display: PASSED")

    else:

        print("Lead Record Display: FAILED")

    print("-----------------------------------")

    if distribution_passed and details_passed:

        print("FINAL RESULT: PASSED")
        print("10 lead records are displayed.")

    else:

        print("FINAL RESULT: FAILED")
        print("Lead count or record display did not match.")

    print("===================================")

except TimeoutException:

    print()
    print("===================================")
    print("TC-TEL-01: TEST FAILED")
    print("===================================")
    print(f"Failed at: {current_step}")
    print("Required element did not appear in time.")
    print("Current URL:", driver.current_url)
    print("===================================")

    screenshot("Test_Failed_Timeout.png")

    raise

except AssertionError as error:

    print()
    print("===================================")
    print("TC-TEL-01: TEST FAILED")
    print("===================================")
    print(f"Failed at: {current_step}")
    print(f"Verification Error: {error}")
    print("===================================")

    screenshot("Test_Failed_Assertion.png")

    raise

except Exception as error:

    print()
    print("===================================")
    print("TC-TEL-01: AUTOMATION ERROR")
    print("===================================")
    print(f"Failed at: {current_step}")
    print(f"Error: {error}")
    print("Current URL:", driver.current_url)
    print("===================================")

    screenshot("Test_Failed_Unexpected.png")

    raise

finally:

    input("\nPress Enter to close the browser...")

    driver.quit()
