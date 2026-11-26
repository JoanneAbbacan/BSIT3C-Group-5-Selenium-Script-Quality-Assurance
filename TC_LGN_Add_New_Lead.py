
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException

# ==========================================
# TC-LGN-01: CREATE NEW LEAD
# ==========================================

# LOGIN CREDENTIALS
EMAIL = "jbabbacan@gmail.com "
PASSWORD = "ABCabc1234!"

# WEBSITE URL
URL = "https://sortrleaddistribution-client.onrender.com/"

# LEAD TEST DATA
LEAD_NAME = "Dran Hub"
LEAD_TYPE = "Manufacturing"
PHONE = "61 491 570 159"
STREET = "Saint Rita Street"
CITY = "San Fernando"
POSTCODE = "2000"
LEAD_EMAIL = "dranhub@example.com"

# ==========================================
# CONFIGURE CHROME
# ==========================================

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 120)

current_step = "Login"

try:

    print("===================================")
    print("TC-LGN-01: CREATE NEW LEAD")
    print("===================================")

    # ==========================================
    # PRECONDITION: OPEN WEBSITE
    # ==========================================

    driver.get(URL)

    print("Website opened.")

    # ==========================================
    # ENTER LOGIN EMAIL
    # ==========================================

    email_field = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input[type="email"]')
        )
    )

    email_field.clear()
    email_field.send_keys(EMAIL)

    print("Login email entered.")

    # ==========================================
    # ENTER LOGIN PASSWORD
    # ==========================================

    password_field = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input[type="password"]')
        )
    )

    password_field.clear()
    password_field.send_keys(PASSWORD)

    print("Login password entered.")

    # ==========================================
    # CLICK LOG IN
    # ==========================================

    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Log In']")
        )
    )

    login_button.click()

    print("Log In button clicked.")
    print("Waiting for Add New Lead sidebar...")

    # ==========================================
    # STEP 1: CLICK ADD NEW LEAD
    # ==========================================

    current_step = "Step 1: Click Add New Lead"

    add_lead_link = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[normalize-space()='Add New Lead']")
        )
    )

    print("Login successful.")

    add_lead_link.click()

    # Verify that the Add New Lead form opened

    wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "name")
        )
    )

    print("-----------------------------------")
    print("STEP 1 PASSED: Add New Lead page opened.")

    # ==========================================
    # STEP 2: ENTER NAME
    # ==========================================

    current_step = "Step 2: Enter Name"

    name_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "name")
        )
    )

    name_field.clear()
    name_field.send_keys(LEAD_NAME)

    print("STEP 2 PASSED: Name entered.")
    print(f"Name: {LEAD_NAME}")

    # ==========================================
    # STEP 3: SELECT LEAD TYPE
    # ==========================================

    current_step = "Step 3: Select Manufacturing"

    print(f"Selecting Lead Type: {LEAD_TYPE}...")

    # Material UI dropdown

    type_dropdown = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[role="combobox"]')
        )
    )

    type_dropdown.click()

    print("Dropdown opened.")

    # Locate Manufacturing using data-value

    option_locator = (
        By.CSS_SELECTOR,
        f'li[role="option"][data-value="{LEAD_TYPE}"]'
    )

    type_option = wait.until(
        EC.visibility_of_element_located(
            option_locator
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        type_option
    )

    try:

        wait.until(
            EC.element_to_be_clickable(
                option_locator
            )
        ).click()

    except ElementClickInterceptedException:

        print("Option click intercepted.")
        print("Retrying Manufacturing selection...")

        type_option = wait.until(
            EC.element_to_be_clickable(
                option_locator
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            type_option
        )

    # Verify Manufacturing is selected

    wait.until(
        lambda d: any(
            element.text.strip() == LEAD_TYPE
            or element.get_attribute("value") == LEAD_TYPE
            for element in d.find_elements(
                By.CSS_SELECTOR,
                '[role="combobox"]'
            )
        )
    )

    print("STEP 3 PASSED: Manufacturing selected.")

    # ==========================================
    # STEP 4: ENTER PHONE NUMBER
    # ==========================================

    current_step = "Step 4: Enter Phone Number"

    phone_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "phonenumber")
        )
    )

    phone_field.clear()
    phone_field.send_keys(PHONE)

    print("STEP 4 PASSED: Phone Number entered.")
    print(f"Phone Number: {PHONE}")

    # ==========================================
    # STEP 5: ENTER STREET ADDRESS
    # ==========================================

    current_step = "Step 5: Enter Street Address"

    street_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "streetaddress")
        )
    )

    street_field.clear()
    street_field.send_keys(STREET)

    print("STEP 5 PASSED: Street Address entered.")
    print(f"Street Address: {STREET}")

    # ==========================================
    # STEP 6: ENTER CITY
    # ==========================================

    current_step = "Step 6: Enter City"

    city_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "city")
        )
    )

    city_field.clear()
    city_field.send_keys(CITY)

    print("STEP 6 PASSED: City entered.")
    print(f"City: {CITY}")

    # ==========================================
    # STEP 7: ENTER POSTCODE
    # ==========================================

    current_step = "Step 7: Enter Postcode"

    postcode_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "postcode")
        )
    )

    postcode_field.clear()
    postcode_field.send_keys(POSTCODE)

    print("STEP 7 PASSED: Postcode entered.")
    print(f"Postcode: {POSTCODE}")

    # ==========================================
    # STEP 8: ENTER EMAIL ADDRESS
    # ==========================================

    current_step = "Step 8: Enter Email Address"

    lead_email_field = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "emailaddress")
        )
    )

    lead_email_field.clear()
    lead_email_field.send_keys(LEAD_EMAIL)

    print("STEP 8 PASSED: Email Address entered.")
    print(f"Email Address: {LEAD_EMAIL}")

    # ==========================================
    # STEP 9: REVIEW ALL ENTERED INFORMATION
    # ==========================================

    current_step = "Step 9: Review Lead Information"

    print()
    print("===================================")
    print("REVIEW OF LEAD INFORMATION")
    print("===================================")

    # Verify Name

    actual_name = driver.find_element(
        By.NAME, "name"
    ).get_attribute("value")

    assert actual_name == LEAD_NAME, "Name does not match."

    print(f"Name: {actual_name} - VERIFIED")

    # Verify Type

    actual_type = driver.find_element(
        By.CSS_SELECTOR, '[role="combobox"]'
    ).text.strip()

    assert actual_type == LEAD_TYPE, "Type does not match."

    print(f"Type: {actual_type} - VERIFIED")

    # Verify Phone Number

    actual_phone = driver.find_element(
        By.NAME, "phonenumber"
    ).get_attribute("value")

    assert actual_phone.replace(" ", "") == PHONE.replace(" ", ""), \
        "Phone Number does not match."

    print(f"Phone Number: {actual_phone} - VERIFIED")

    # Verify Street Address

    actual_street = driver.find_element(
        By.NAME, "streetaddress"
    ).get_attribute("value")

    assert actual_street == STREET, \
        "Street Address does not match."

    print(f"Street Address: {actual_street} - VERIFIED")

    # Verify City

    actual_city = driver.find_element(
        By.NAME, "city"
    ).get_attribute("value")

    assert actual_city == CITY, "City does not match."

    print(f"City: {actual_city} - VERIFIED")

    # Verify Postcode

    actual_postcode = driver.find_element(
        By.NAME, "postcode"
    ).get_attribute("value")

    assert actual_postcode == POSTCODE, \
        "Postcode does not match."

    print(f"Postcode: {actual_postcode} - VERIFIED")

    # Verify Email Address

    actual_email = driver.find_element(
        By.NAME, "emailaddress"
    ).get_attribute("value")

    assert actual_email == LEAD_EMAIL, \
        "Email Address does not match."

    print(f"Email Address: {actual_email} - VERIFIED")

    print("-----------------------------------")
    print("STEP 9 PASSED: All information verified.")
    print("-----------------------------------")

    # Screenshot before submission

    driver.save_screenshot(
        "TC-LGN-01_Completed_Form.png"
    )

    # ==========================================
    # STEP 10: CLICK SUBMIT BUTTON
    # ==========================================

    current_step = "Step 10: Submit New Lead"

    submit_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[type="submit"]')
        )
    )

    submit_button.click()

    print("SUBMIT button clicked.")
    print("Waiting for success message...")

    # Verify successful lead creation

    success_locator = (
        By.XPATH,
        "//*[normalize-space()='New lead added!']"
    )

    success_message = wait.until(
        EC.visibility_of_element_located(
            success_locator
        )
    )

    print("STEP 10 PASSED: New lead successfully added.")
    print(f"Success Message: {success_message.text}")

    driver.save_screenshot(
        "TC-LGN-01_Success_Message.png"
    )

    # Wait for success popup to close

    print("Waiting for success popup to close...")

    wait.until(
        EC.invisibility_of_element_located(
            success_locator
        )
    )

    wait.until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".MuiBackdrop-root")
        )
    )

    print("Success popup closed.")

    # ==========================================
    # STEP 11: NAVIGATE TO LEADS LIST
    # ==========================================

    current_step = "Step 11: Navigate to Leads List"

    print("Opening Leads page...")

    leads_link = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//li[contains(@class,'ps-menuitem-root')]"
                "[.//*[normalize-space()='Leads']]"
            )
        )
    )

    leads_link.click()

    print("STEP 11: Leads sidebar clicked.")

    # ==========================================
    # STEP 12: LOCATE NEWLY CREATED LEAD
    # ==========================================

    current_step = "Step 12: Verify Dran Hub"

    print(f"Searching for newly created lead: {LEAD_NAME}")

    created_lead = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[normalize-space()='{LEAD_NAME}']"
            )
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        created_lead
    )

    assert created_lead.is_displayed(), \
        "The newly created lead is not displayed."

    print("STEP 11 PASSED: Leads page displayed.")
    print("STEP 12 PASSED: Dran Hub found in Leads list.")

    # Screenshot of newly created lead

    driver.save_screenshot(
        "TC-LGN-01_Lead_Verification.png"
    )

    # ==========================================
    # FINAL TEST RESULT
    # ==========================================

    print()
    print("===================================")
    print("TEST PASSED")
    print("===================================")
    print("Test Case ID: TC-LGN-01")
    print("Test Case: Create New Lead")
    print(f"Lead Name: {LEAD_NAME}")
    print(f"Lead Type: {LEAD_TYPE}")
    print("All 12 test steps completed.")
    print("Success message: New lead added!")
    print("The lead is visible on the Leads page.")
    print("Screenshot evidence captured.")
    print("===================================")

except TimeoutException:

    print()
    print("===================================")
    print("TEST FAILED")
    print("===================================")
    print(f"Failed at: {current_step}")
    print("A required element did not appear.")
    print("Waiting time exceeded 120 seconds.")
    print("Current URL:", driver.current_url)
    print("===================================")

    driver.save_screenshot(
        "TC-LGN-01_Failed.png"
    )

    raise

except AssertionError as error:

    print()
    print("===================================")
    print("TEST FAILED")
    print("===================================")
    print(f"Failed at: {current_step}")
    print(f"Verification Error: {error}")
    print("===================================")

    driver.save_screenshot(
        "TC-LGN-01_Failed.png"
    )

    raise

except Exception as error:

    print()
    print("===================================")
    print("TEST FAILED")
    print("===================================")
    print(f"Failed at: {current_step}")
    print(f"Error: {error}")
    print("Current URL:", driver.current_url)
    print("===================================")

    driver.save_screenshot(
        "TC-LGN-01_Failed.png"
    )

    raise

finally:

    input("\nPress Enter to close the browser...")
    driver.quit()
