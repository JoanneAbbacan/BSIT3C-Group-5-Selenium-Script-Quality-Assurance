
import os
import csv
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException
)

# ==========================================
# TC-TEL-06
# SEND EMAIL WITH EMPTY REQUIRED FIELDS
# ==========================================

URL = "https://sortrleaddistribution-client.onrender.com/"

# Telemarketer login credentials

EMAIL = "dranheirdejesus@gmail.com"
PASSWORD = "ABCabc123!"

# Email test inputs

FROM_EMAIL = "jbabbacan@gmail.com"
TO_EMAIL = "onlydrans@example.com"

SUBJECT = "sample text"

MESSAGE = "Test message for lead outreach."

TIMEOUT = 120

# ==========================================
# EVIDENCE FOLDER
# ==========================================

EVIDENCE_FOLDER = "TC-TEL-06_Evidence"

os.makedirs(
    EVIDENCE_FOLDER,
    exist_ok=True
)

# ==========================================
# CHROME CONFIGURATION
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

deadline = None

current_step = "Precondition"

test_start = time.monotonic()

precondition_passed = False

selected_lead_id = ""

unexpected_send = False

# ==========================================
# ELEMENT LOCATORS
# ==========================================

EMAIL_FIELD = (
    By.CSS_SELECTOR,
    'input[type="email"]'
)

PASSWORD_FIELD = (
    By.CSS_SELECTOR,
    'input[type="password"]'
)

LOGIN_BUTTON = (
    By.XPATH,
    "//button[normalize-space()='Log In']"
)

LEADS_LINK = (
    By.XPATH,
    "//li[contains(@class,'ps-menuitem-root')]"
    "[.//*[normalize-space()='Leads']]"
)

ASSIGNED_TITLE = (
    By.XPATH,
    "//*[normalize-space()='ASSIGNED LEADS']"
)

ROW_SELECTOR = (
    ".MuiDataGrid-row, "
    "table tbody tr, "
    "[role='rowgroup'] [role='row']"
)

SEND_BUTTON = (
    By.XPATH,
    ".//button[translate(normalize-space(.),"
    "'abcdefghijklmnopqrstuvwxyz',"
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='SEND']"
)

# ==========================================
# CUSTOM EXCEPTIONS
# ==========================================

class TestBlocked(Exception):
    pass


class UnexpectedSend(Exception):
    pass


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
        poll_frequency=0.25,
        ignored_exceptions=(
            StaleElementReferenceException,
        )
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
# AUTOMATIC LOGIN
# ==========================================

def login():

    print("Opening website...")

    driver.get(URL)

    email_field = step_wait().until(
        EC.visibility_of_element_located(
            EMAIL_FIELD
        )
    )

    email_field.clear()
    email_field.send_keys(EMAIL)

    password_field = step_wait().until(
        EC.visibility_of_element_located(
            PASSWORD_FIELD
        )
    )

    password_field.clear()
    password_field.send_keys(PASSWORD)

    step_wait().until(
        EC.element_to_be_clickable(
            LOGIN_BUTTON
        )
    ).click()

    step_wait().until(
        EC.element_to_be_clickable(
            LEADS_LINK
        )
    )

    print("Login successful.")

    screenshot(
        "Precondition_Login_Success.png"
    )


# ==========================================
# OPEN ASSIGNED LEADS
# ==========================================

def open_assigned_leads():

    step_wait().until(
        EC.element_to_be_clickable(
            LEADS_LINK
        )
    ).click()

    step_wait().until(
        EC.visibility_of_element_located(
            ASSIGNED_TITLE
        )
    )

    step_wait().until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".MuiDataGrid-root, table, [role='grid']"
            )
        )
    )

    print("Assigned Leads page opened.")

    screenshot(
        "Precondition_Assigned_Leads.png"
    )


# ==========================================
# FIND AUTHORIZED RECIPIENT LEAD
# ==========================================

def find_lead_row():

    global selected_lead_id

    def locate(browser):

        check_timer()

        rows = browser.find_elements(
            By.CSS_SELECTOR,
            ROW_SELECTOR
        )

        for row in rows:

            if not row.is_displayed():

                continue

            cells = row.find_elements(
                By.CSS_SELECTOR,
                "td, [role='gridcell'], [role='cell']"
            )

            for cell in cells:

                if (
                    cell.text.strip().lower()
                    == TO_EMAIL.lower()
                ):

                    return row

        return False

    row = step_wait().until(locate)

    id_cells = row.find_elements(
        By.CSS_SELECTOR,
        '[data-field="id"], [data-field="leadid"]'
    )

    if id_cells:

        selected_lead_id = id_cells[0].text.strip()

    else:

        selected_lead_id = (
            row.get_attribute("data-id")
            or "Not available"
        )

    print(f"Lead ID: {selected_lead_id}")
    print(f"Lead Email: {TO_EMAIL}")

    return row


# ==========================================
# FIND EMAIL COMPOSE FORM
# ==========================================

def find_visible_email_form(browser):

    containers = browser.find_elements(
        By.CSS_SELECTOR,
        "[role='dialog'], .MuiModal-root, form"
    )

    for container in containers:

        try:

            if not container.is_displayed():

                continue

            buttons = container.find_elements(
                *SEND_BUTTON
            )

            if any(
                button.is_displayed()
                for button in buttons
            ):

                return container

        except StaleElementReferenceException:

            continue

    return False


def get_email_form():

    return step_wait().until(
        find_visible_email_form
    )


# ==========================================
# CLICK EMAIL ICON
# ==========================================

def open_email_form():

    row = find_lead_row()

    buttons = row.find_elements(
        By.XPATH,
        ".//button["
        ".//*[contains(@data-testid,'Email')]"
        " or .//*[contains(@data-testid,'Mail')]"
        " or contains("
        "translate(@aria-label,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'email')"
        " or contains("
        "translate(@title,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'email')"
        "]"
    )

    buttons = [
        button for button in buttons
        if button.is_displayed()
        and button.is_enabled()
    ]

    if len(buttons) == 1:

        email_button = buttons[0]

    elif len(buttons) == 0:

        action_cells = row.find_elements(
            By.CSS_SELECTOR,
            '[data-field="actions"], '
            'td:last-child, '
            '[role="gridcell"]:last-child'
        )

        if len(action_cells) != 1:

            raise TestBlocked(
                "Actions column not identified."
            )

        action_buttons = action_cells[0].find_elements(
            By.CSS_SELECTOR,
            "button, [role='button']"
        )

        action_buttons = [
            button for button in action_buttons
            if button.is_displayed()
        ]

        if len(action_buttons) != 4:

            raise TestBlocked(
                "Expected View, Edit, Call and Email icons."
            )

        email_button = action_buttons[3]

    else:

        raise TestBlocked(
            "Multiple email buttons found."
        )

    driver.execute_script(
        "arguments[0].scrollIntoView("
        "{block:'center', inline:'center'});",
        email_button
    )

    email_button.click()

    get_email_form()

    print("Email compose form opened.")


# ==========================================
# FIND FROM AND TO FIELDS
# ==========================================

def get_email_field(field_name):

    form = get_email_form()

    aliases = {
        "from": [
            "from",
            "fromemail",
            "sender",
            "senderemail"
        ],
        "to": [
            "to",
            "toemail",
            "recipient",
            "recipientemail"
        ]
    }

    fields = form.find_elements(
        By.CSS_SELECTOR,
        "input:not([type='hidden'])"
    )

    fields = [
        field for field in fields
        if field.is_displayed()
    ]

    for field in fields:

        attributes = [
            field.get_attribute("name") or "",
            field.get_attribute("id") or "",
            field.get_attribute("aria-label") or "",
            field.get_attribute("placeholder") or ""
        ]

        for attribute in attributes:

            normalized = re.sub(
                r"[^a-z]",
                "",
                attribute.lower()
            )

            if normalized in aliases[field_name]:

                return field

        containers = field.find_elements(
            By.XPATH,
            "./ancestor::*[contains(@class,"
            "'MuiFormControl-root')][1]"
        )

        for container in containers:

            labels = container.find_elements(
                By.TAG_NAME,
                "label"
            )

            for label in labels:

                label_text = re.sub(
                    r"[^a-z]",
                    "",
                    label.text.lower()
                )

                if label_text in aliases[field_name]:

                    return field

    email_fields = [
        field for field in fields
        if field.get_attribute("type") == "email"
    ]

    if len(email_fields) == 2:

        if field_name == "from":

            return email_fields[0]

        return email_fields[1]

    raise TestBlocked(
        f"{field_name.upper()} field not identified."
    )


# ==========================================
# FIND SUBJECT DROPDOWN
# ==========================================

def get_subject_dropdown():

    form = get_email_form()

    dropdowns = form.find_elements(
        By.CSS_SELECTOR,
        "[role='combobox'], select"
    )

    dropdowns = [
        dropdown for dropdown in dropdowns
        if dropdown.is_displayed()
    ]

    for dropdown in dropdowns:

        attributes = " ".join([
            dropdown.get_attribute("name") or "",
            dropdown.get_attribute("id") or "",
            dropdown.get_attribute("aria-label") or "",
            dropdown.get_attribute(
                "aria-labelledby"
            ) or ""
        ])

        if "subject" in attributes.lower():

            return dropdown

    if len(dropdowns) == 1:

        return dropdowns[0]

    raise TestBlocked(
        "Subject dropdown not identified."
    )


# ==========================================
# FIND MESSAGE FIELD
# ==========================================

def get_message_field():

    form = get_email_form()

    selectors = [
        'textarea[name="body"]',
        'textarea[name="message"]',
        'textarea[name="text"]',
        'textarea[name="content"]',
        'textarea[name="emailBody"]',
        '[contenteditable="true"]',
        'textarea'
    ]

    for selector in selectors:

        fields = form.find_elements(
            By.CSS_SELECTOR,
            selector
        )

        fields = [
            field for field in fields
            if field.is_displayed()
        ]

        if len(fields) == 1:

            return fields[0]

    raise TestBlocked(
        "Message field not identified."
    )


# ==========================================
# READ FIELD VALUE
# ==========================================

def get_field_value(field):

    if field.get_attribute(
        "contenteditable"
    ) == "true":

        return field.text.strip()

    return (
        field.get_attribute("value") or ""
    ).strip()


# ==========================================
# SET OR CLEAR TEXT FIELD
# ==========================================

def set_text_field(field, value, label):

    check_timer()

    current_value = get_field_value(field)

    if current_value == value:

        return

    if (
        not field.is_enabled()
        or field.get_attribute("readonly") is not None
        or field.get_attribute("aria-readonly") == "true"
    ):

        raise TestBlocked(
            f"{label} is read-only or disabled."
        )

    field.click()

    field.send_keys(
        Keys.CONTROL,
        "a"
    )

    field.send_keys(
        Keys.BACKSPACE
    )

    if value:

        field.send_keys(value)

    actual_value = get_field_value(field)

    if actual_value != value:

        raise TestBlocked(
            f"Unable to prepare {label}. "
            f"Expected: {value!r}. "
            f"Actual: {actual_value!r}."
        )


# ==========================================
# SUBJECT PLACEHOLDERS
# ==========================================

def is_empty_subject(text):

    normalized = text.strip().lower()

    return normalized in [
        "",
        "subject",
        "subject *",
        "select",
        "select subject",
        "select a subject",
        "select template",
        "select a template",
        "choose subject",
        "choose a subject",
        "none"
    ]


# ==========================================
# READ SUBJECT VALUE
# ==========================================

def get_subject_value():

    dropdown = get_subject_dropdown()

    if dropdown.tag_name.lower() == "select":

        option = Select(
            dropdown
        ).first_selected_option

        if option.get_attribute("value") == "":

            return ""

        value = option.text.strip()

    else:

        value = dropdown.text.strip()

    if is_empty_subject(value):

        return ""

    return value


# ==========================================
# SELECT OR CLEAR SUBJECT
# ==========================================

def set_subject(value):

    dropdown = get_subject_dropdown()

    current_value = get_subject_value()

    if current_value == value:

        return

    if dropdown.tag_name.lower() == "select":

        select = Select(dropdown)

        matching_options = []

        for option in select.options:

            text = option.text.strip()

            if value:

                matches = text == value

            else:

                matches = (
                    is_empty_subject(text)
                    or option.get_attribute("value") == ""
                )

            if matches and option.is_enabled():

                matching_options.append(option)

        if not matching_options:

            raise TestBlocked(
                f"Subject option unavailable: {value!r}"
            )

        matching_options[0].click()

    else:

        dropdown.click()

        options = step_wait().until(
            lambda d: [
                option
                for option in d.find_elements(
                    By.CSS_SELECTOR,
                    "[role='option']"
                )
                if option.is_displayed()
            ] or False
        )

        matching_options = []

        for option in options:

            if option.get_attribute(
                "aria-disabled"
            ) == "true":

                continue

            text = option.text.strip()

            if value:

                matches = text == value

            else:

                matches = (
                    is_empty_subject(text)
                    or option.get_attribute("data-value") == ""
                )

            if matches:

                matching_options.append(option)

        if not matching_options:

            dropdown.send_keys(Keys.ESCAPE)

            raise TestBlocked(
                f"Subject option unavailable: {value!r}"
            )

        matching_options[0].click()

    step_wait().until(
        lambda d: get_subject_value() == value
    )


# ==========================================
# PREPARE EMAIL TEST INPUTS
# ==========================================

def prepare_email(
    from_value,
    to_value,
    subject_value,
    message_value
):

    print("Preparing email test inputs...")

    # Set subject first because selecting
    # a template may automatically fill
    # the email message.

    set_subject(subject_value)

    set_text_field(
        get_email_field("from"),
        from_value,
        "From"
    )

    set_text_field(
        get_email_field("to"),
        to_value,
        "To"
    )

    set_text_field(
        get_message_field(),
        message_value,
        "Message"
    )

    actual_values = {
        "From": get_field_value(
            get_email_field("from")
        ),
        "To": get_field_value(
            get_email_field("to")
        ),
        "Subject": get_subject_value(),
        "Message": get_field_value(
            get_message_field()
        )
    }

    expected_values = {
        "From": from_value,
        "To": to_value,
        "Subject": subject_value,
        "Message": message_value
    }

    print("-----------------------------------")

    for field_name, expected in expected_values.items():

        actual = actual_values[field_name]

        print(
            f"{field_name}: "
            f"{actual if actual else '[EMPTY]'}"
        )

        if actual != expected:

            raise TestBlocked(
                f"{field_name} test input "
                "verification failed."
            )

    print("-----------------------------------")
    print("All test inputs verified.")


# ==========================================
# INSTALL VALIDATION MONITOR
# ==========================================

def install_validation_monitor():

    driver.execute_script("""
        if (window.__tel06Observer) {
            window.__tel06Observer.disconnect();
        }

        if (window.__tel06InvalidHandler) {
            document.removeEventListener(
                'invalid',
                window.__tel06InvalidHandler,
                true
            );
        }

        window.__tel06Errors = [];
        window.__tel06Messages = [];

        window.__tel06InvalidHandler = function(event) {

            const field = event.target;

            window.__tel06Errors.push({
                name: field.name || field.id || 'Field',
                message: field.validationMessage
            });
        };

        document.addEventListener(
            'invalid',
            window.__tel06InvalidHandler,
            true
        );

        const selector =
            '[role="alert"], ' +
            '[role="status"], ' +
            '.MuiAlert-message, ' +
            '.MuiSnackbar-root, ' +
            '.Toastify__toast, ' +
            '.MuiFormHelperText-root.Mui-error';

        function inspect(node) {

            if (!node) return;

            if (node.nodeType === Node.TEXT_NODE) {

                const message = node.textContent.trim();

                if (message) {
                    window.__tel06Messages.push(message);
                }

                return;
            }

            if (node.nodeType !== Node.ELEMENT_NODE) {
                return;
            }

            const elements = [
                node,
                ...node.querySelectorAll(selector)
            ];

            for (const element of elements) {

                const message = (
                    element.innerText ||
                    element.textContent ||
                    ''
                ).trim();

                if (message && message.length < 500) {

                    window.__tel06Messages.push(message);
                }
            }
        }

        window.__tel06Observer =
            new MutationObserver(function(mutations) {

                for (const mutation of mutations) {

                    if (mutation.type === 'characterData') {
                        inspect(mutation.target);
                    }

                    for (const node of mutation.addedNodes) {
                        inspect(node);
                    }
                }
            });

        window.__tel06Observer.observe(
            document.body,
            {
                childList: true,
                subtree: true,
                characterData: true
            }
        );
    """)


# ==========================================
# GET VALIDATION MESSAGES
# ==========================================

def get_validation_messages():

    messages = driver.execute_script("""
        return window.__tel06Errors || [];
    """)

    form = find_visible_email_form(driver)

    if form:

        native_errors = driver.execute_script("""
            return Array.from(
                arguments[0].querySelectorAll(
                    'input, select, textarea'
                )
            ).filter(
                field => field.willValidate &&
                         !field.validity.valid
            ).map(
                field => ({
                    name: field.name || field.id || 'Field',
                    message: field.validationMessage
                })
            );
        """, form)

        messages.extend(native_errors)

        error_elements = form.find_elements(
            By.CSS_SELECTOR,
            ".MuiFormHelperText-root.Mui-error, "
            "[role='alert']"
        )

        for element in error_elements:

            if element.is_displayed():

                text = element.text.strip()

                if text:

                    messages.append({
                        "name": "Form",
                        "message": text
                    })

    unique_messages = []

    for message in messages:

        if message not in unique_messages:

            unique_messages.append(message)

    return unique_messages


# ==========================================
# GET NOTIFICATION MESSAGES
# ==========================================

def get_notifications():

    messages = driver.execute_script("""
        return window.__tel06Messages || [];
    """)

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "[role='alert'], "
        "[role='status'], "
        ".MuiAlert-message, "
        ".MuiSnackbar-root, "
        ".Toastify__toast"
    )

    for element in elements:

        try:

            if element.is_displayed():

                text = element.text.strip()

                if text:

                    messages.append(text)

        except StaleElementReferenceException:

            continue

    return messages


# ==========================================
# CHECK SUBMISSION OUTCOME
# ==========================================

def check_submission(browser):

    check_timer()

    notifications = get_notifications()

    success_pattern = (
        r"email\s+(?:has\s+been\s+)?sent"
        r"|successfully\s+sent"
        r"|sent\s+successfully"
        r"|send\s+successfully"
    )

    for message in notifications:

        if re.search(
            success_pattern,
            message,
            re.IGNORECASE
        ) and not re.search(
            r"failed|not sent|error|unsuccessful",
            message,
            re.IGNORECASE
        ):

            return "UNEXPECTED_SUCCESS", message

    validation = get_validation_messages()

    if validation:

        return "VALIDATION", validation

    validation_pattern = (
        r"required"
        r"|please fill"
        r"|cannot be empty"
        r"|must not be empty"
        r"|please enter"
        r"|please select"
        r"|all fields"
        r"|invalid email"
    )

    for message in notifications:

        if re.search(
            validation_pattern,
            message,
            re.IGNORECASE
        ):

            return "VALIDATION", message

    return False


# ==========================================
# CLICK SEND WITH EMPTY FIELDS
# ==========================================

def submit_invalid_email():

    form = get_email_form()

    buttons = form.find_elements(
        *SEND_BUTTON
    )

    buttons = [
        button for button in buttons
        if button.is_displayed()
    ]

    if len(buttons) != 1:

        raise TestBlocked(
            "SEND button not identified."
        )

    send_button = buttons[0]

    if (
        not send_button.is_enabled()
        or send_button.get_attribute(
            "aria-disabled"
        ) == "true"
    ):

        return (
            "SEND button is disabled. "
            "Email submission was prevented."
        )

    install_validation_monitor()

    send_button.click()

    print("SEND button clicked.")
    print("Checking validation result...")

    outcome, message = step_wait().until(
        check_submission
    )

    if outcome == "UNEXPECTED_SUCCESS":

        raise UnexpectedSend(
            f"Email accepted despite empty fields: "
            f"{message}"
        )

    if outcome == "VALIDATION":

        print("Validation message detected:")
        print(message)

        # Allow time to detect a delayed
        # unexpected success notification.

        observation_end = (
            time.monotonic() + 3
        )

        while time.monotonic() < observation_end:

            check_timer()

            result = check_submission(driver)

            if result:

                if result[0] == "UNEXPECTED_SUCCESS":

                    raise UnexpectedSend(
                        str(result[1])
                    )

            time.sleep(0.25)

        if not find_visible_email_form(driver):

            raise AssertionError(
                "The compose form closed after submission. "
                "Unable to confirm that the email was blocked."
            )

        return (
            "Email submission prevented. "
            f"Validation: {message}"
        )

    raise AssertionError(
        "Email validation could not be confirmed."
    )


# ==========================================
# CLOSE EMAIL FORM WITHOUT REFRESHING
# ==========================================

def close_email_form():

    form = find_visible_email_form(driver)

    if not form:

        return

    close_buttons = form.find_elements(
        By.XPATH,
        ".//button["
        "normalize-space()='Cancel'"
        " or normalize-space()='CANCEL'"
        " or normalize-space()='Close'"
        " or normalize-space()='CLOSE'"
        " or @aria-label='close'"
        " or @aria-label='Close'"
        " or .//*[@data-testid='CloseIcon']"
        "]"
    )

    close_buttons = [
        button for button in close_buttons
        if button.is_displayed()
        and button.is_enabled()
    ]

    if close_buttons:

        close_buttons[0].click()

    else:

        driver.switch_to.active_element.send_keys(
            Keys.ESCAPE
        )

    try:

        WebDriverWait(
            driver,
            min(5, remaining_time())
        ).until(
            lambda d: not find_visible_email_form(d)
        )

    except TimeoutException:

        raise TestBlocked(
            "Unable to close the email form safely. "
            "No page refresh was performed."
        )

    print("Email form closed.")


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
        "Lead ID": selected_lead_id,
        "Status": status,
        "Details": details,
        "Execution Time (Seconds)": round(
            elapsed,
            2
        )
    })

    print("-----------------------------------")
    print(f"STEP {step}: {status}")
    print(f"Details: {details}")
    print(f"Execution Time: {elapsed:.2f} seconds")
    print(f"Time Limit: {TIMEOUT} seconds")
    print("-----------------------------------")

    screenshot(
        f"Step_{step:02d}_{status}.png"
    )


# ==========================================
# EXECUTE INDIVIDUAL EMPTY FIELD SCENARIO
# ==========================================

def execute_scenario(
    step,
    description,
    from_value,
    to_value,
    subject_value,
    message_value
):

    global current_step
    global deadline
    global unexpected_send

    current_step = f"Step {step}: {description}"

    start = start_timer()

    status = "PASSED"
    details = ""

    print()
    print("===================================")
    print(current_step)
    print(f"TIME LIMIT: {TIMEOUT} SECONDS")
    print("===================================")

    try:

        # Open a fresh compose form for
        # every independent test scenario.

        if find_visible_email_form(driver):

            close_email_form()

        open_email_form()

        prepare_email(
            from_value,
            to_value,
            subject_value,
            message_value
        )

        screenshot(
            f"Step_{step:02d}_Before_Send.png"
        )

        details = submit_invalid_email()

        check_timer()

    except TimeoutException:

        status = "FAILED"

        details = (
            f"TIMEOUT: Step did not complete "
            f"within {TIMEOUT} seconds."
        )

        print()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"STEP {step}: FAILED")
        print("REASON: EXECUTION TIMEOUT")
        print(f"TIME LIMIT: {TIMEOUT} SECONDS")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    except TestBlocked as error:

        status = "BLOCKED"

        details = str(error)

    except UnexpectedSend as error:

        status = "FAILED"

        details = str(error)

        unexpected_send = True

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

    # Stop after an unexpected successful
    # submission to prevent further emails.

    if unexpected_send:

        raise RuntimeError(
            "Testing stopped because an invalid "
            "email was unexpectedly accepted."
        )

    # A timeout may mean the send result
    # is unknown. Do not retry automatically.

    if status == "FAILED" and "TIMEOUT" in details:

        raise RuntimeError(
            "Testing stopped because the previous "
            "submission outcome is uncertain."
        )

    if status == "FAILED":

        raise RuntimeError(
            "Testing stopped after an unverified "
            "submission outcome."
        )


# ==========================================
# MAIN TEST EXECUTION
# ==========================================

try:

    print("===================================")
    print("TC-TEL-06")
    print("SEND EMAIL WITH EMPTY FIELDS")
    print(f"TIMEOUT: {TIMEOUT} SECONDS")
    print("===================================")

    # ======================================
    # PRECONDITION 1: LOGIN
    # ======================================

    current_step = "Precondition: Login"

    start_timer()

    login()

    # ======================================
    # PRECONDITION 2: ASSIGNED LEADS
    # ======================================

    current_step = "Precondition: Assigned Leads"

    start_timer()

    open_assigned_leads()

    # ======================================
    # PRECONDITION 3: FIND TEST LEAD
    # ======================================

    current_step = "Precondition: Find Test Lead"

    start_timer()

    find_lead_row()

    precondition_passed = True

    deadline = None

    # ======================================
    # STEP 1: EMPTY FROM FIELD
    # ======================================

    execute_scenario(
        step=1,
        description="Leave From Field Empty",
        from_value="",
        to_value=TO_EMAIL,
        subject_value="",
        message_value=""
    )

    # ======================================
    # STEP 2: EMPTY TO FIELD
    # ======================================

    execute_scenario(
        step=2,
        description="Leave To Field Empty",
        from_value=FROM_EMAIL,
        to_value="",
        subject_value="",
        message_value=""
    )

    # ======================================
    # STEP 3: EMPTY SUBJECT FIELD
    # ======================================

    execute_scenario(
        step=3,
        description="Leave Subject Field Empty",
        from_value=FROM_EMAIL,
        to_value=TO_EMAIL,
        subject_value="",
        message_value=MESSAGE
    )

    # ======================================
    # STEP 4: EMPTY MESSAGE FIELD
    # ======================================

    execute_scenario(
        step=4,
        description="Leave Message Field Empty",
        from_value=FROM_EMAIL,
        to_value=TO_EMAIL,
        subject_value=SUBJECT,
        message_value=""
    )

    # ======================================
    # STEP 5: ALL REQUIRED FIELDS EMPTY
    # ======================================

    execute_scenario(
        step=5,
        description="Leave All Required Fields Empty",
        from_value="",
        to_value="",
        subject_value="",
        message_value=""
    )

    screenshot(
        "Final_Test_Result.png"
    )


# ==========================================
# TIMEOUT ERROR HANDLER
# ==========================================

except TimeoutException:

    print()
    print("===================================")
    print("TC-TEL-06: FAILED")
    print(f"Failed at: {current_step}")
    print("REASON: EXECUTION TIMEOUT")
    print(f"TIME LIMIT: {TIMEOUT} SECONDS")
    print("===================================")

    screenshot(
        "TC-TEL-06_Timeout.png"
    )


# ==========================================
# GENERAL ERROR HANDLER
# ==========================================

except Exception as error:

    print()
    print("===================================")
    print("TC-TEL-06: EXECUTION STOPPED")
    print(f"Stopped at: {current_step}")
    print(f"Reason: {error}")
    print("===================================")

    screenshot(
        "TC-TEL-06_Execution_Stopped.png"
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
    print("===================================")
    print("TC-TEL-06: FINAL TEST SUMMARY")
    print("===================================")

    for result in results:

        print(
            f"Step {result['Step']}: "
            f"{result['Test Scenario']}"
        )

        print(
            f"Result: {result['Status']}"
        )

        print(
            f"Details: {result['Details']}"
        )

        print(
            "Execution Time: "
            f"{result['Execution Time (Seconds)']:.2f} "
            "seconds"
        )

        print("-----------------------------------")

    passed = sum(
        result["Status"] == "PASSED"
        for result in results
    )

    failed = sum(
        result["Status"] == "FAILED"
        for result in results
    )

    blocked = sum(
        result["Status"] == "BLOCKED"
        for result in results
    )

    timed_out = sum(
        result["Status"] == "FAILED"
        and "TIMEOUT" in result["Details"]
        for result in results
    )

    not_executed = 5 - len(results)

    print()
    print("===================================")
    print("TOTAL TEST RESULTS")
    print("===================================")

    print(
        "Precondition: "
        + (
            "PASSED"
            if precondition_passed
            else "NOT SATISFIED"
        )
    )

    print("Total Test Scenarios: 5")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Blocked: {blocked}")
    print(f"Timeout Failures: {timed_out}")
    print(f"Not Executed: {not_executed}")

    print("-----------------------------------")

    print(
        "Unexpected Email Success: "
        + ("YES" if unexpected_send else "NO DETECTED")
    )

    print(
        f"Total Execution Time: "
        f"{total_execution_time:.2f} seconds"
    )

    print("-----------------------------------")

    if not precondition_passed:

        final_result = "BLOCKED"

    elif failed > 0 or unexpected_send:

        final_result = "FAILED"

    elif blocked > 0 or not_executed > 0:

        final_result = "BLOCKED"

    elif passed == 5:

        final_result = "PASSED"

    else:

        final_result = "NOT FULLY VERIFIED"

    print(f"FINAL RESULT: {final_result}")

    # ======================================
    # EXPORT CSV TEST REPORT
    # ======================================

    csv_path = os.path.join(
        EVIDENCE_FOLDER,
        "TC-TEL-06_Test_Results.csv"
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
                "Lead ID",
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
    print("===================================")

    # Keep browser open for inspection.

    try:

        input(
            "\nPress Enter to close the browser..."
        )

    finally:

        driver.quit()
