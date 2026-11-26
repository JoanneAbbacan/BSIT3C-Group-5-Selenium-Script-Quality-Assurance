
import os
import csv
import time

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException
)

# ==========================================
# TC-TLD-03 - ADD USER
# ==========================================

URL = "https://sortrleaddistribution-client.onrender.com/"

# TEAM LEADER ACCOUNT

TEAM_LEADER_EMAIL = "bsit3c@gmail.com"
TEAM_LEADER_PASSWORD = "ABCabc123!"

# NEW USER TEST DATA

NEW_FULL_NAME = "Joanne Abaccan"
NEW_EMAIL = "jbabaccan@gmail.com"
NEW_PASSWORD = "Wh4tTheH3ll4n0gUst0n3t0?"
NEW_ROLE = "Telemarketer"

# ==========================================
# TIMEOUT SETTINGS
# ==========================================

TIMEOUT = 120

# ==========================================
# EVIDENCE FOLDER
# ==========================================

EVIDENCE_FOLDER = "TC-TLD-03_Evidence"

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

RUN_FOLDER = os.path.join(
    EVIDENCE_FOLDER,
    RUN_ID
)

os.makedirs(RUN_FOLDER, exist_ok=True)

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

success_message = "N/A"

creation_confirmed = False
user_verified = False
login_verified = False

# ==========================================
# ELEMENT LOCATORS
# ==========================================

LOGIN_EMAIL = (
    By.CSS_SELECTOR,
    'input[type="email"]'
)

LOGIN_PASSWORD = (
    By.CSS_SELECTOR,
    'input[type="password"]'
)

LOGIN_BUTTON = (
    By.XPATH,
    "//button[normalize-space()='Log In' "
    "or normalize-space()='Log in' "
    "or normalize-space()='LOGIN']"
)

ADD_USER_LINK = (
    By.XPATH,
    "//li[contains(@class,'ps-menuitem-root')]"
    "[.//*[normalize-space()='Add New User']]"
)

USERS_LINK = (
    By.XPATH,
    "//li[contains(@class,'ps-menuitem-root')]"
    "[.//*[normalize-space()='Users']]"
)

SIGN_OUT_LINK = (
    By.XPATH,
    "//li[contains(@class,'ps-menuitem-root')]"
    "[.//*[normalize-space()='Sign Out']]"
)

ADD_USER_BUTTON = (
    By.XPATH,
    "//button[normalize-space()='ADD NEW USER' "
    "or normalize-space()='Add New User']"
)

SUCCESS_POPUP = (
    By.XPATH,
    "//*[normalize-space(.)="
    "'New User Added Successfully!']"
)

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
        poll_frequency=0.2,
        ignored_exceptions=(
            StaleElementReferenceException,
            NoSuchElementException
        )
    )


# ==========================================
# SCREENSHOT FUNCTION
# ==========================================

def screenshot(filename):

    path = os.path.join(
        RUN_FOLDER,
        filename
    )

    try:

        if driver.save_screenshot(path):

            print(f"Screenshot saved: {path}")

    except Exception as error:

        print(f"Screenshot error: {error}")


# ==========================================
# FIND VISIBLE ELEMENT
# ==========================================

def find_visible(locators):

    def locate(browser):

        check_timer()

        for by, value in locators:

            elements = browser.find_elements(
                by,
                value
            )

            for element in elements:

                if (
                    element.is_displayed()
                    and element.is_enabled()
                ):

                    return element

        return False

    return step_wait().until(locate)


# ==========================================
# CHECK ELEMENT VISIBILITY
# ==========================================

def is_visible(locator):

    elements = driver.find_elements(
        *locator
    )

    for element in elements:

        try:

            if element.is_displayed():

                return True

        except StaleElementReferenceException:

            continue

    return False


# ==========================================
# SAFE CLICK FUNCTION
# ==========================================

def safe_click(locator):

    def click_element(browser):

        check_timer()

        try:

            elements = browser.find_elements(
                *locator
            )

            for element in elements:

                if (
                    element.is_displayed()
                    and element.is_enabled()
                ):

                    element.click()

                    return True

        except (
            ElementClickInterceptedException,
            StaleElementReferenceException,
            NoSuchElementException
        ):

            return False

        return False

    step_wait().until(click_element)


# ==========================================
# ENTER AND VERIFY FIELD VALUE
# ==========================================

def enter_value(field, value):

    field.click()

    field.send_keys(Keys.CONTROL, "a")
    field.send_keys(Keys.BACKSPACE)

    field.send_keys(value)

    actual_value = field.get_attribute("value")

    if actual_value != value:

        raise AssertionError(
            "The field did not accept "
            "the expected test input."
        )


# ==========================================
# VERIFY PASSWORD MASKING
# ==========================================

def verify_password_masked(field):

    if field.get_attribute("type") != "password":

        raise AssertionError(
            "Password is not masked."
        )

    print("Password masking verified.")


# ==========================================
# GET VISIBLE NOTIFICATIONS
# ==========================================

def get_visible_messages():

    messages = []

    selectors = (
        "[role='alert'], "
        "[role='status'], "
        "[role='dialog'], "
        ".MuiSnackbar-root, "
        ".MuiAlert-root, "
        ".Toastify__toast, "
        ".swal2-popup"
    )

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        selectors
    )

    for element in elements:

        try:

            if element.is_displayed():

                message = element.text.strip()

                if message and message not in messages:

                    messages.append(message)

        except StaleElementReferenceException:

            continue

    return messages


# ==========================================
# DETECT ERROR NOTIFICATIONS
# ==========================================

def get_error_message(previous_messages):

    error_patterns = [

        "already exists",
        "already registered",
        "already in use",
        "already taken",
        "duplicate email",
        "failed to add",
        "failed to create",
        "invalid credentials",
        "incorrect password",
        "invalid email",
        "login failed",
        "user not found",
        "unable to create",
        "something went wrong",
        "password must"

    ]

    for message in get_visible_messages():

        if message in previous_messages:

            continue

        lower_message = message.lower()

        if any(
            pattern in lower_message
            for pattern in error_patterns
        ):

            return message

    return None


# ==========================================
# PRECONDITION - TEAM LEADER LOGIN
# ==========================================

def login_team_leader():

    print("\nOpening application...")

    driver.get(URL)

    print("Application opened successfully.")

    print("\nLogging in as Team Leader...")

    email_field = step_wait().until(
        EC.visibility_of_element_located(
            LOGIN_EMAIL
        )
    )

    enter_value(
        email_field,
        TEAM_LEADER_EMAIL
    )

    print("Team Leader email entered.")

    password_field = step_wait().until(
        EC.visibility_of_element_located(
            LOGIN_PASSWORD
        )
    )

    enter_value(
        password_field,
        TEAM_LEADER_PASSWORD
    )

    print("Team Leader password entered.")

    safe_click(LOGIN_BUTTON)

    print("Login button clicked.")

    step_wait().until(
        EC.element_to_be_clickable(
            ADD_USER_LINK
        )
    )

    print("------------------------------------------")
    print("PRECONDITION: PASSED")
    print("Team Leader login successful.")
    print("------------------------------------------")

    screenshot(
        "Precondition_Team_Leader_Login.png"
    )


# ==========================================
# FIND FULL NAME FIELD
# ==========================================

def find_full_name_field():

    return find_visible([

        (
            By.CSS_SELECTOR,
            'input[placeholder="Full Name"]'
        ),

        (
            By.CSS_SELECTOR,
            'input[name="fullname"]'
        ),

        (
            By.CSS_SELECTOR,
            'input[name="fullName"]'
        ),

        (
            By.CSS_SELECTOR,
            'input[name="name"]'
        ),

        (
            By.XPATH,
            "//label[contains(normalize-space(.),"
            "'Full Name')]/following::input[1]"
        )

    ])


# ==========================================
# FIND EMAIL FIELD
# ==========================================

def find_new_email_field():

    return find_visible([

        (
            By.CSS_SELECTOR,
            'input[type="email"]'
        ),

        (
            By.CSS_SELECTOR,
            'input[name="email"]'
        ),

        (
            By.XPATH,
            "//label[contains(normalize-space(.),"
            "'Email')]/following::input[1]"
        )

    ])


# ==========================================
# FIND PASSWORD FIELD
# ==========================================

def find_new_password_field():

    return find_visible([

        (
            By.CSS_SELECTOR,
            'input[type="password"]'
        ),

        (
            By.CSS_SELECTOR,
            'input[name="password"]'
        ),

        (
            By.XPATH,
            "//label[contains(normalize-space(.),"
            "'Password')]/following::input[1]"
        )

    ])


# ==========================================
# STEP 1 - CLICK ADD NEW USER
# ==========================================

def open_add_new_user():

    print("Clicking Add New User in sidebar...")

    safe_click(ADD_USER_LINK)

    step_wait().until(
        EC.visibility_of_element_located(
            ADD_USER_BUTTON
        )
    )

    find_full_name_field()
    find_new_email_field()
    find_new_password_field()

    print("New User form displayed successfully.")

    return "The New User form is displayed."


# ==========================================
# STEP 2 - ENTER FULL NAME
# ==========================================

def enter_full_name():

    print(f"Entering Full Name: {NEW_FULL_NAME}")

    field = find_full_name_field()

    enter_value(
        field,
        NEW_FULL_NAME
    )

    print("Full Name accepted.")

    return f"Full Name accepted: {NEW_FULL_NAME}"


# ==========================================
# STEP 3 - ENTER EMAIL
# ==========================================

def enter_new_email():

    print(f"Entering Email: {NEW_EMAIL}")

    field = find_new_email_field()

    enter_value(
        field,
        NEW_EMAIL
    )

    print("Email accepted.")

    return f"Email accepted: {NEW_EMAIL}"


# ==========================================
# STEP 4 - ENTER PASSWORD
# ==========================================

def enter_new_password():

    print("Entering new user password...")

    field = find_new_password_field()

    enter_value(
        field,
        NEW_PASSWORD
    )

    verify_password_masked(field)

    print("Password accepted and masked.")

    return "Password accepted and masked."


# ==========================================
# STEP 5 - SELECT TELEMARKETER ROLE
# ==========================================

def select_role():

    print(f"Selecting Role: {NEW_ROLE}")

    role_dropdown = find_visible([

        (
            By.CSS_SELECTOR,
            'select[name="role"]'
        ),

        (
            By.CSS_SELECTOR,
            '[role="combobox"][id*="role"]'
        ),

        (
            By.CSS_SELECTOR,
            '[role="combobox"][aria-label*="Role"]'
        ),

        (
            By.XPATH,
            "//label[contains(normalize-space(.),"
            "'Role')]/following::*"
            "[@role='combobox' or self::select][1]"
        ),

        (
            By.CSS_SELECTOR,
            '[role="combobox"]'
        )

    ])

    if role_dropdown.tag_name.lower() == "select":

        dropdown = Select(role_dropdown)

        dropdown.select_by_visible_text(
            NEW_ROLE
        )

        selected_role = (
            dropdown.first_selected_option.text
        )

    else:

        role_dropdown.click()

        role_option = step_wait().until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//*[@role='option']"
                    f"[normalize-space(.)='{NEW_ROLE}']"
                )
            )
        )

        role_option.click()

        selected_role = step_wait().until(
            lambda browser:
                role_dropdown.text.strip()
                if role_dropdown.text.strip().lower()
                == NEW_ROLE.lower()
                else False
        )

    if selected_role.strip().lower() != NEW_ROLE.lower():

        raise AssertionError(
            f"Incorrect role selected: {selected_role}"
        )

    print(f"Selected Role: {selected_role}")

    return f"Role selected: {selected_role}"


# ==========================================
# DETECT SUCCESS MESSAGE
# ==========================================

def detect_success_message(browser):

    check_timer()

    elements = browser.find_elements(
        *SUCCESS_POPUP
    )

    for element in elements:

        try:

            if element.is_displayed():

                message = element.text.strip()

                if message == "New User Added Successfully!":

                    return message

        except StaleElementReferenceException:

            continue

    return False


# ==========================================
# WAIT FOR SUCCESS POP-UP TO CLOSE
# ==========================================

def wait_for_success_popup_to_close():

    print("Waiting for success pop-up to close...")

    # First wait for automatic dismissal.

    try:

        WebDriverWait(
            driver,
            min(5, remaining_time()),
            poll_frequency=0.2
        ).until(
            lambda browser:
                not is_visible(SUCCESS_POPUP)
        )

        print("Success pop-up closed automatically.")

        return

    except TimeoutException:

        print("Success pop-up remains visible.")

    # Look for an available dismissal button.

    close_buttons = driver.find_elements(
        By.XPATH,
        "//*[@role='dialog' or @role='alertdialog']"
        "//button[normalize-space()='OK' "
        "or normalize-space()='Close' "
        "or normalize-space()='Done' "
        "or @aria-label='Close' "
        "or @aria-label='close']"
    )

    for button in close_buttons:

        try:

            if (
                button.is_displayed()
                and button.is_enabled()
            ):

                button.click()

                print("Pop-up dismissal button clicked.")

                break

        except (
            StaleElementReferenceException,
            ElementClickInterceptedException
        ):

            continue

    # Try Escape if the pop-up remains visible.

    if is_visible(SUCCESS_POPUP):

        print("Attempting dismissal using Escape...")

        driver.find_element(
            By.TAG_NAME,
            "body"
        ).send_keys(Keys.ESCAPE)

    # Try clicking outside the dialog.

    if is_visible(SUCCESS_POPUP):

        backdrops = driver.find_elements(
            By.CSS_SELECTOR,
            ".MuiBackdrop-root"
        )

        for backdrop in backdrops:

            try:

                if backdrop.is_displayed():

                    from selenium.webdriver.common.action_chains import ActionChains

                    ActionChains(driver).move_to_element_with_offset(
                        backdrop,
                        20 - backdrop.size["width"] / 2,
                        20 - backdrop.size["height"] / 2
                    ).click().perform()

                    print("Clicked outside the success dialog.")

                    break

            except Exception:

                continue

    # Confirm that the pop-up has disappeared.

    step_wait().until(
        lambda browser:
            not is_visible(SUCCESS_POPUP)
    )

    print("Success pop-up closed successfully.")


# ==========================================
# STEP 6 - CREATE NEW USER
# ==========================================

def submit_new_user():

    global success_message
    global creation_confirmed

    print("Verifying completed New User form...")

    name_field = find_full_name_field()
    email_field = find_new_email_field()
    password_field = find_new_password_field()

    if name_field.get_attribute("value") != NEW_FULL_NAME:

        raise AssertionError(
            "Full Name does not match."
        )

    if email_field.get_attribute("value") != NEW_EMAIL:

        raise AssertionError(
            "Email does not match."
        )

    if password_field.get_attribute("value") != NEW_PASSWORD:

        raise AssertionError(
            "Password does not match."
        )

    print(f"Full Name: {NEW_FULL_NAME}")
    print(f"Email: {NEW_EMAIL}")
    print("Password: ********")
    print(f"Role: {NEW_ROLE}")

    # Check native form validation before submission.

    add_button = step_wait().until(
        EC.element_to_be_clickable(
            ADD_USER_BUTTON
        )
    )

    form_errors = driver.execute_script(
        """
        const form = arguments[0].closest('form');

        if (!form) {
            return [];
        }

        return Array.from(form.elements)
            .filter(e => e.willValidate && !e.validity.valid)
            .map(e => ({
                field: e.name || e.id || 'Field',
                message: e.validationMessage
            }));
        """,
        add_button
    )

    if form_errors:

        raise AssertionError(
            f"Form validation failed: {form_errors}"
        )

    screenshot(
        "Step_06_Before_Submission.png"
    )

    previous_messages = set(
        get_visible_messages()
    )

    if is_visible(SUCCESS_POPUP):

        raise AssertionError(
            "A previous success message is still visible."
        )

    print("Clicking ADD NEW USER...")

    safe_click(ADD_USER_BUTTON)

    print("ADD NEW USER button clicked.")
    print("Waiting for success confirmation...")
    print("Expected: New User Added Successfully!")

    observation_start = time.monotonic()

    last_report = 0

    def check_submission(browser):

        nonlocal last_report

        check_timer()

        # Detect the exact success message.

        message = detect_success_message(browser)

        if message:

            return message

        # Detect error notifications.

        error_message = get_error_message(
            previous_messages
        )

        if error_message:

            raise AssertionError(
                f"User creation rejected: {error_message}"
            )

        elapsed = (
            time.monotonic() - observation_start
        )

        if elapsed - last_report >= 5:

            last_report = elapsed

            print(
                f"Waiting for confirmation: "
                f"{elapsed:.0f} seconds"
            )

        return False

    success_message = step_wait().until(
        check_submission
    )

    creation_confirmed = True

    print("------------------------------------------")
    print("NEW USER CREATED SUCCESSFULLY")
    print(f"System Message: {success_message}")
    print("------------------------------------------")

    screenshot(
        "Step_06_Success_Message.png"
    )

    # Creation is confirmed.
    # Popup dismissal will be handled in Step 7.

    return f"Success confirmation: {success_message}"


# ==========================================
# FIND NEW USER IN USERS LIST
# ==========================================

def find_new_user_row(browser):

    check_timer()

    rows = browser.find_elements(
        By.CSS_SELECTOR,
        ".MuiDataGrid-row, "
        "table tbody tr, "
        "[role='rowgroup'] [role='row']"
    )

    for row in rows:

        try:

            if not row.is_displayed():

                continue

            cells = row.find_elements(
                By.CSS_SELECTOR,
                "td, [role='gridcell']"
            )

            values = [

                cell.text.strip().lower()

                for cell in cells

            ]

            name_matches = (
                NEW_FULL_NAME.lower() in values
            )

            email_matches = (
                NEW_EMAIL.lower() in values
            )

            role_matches = (
                NEW_ROLE.lower() in values
            )

            if (
                name_matches
                and email_matches
                and role_matches
            ):

                return row

        except StaleElementReferenceException:

            continue

    return False


# ==========================================
# STEP 7 - OPEN USERS LIST
# ==========================================

def verify_users_list():

    global user_verified

    # Dismiss the success pop-up before navigation.

    wait_for_success_popup_to_close()

    print("Opening Users list...")

    # Use sidebar navigation.
    # Do not refresh the internal application URL.

    safe_click(USERS_LINK)

    step_wait().until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".MuiDataGrid-root, "
                "table, [role='grid']"
            )
        )
    )

    print("Users list opened successfully.")

    screenshot(
        "Step_07_Users_List.png"
    )

    # Check whether the account is already visible.

    target_row = find_new_user_row(driver)

    # Search for the new user if necessary.

    if not target_row:

        search_fields = driver.find_elements(
            By.CSS_SELECTOR,
            'input[placeholder="Search"], '
            'input[type="search"], '
            'input[placeholder="Search users"]'
        )

        for search_box in search_fields:

            if (
                search_box.is_displayed()
                and search_box.is_enabled()
            ):

                search_box.click()

                search_box.send_keys(
                    Keys.CONTROL,
                    "a"
                )

                search_box.send_keys(
                    Keys.BACKSPACE
                )

                search_box.send_keys(
                    NEW_FULL_NAME
                )

                print(f"Searching for: {NEW_FULL_NAME}")

                break

        print("Verifying new user information...")

        target_row = step_wait().until(
            find_new_user_row
        )

    driver.execute_script(
        "arguments[0].scrollIntoView("
        "{block:'center', inline:'center'});",
        target_row
    )

    user_verified = True

    print("------------------------------------------")
    print("NEW USER FOUND IN USERS LIST")
    print(f"Full Name: {NEW_FULL_NAME}")
    print(f"Email: {NEW_EMAIL}")
    print(f"Role: {NEW_ROLE}")
    print("Account existence verified.")
    print("------------------------------------------")

    screenshot(
        "Step_07_New_User_Found.png"
    )

    return (
        f"{NEW_FULL_NAME} appears in the Users "
        f"list with the {NEW_ROLE} role."
    )


# ==========================================
# STEP 8 - SIGN OUT
# ==========================================

def sign_out():

    print("Signing out Team Leader account...")

    safe_click(SIGN_OUT_LINK)

    confirmation_clicked = False

    def check_sign_out(browser):

        nonlocal confirmation_clicked

        check_timer()

        # Check if the login page is displayed.

        if (
            is_visible(LOGIN_EMAIL)
            and is_visible(LOGIN_PASSWORD)
            and is_visible(LOGIN_BUTTON)
        ):

            return True

        # Handle a possible sign-out confirmation.

        if not confirmation_clicked:

            buttons = browser.find_elements(
                By.XPATH,
                "//*[@role='dialog' or @role='alertdialog']"
                "//button[normalize-space()='Yes' "
                "or normalize-space()='YES' "
                "or normalize-space()='Confirm' "
                "or normalize-space()='Sign Out' "
                "or normalize-space()='SIGN OUT']"
            )

            for button in buttons:

                if (
                    button.is_displayed()
                    and button.is_enabled()
                ):

                    button.click()

                    confirmation_clicked = True

                    print("Sign-out confirmation clicked.")

                    return False

        return False

    step_wait().until(
        check_sign_out
    )

    print("Team Leader signed out successfully.")
    print("Log-In page displayed.")

    screenshot(
        "Step_08_Login_Page.png"
    )

    return "User returned to the Log-In page."


# ==========================================
# STEP 9 - ENTER NEW USER EMAIL
# ==========================================

def enter_login_email():

    print("Entering new user email...")

    email_field = step_wait().until(
        EC.visibility_of_element_located(
            LOGIN_EMAIL
        )
    )

    enter_value(
        email_field,
        NEW_EMAIL
    )

    print(f"Email accepted: {NEW_EMAIL}")

    return f"Login email accepted: {NEW_EMAIL}"


# ==========================================
# STEP 10 - ENTER NEW USER PASSWORD
# ==========================================

def enter_login_password():

    print("Entering new user password...")

    password_field = step_wait().until(
        EC.visibility_of_element_located(
            LOGIN_PASSWORD
        )
    )

    enter_value(
        password_field,
        NEW_PASSWORD
    )

    verify_password_masked(
        password_field
    )

    print("Password accepted and masked.")

    return "Login password accepted and masked."


# ==========================================
# VERIFY TELEMARKETER DASHBOARD
# ==========================================

def verify_telemarketer_dashboard(browser):

    check_timer()

    dashboard_locator = (
        By.XPATH,
        "//*[normalize-space()='DASHBOARD' "
        "or normalize-space()='Dashboard']"
    )

    role_locator = (
        By.XPATH,
        "//*[normalize-space()='Telemarketer']"
    )

    leads_locator = (
        By.XPATH,
        "//li[contains(@class,'ps-menuitem-root')]"
        "[.//*[normalize-space()='Leads']]"
    )

    name_locator = (
        By.XPATH,
        f"//*[normalize-space(.)='{NEW_FULL_NAME}']"
    )

    dashboard_visible = is_visible(
        dashboard_locator
    )

    role_visible = is_visible(
        role_locator
    )

    leads_visible = is_visible(
        leads_locator
    )

    name_visible = is_visible(
        name_locator
    )

    login_visible = is_visible(
        LOGIN_BUTTON
    )

    add_user_visible = is_visible(
        ADD_USER_LINK
    )

    return (
        dashboard_visible
        and role_visible
        and leads_visible
        and name_visible
        and not login_visible
        and not add_user_visible
    )


# ==========================================
# STEP 11 - LOGIN AS NEW TELEMARKETER
# ==========================================

def login_new_user():

    global login_verified

    print("Logging in using newly created account...")

    screenshot(
        "Step_11_Before_Login.png"
    )

    previous_messages = set(
        get_visible_messages()
    )

    safe_click(LOGIN_BUTTON)

    print("Log In button clicked.")
    print("Waiting for Telemarketer dashboard...")

    observation_start = time.monotonic()

    last_report = 0

    def check_login(browser):

        nonlocal last_report

        check_timer()

        if verify_telemarketer_dashboard(browser):

            return True

        error_message = get_error_message(
            previous_messages
        )

        if error_message:

            raise AssertionError(
                f"New user login failed: {error_message}"
            )

        elapsed = (
            time.monotonic() - observation_start
        )

        if elapsed - last_report >= 5:

            last_report = elapsed

            print(
                f"Waiting for dashboard: "
                f"{elapsed:.0f} seconds"
            )

        return False

    step_wait().until(
        check_login
    )

    login_verified = True

    print("------------------------------------------")
    print("NEW USER LOGIN SUCCESSFUL")
    print(f"Full Name: {NEW_FULL_NAME}")
    print(f"Email: {NEW_EMAIL}")
    print(f"Role: {NEW_ROLE}")
    print("Telemarketer dashboard displayed.")
    print("------------------------------------------")

    screenshot(
        "Step_11_Telemarketer_Dashboard.png"
    )

    return (
        "New user successfully logged in "
        "to the Telemarketer dashboard."
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

        "Full Name": NEW_FULL_NAME,

        "Email": NEW_EMAIL,

        "Role": NEW_ROLE,

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

    if status != "NOT EXECUTED":

        screenshot(
            f"Step_{step:02d}_"
            f"{status.replace(' ', '_')}.png"
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

    except TimeoutException:

        status = "FAILED"

        details = (
            f"TIMEOUT: Step did not complete "
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

        details = (
            f"{type(error).__name__}: {error}"
        )

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
# COMPLETE TEST STEP LIST
# ==========================================

TEST_STEPS = [

    (
        1,
        "Click Add New User in sidebar",
        open_add_new_user
    ),

    (
        2,
        "Enter Full Name",
        enter_full_name
    ),

    (
        3,
        "Enter Email",
        enter_new_email
    ),

    (
        4,
        "Enter Password",
        enter_new_password
    ),

    (
        5,
        "Select Telemarketer Role",
        select_role
    ),

    (
        6,
        "Click ADD NEW USER",
        submit_new_user
    ),

    (
        7,
        "Open Users List and Verify User",
        verify_users_list
    ),

    (
        8,
        "Sign Out",
        sign_out
    ),

    (
        9,
        "Enter New User Login Email",
        enter_login_email
    ),

    (
        10,
        "Enter New User Login Password",
        enter_login_password
    ),

    (
        11,
        "Click Log In and Verify Dashboard",
        login_new_user
    )

]


# ==========================================
# MAIN TEST EXECUTION
# ==========================================

try:

    print()
    print("==========================================")
    print("TC-TLD-03")
    print("ADD USER")
    print("==========================================")

    print(f"Full Name: {NEW_FULL_NAME}")
    print(f"Email: {NEW_EMAIL}")
    print("Password: ********")
    print(f"Role: {NEW_ROLE}")
    print(f"Timeout: {TIMEOUT} seconds")

    print("Execution Mode: FULL TEST")
    print("Executing all 11 test steps.")
    print("==========================================")

    # ======================================
    # PRECONDITION - TEAM LEADER LOGIN
    # ======================================

    current_step = "Precondition: Team Leader Login"

    start_timer()

    login_team_leader()

    check_timer()

    precondition_passed = True

    deadline = None

    # ======================================
    # EXECUTE ALL 11 TEST STEPS
    # ======================================

    for step, description, action in TEST_STEPS:

        execute_step(
            step,
            description,
            action
        )

    screenshot(
        "Final_Test_Result.png"
    )


# ==========================================
# TIMEOUT ERROR HANDLER
# ==========================================

except TimeoutException:

    precondition_timeout = True

    print()
    print("==========================================")
    print("TC-TLD-03: FAILED")
    print("------------------------------------------")
    print(f"Failed at: {current_step}")
    print("Reason: EXECUTION TIMEOUT")
    print(f"Time Limit: {TIMEOUT} seconds")
    print("Current URL:", driver.current_url)
    print("==========================================")

    screenshot(
        "TC-TLD-03_Timeout.png"
    )


# ==========================================
# GENERAL ERROR HANDLER
# ==========================================

except Exception as error:

    print()
    print("==========================================")
    print("TC-TLD-03: EXECUTION STOPPED")
    print("------------------------------------------")
    print(f"Stopped at: {current_step}")
    print(f"Error Type: {type(error).__name__}")
    print(f"Error Details: {error}")
    print("==========================================")

    screenshot(
        "TC-TLD-03_Execution_Stopped.png"
    )


# ==========================================
# FINAL TEST SUMMARY
# ==========================================

finally:

    deadline = None

    total_execution_time = (
        time.monotonic() - test_start
    )

    # Record any unexecuted test steps.

    executed_steps = {

        result["Step"]

        for result in results

    }

    for step, description, action in TEST_STEPS:

        if step not in executed_steps:

            results.append({

                "Step": step,

                "Test Scenario": description,

                "Full Name": NEW_FULL_NAME,

                "Email": NEW_EMAIL,

                "Role": NEW_ROLE,

                "Status": "NOT EXECUTED",

                "Details": (
                    "A previous step or "
                    "precondition was unsuccessful."
                ),

                "Execution Time (Seconds)": 0

            })

    results.sort(
        key=lambda result: result["Step"]
    )

    # ======================================
    # STEP-BY-STEP SUMMARY
    # ======================================

    print()
    print("==========================================")
    print("TC-TLD-03: FINAL TEST SUMMARY")
    print("==========================================")

    for result in results:

        print(
            f"Step {result['Step']}: "
            f"{result['Test Scenario']}"
        )

        print(f"Result: {result['Status']}")
        print(f"Details: {result['Details']}")

        print(
            "Execution Time: "
            f"{result['Execution Time (Seconds)']:.2f} "
            "seconds"
        )

        print("------------------------------------------")

    # ======================================
    # COUNT TEST RESULTS
    # ======================================

    passed = sum(
        result["Status"] == "PASSED"
        for result in results
    )

    failed = sum(
        result["Status"] == "FAILED"
        for result in results
    )

    timed_out = sum(
        result["Status"] == "FAILED"
        and "TIMEOUT" in result["Details"]
        for result in results
    )

    if precondition_timeout:

        timed_out += 1

    not_executed = sum(
        result["Status"] == "NOT EXECUTED"
        for result in results
    )

    # ======================================
    # DISPLAY TOTAL TEST RESULTS
    # ======================================

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

    print("Total Test Steps: 11")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Timeout Failures: {timed_out}")
    print(f"Not Executed: {not_executed}")

    print("------------------------------------------")

    print(f"New User Full Name: {NEW_FULL_NAME}")
    print(f"New User Email: {NEW_EMAIL}")
    print(f"New User Role: {NEW_ROLE}")

    print(f"Success Message: {success_message}")

    print(
        "Account Creation Confirmed: "
        + ("YES" if creation_confirmed else "NO")
    )

    print(
        "Account Found in Users List: "
        + ("YES" if user_verified else "NO")
    )

    print(
        "Telemarketer Login Verified: "
        + ("YES" if login_verified else "NO")
    )

    print(
        f"Total Execution Time: "
        f"{total_execution_time:.2f} seconds"
    )

    print("------------------------------------------")

    # ======================================
    # DETERMINE FINAL RESULT
    # ======================================

    if precondition_timeout or failed > 0:

        final_result = "FAILED"

    elif not precondition_passed:

        final_result = "BLOCKED"

    elif (
        passed == 11
        and creation_confirmed
        and user_verified
        and login_verified
    ):

        final_result = "PASSED"

    else:

        final_result = "NOT FULLY VERIFIED"

    print(f"FINAL RESULT: {final_result}")

    # ======================================
    # EXPORT CSV TEST RESULTS
    # ======================================

    csv_path = os.path.join(
        RUN_FOLDER,
        "TC-TLD-03_Test_Results.csv"
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
                "Full Name",
                "Email",
                "Role",
                "Status",
                "Details",
                "Execution Time (Seconds)"

            ]

        )

        writer.writeheader()

        writer.writerows(results)

    print()
    print(f"Test Results: {csv_path}")
    print(f"Evidence Folder: {RUN_FOLDER}")
    print("==========================================")

    # ======================================
    # KEEP BROWSER OPEN FOR INSPECTION
    # ======================================

    try:

        input(
            "\nPress Enter to close the browser..."
        )

    finally:

        driver.quit()
