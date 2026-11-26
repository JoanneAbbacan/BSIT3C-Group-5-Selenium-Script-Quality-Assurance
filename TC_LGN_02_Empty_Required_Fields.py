
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

# ==========================================
# TC-LGN-02: DEFECT RETESTING
# STEP 15 AND STEP 24 ONLY
# ==========================================

# LEAD GENERATION SPECIALIST ACCOUNT

EMAIL = "jbabbacan@gmail.com"
PASSWORD = "ABCabc1234!"

URL = "https://sortrleaddistribution-client.onrender.com/"

# LEAD TEST DATA

LEAD_NAME = "Only Drans"
LEAD_TYPE = "Hotel"
PHONE = "0967 570 067"
STREET = "Saint Dominic Street"
CITY = "San Fernando"
POSTCODE = "2000"
LEAD_EMAIL = "onlydrans@example.com"

# ==========================================
# CONFIGURE CHROME WINDOW
# ==========================================

options = webdriver.ChromeOptions()

options.add_argument("--start-maximized")
options.add_argument("--force-device-scale-factor=0.8")

driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 120)

results = []

# ==========================================
# SCREENSHOT EVIDENCE FOLDER
# ==========================================

SCREENSHOT_FOLDER = "TC-LGN-02_Retesting_Evidence"

os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

# ==========================================
# ELEMENT LOCATORS
# ==========================================

ADD_LEAD = (
    By.XPATH,
    "//*[normalize-space()='Add New Lead']"
)

LEADS_LIST = (
    By.XPATH,
    "//li[contains(@class,'ps-menuitem-root')]"
    "[.//*[normalize-space()='Leads']]"
)

SUBMIT = (
    By.CSS_SELECTOR,
    'button[type="submit"]'
)

SUCCESS = (
    By.XPATH,
    "//*[normalize-space()='New lead added!']"
)

TYPE_DROPDOWN = (
    By.CSS_SELECTOR,
    '[role="combobox"]'
)

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


def enter_field(field_name, value):

    field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, field_name)
        )
    )

    field.click()
    field.send_keys(Keys.CONTROL, "a")
    field.send_keys(Keys.BACKSPACE)
    field.send_keys(value)

    actual = field.get_attribute("value")

    if field_name == "phonenumber":

        assert "".join(
            c for c in actual if c.isdigit()
        ) == "".join(
            c for c in value if c.isdigit()
        ), "Phone number input mismatch."

    else:

        assert actual == value, (
            f"{field_name} input mismatch."
        )

    print(f"{field_name}: {actual}")


def clear_field(field_name):

    field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, field_name)
        )
    )

    field.click()
    field.send_keys(Keys.CONTROL, "a")
    field.send_keys(Keys.BACKSPACE)

    assert field.get_attribute("value") == "", (
        f"{field_name} was not cleared."
    )

    print(f"{field_name} cleared successfully.")


def select_hotel():

    dropdown = wait.until(
        EC.element_to_be_clickable(
            TYPE_DROPDOWN
        )
    )

    dropdown.click()

    option_locator = (
        By.CSS_SELECTOR,
        'li[role="option"][data-value="Hotel"]'
    )

    hotel_option = wait.until(
        EC.visibility_of_element_located(
            option_locator
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        hotel_option
    )

    wait.until(
        EC.element_to_be_clickable(
            option_locator
        )
    ).click()

    wait.until(
        lambda d: any(
            element.text.strip() == LEAD_TYPE
            for element in d.find_elements(
                *TYPE_DROPDOWN
            )
        )
    )

    print("Type: Hotel")


def open_add_lead():

    wait.until(
        EC.invisibility_of_element_located(
            SUCCESS
        )
    )

    wait.until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".MuiBackdrop-root")
        )
    )

    wait.until(
        EC.element_to_be_clickable(
            ADD_LEAD
        )
    ).click()

    wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "name")
        )
    )

    print("Add New Lead form opened.")


def complete_lead_form():

    enter_field("name", LEAD_NAME)

    select_hotel()

    enter_field("phonenumber", PHONE)

    enter_field("streetaddress", STREET)

    enter_field("city", CITY)

    enter_field("postcode", POSTCODE)

    enter_field("emailaddress", LEAD_EMAIL)

    print("All lead information entered.")


def verify_other_fields(empty_field):

    expected_fields = {
        "name": LEAD_NAME,
        "phonenumber": PHONE,
        "streetaddress": STREET,
        "city": CITY,
        "postcode": POSTCODE,
        "emailaddress": LEAD_EMAIL
    }

    for field_name, expected in expected_fields.items():

        field = driver.find_element(
            By.NAME,
            field_name
        )

        actual = field.get_attribute("value")

        if field_name == empty_field:

            assert actual == "", (
                f"{field_name} must be empty."
            )

        elif field_name == "phonenumber":

            assert "".join(
                c for c in actual if c.isdigit()
            ) == "".join(
                c for c in expected if c.isdigit()
            )

        else:

            assert actual == expected, (
                f"{field_name} does not match test data."
            )

    assert driver.find_element(
        *TYPE_DROPDOWN
    ).text.strip() == LEAD_TYPE

    print("Verified: Only the target field is empty.")


def get_validation_message(field_name):

    fields = driver.find_elements(
        By.NAME,
        field_name
    )

    if not fields:
        return ""

    field = fields[0]

    # Check native browser validation

    native_message = driver.execute_script(
        "return arguments[0].validationMessage || '';",
        field
    )

    if native_message:
        return native_message

    # Check Material UI validation messages

    containers = field.find_elements(
        By.XPATH,
        "./ancestor::*[contains(@class,"
        "'MuiFormControl-root')][1]"
    )

    for container in containers:

        errors = container.find_elements(
            By.CSS_SELECTOR,
            ".MuiFormHelperText-root.Mui-error"
        )

        for error in errors:

            if error.is_displayed() and error.text.strip():

                return error.text.strip()

    # Check accessibility-linked validation messages

    described_by = field.get_attribute(
        "aria-describedby"
    ) or ""

    if field.get_attribute("aria-invalid") == "true":

        for element_id in described_by.split():

            for helper in driver.find_elements(
                By.ID,
                element_id
            ):

                if helper.is_displayed() and helper.text.strip():

                    return helper.text.strip()

    return ""


def check_submission(field_name):

    # Check whether the system incorrectly created a lead

    for message in driver.find_elements(*SUCCESS):

        if message.is_displayed():

            return (
                "FAILED",
                "DEFECT STILL EXISTS: Incomplete lead was created."
            )

    # Check whether the expected validation appeared

    message = get_validation_message(field_name)

    if message:

        return (
            "PASSED",
            f"Validation message: {message}"
        )

    return False


def retest(step, field_name, field_label):

    print()
    print("===================================")
    print(f"STEP {step}: EMPTY {field_label.upper()}")
    print("===================================")

    try:

        open_add_lead()

        complete_lead_form()

        # Clear only the field being retested

        clear_field(field_name)

        verify_other_fields(field_name)

        screenshot(
            f"Step_{step}_Before_Submission.png"
        )

        submit_button = wait.until(
            EC.visibility_of_element_located(
                SUBMIT
            )
        )

        # Check whether submission is disabled

        if not submit_button.is_enabled():

            message = get_validation_message(
                field_name
            )

            if message:

                status = "PASSED"

                reason = (
                    "Submission disabled. "
                    f"Validation: {message}"
                )

            else:

                status = "INCONCLUSIVE"

                reason = (
                    "Submission disabled, but no "
                    "validation message was detected."
                )

        else:

            submit_button.click()

            print("SUBMIT button clicked.")
            print("Checking submission result...")

            try:

                status, reason = WebDriverWait(
                    driver,
                    20
                ).until(
                    lambda d: check_submission(
                        field_name
                    )
                )

            except TimeoutException:

                status = "INCONCLUSIVE"

                reason = (
                    "No success or field validation "
                    "message was detected."
                )

        print("-----------------------------------")
        print(f"STEP {step}: {status}")
        print(reason)
        print("-----------------------------------")

        screenshot(
            f"Step_{step}_{status}.png"
        )

        results.append(
            (step, field_label, status, reason)
        )

    except Exception as error:

        results.append(
            (
                step,
                field_label,
                "ERROR",
                str(error)
            )
        )

        print(f"STEP {step}: AUTOMATION ERROR")
        print(f"Error: {error}")

        screenshot(
            f"Step_{step}_Automation_Error.png"
        )


def open_leads_list():

    wait.until(
        EC.invisibility_of_element_located(
            SUCCESS
        )
    )

    wait.until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".MuiBackdrop-root")
        )
    )

    wait.until(
        EC.element_to_be_clickable(
            LEADS_LIST
        )
    ).click()

    wait.until(
        EC.invisibility_of_element_located(
            (By.NAME, "streetaddress")
        )
    )

    print("Leads list opened.")


try:

    print("===================================")
    print("TC-LGN-02: DEFECT RETESTING")
    print("STEP 15 AND STEP 24")
    print("===================================")

    # ==========================================
    # PRECONDITION: LOGIN TO THE SYSTEM
    # ==========================================

    driver.get(URL)

    print("Website opened.")

    email_field = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input[type="email"]')
        )
    )

    email_field.send_keys(EMAIL)

    print("Login email entered.")

    password_field = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input[type="password"]')
        )
    )

    password_field.send_keys(PASSWORD)

    print("Login password entered.")

    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Log In']")
        )
    )

    login_button.click()

    wait.until(
        EC.element_to_be_clickable(
            ADD_LEAD
        )
    )

    print("Lead Generation Specialist login successful.")

    # ==========================================
    # STEP 15: SUBMIT WITH EMPTY PHONE NUMBER
    # ==========================================

    retest(
        step=15,
        field_name="phonenumber",
        field_label="Phone Number"
    )

    # Leave the previous form before the next test

    open_leads_list()

    # ==========================================
    # STEP 24: SUBMIT WITH EMPTY POSTCODE
    # ==========================================

    retest(
        step=24,
        field_name="postcode",
        field_label="Postcode"
    )

    # ==========================================
    # OPEN LEADS LIST AFTER RETESTING
    # ==========================================

    open_leads_list()

    screenshot("Final_Leads_List.png")

except Exception as error:

    print()
    print("===================================")
    print("AUTOMATION ERROR")
    print("===================================")
    print(f"Error: {error}")
    print("Current URL:", driver.current_url)

    screenshot("Unexpected_Error.png")

finally:

    # ==========================================
    # FINAL RETESTING SUMMARY
    # ==========================================

    print()
    print("===================================")
    print("TC-LGN-02: RETESTING SUMMARY")
    print("===================================")

    for step, field, status, reason in results:

        print(f"Step {step}: {field}")
        print(f"Result: {status}")
        print(f"Details: {reason}")
        print("-----------------------------------")

    passed = sum(
        result[2] == "PASSED"
        for result in results
    )

    failed = sum(
        result[2] == "FAILED"
        for result in results
    )

    inconclusive = sum(
        result[2] == "INCONCLUSIVE"
        for result in results
    )

    errors = sum(
        result[2] == "ERROR"
        for result in results
    )

    print("Total Retesting Scenarios: 2")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Inconclusive: {inconclusive}")
    print(f"Automation Errors: {errors}")
    print(f"Not Executed: {2 - len(results)}")

    print("-----------------------------------")

    if failed > 0:

        print("FINAL RESULT: FAILED")
        print("One or more reported defects still exist.")

    elif passed == 2:

        print("FINAL RESULT: PASSED")
        print("Both validation retests passed.")

    else:

        print("FINAL RESULT: NOT FULLY VERIFIED")

    print("===================================")

    input("\nPress Enter to close the browser...")

    driver.quit()
