
import os
import csv
import time
import re

from datetime import datetime

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
# TC-TEL-05 - SEND EMAIL
# ==========================================

URL = "https://sortrleaddistribution-client.onrender.com/"

EMAIL = "dranheirdejesus@gmail.com"
PASSWORD = "ABCabc123!"

RECIPIENT = "onlydrans@example.com"

EMAIL_BODY = (
    "Good day, we are following up about your "
    "inquiry regarding the hot-water system upgrade."
)

TIMEOUT = 120

# ==========================================
# SCREENSHOT EVIDENCE FOLDER
# ==========================================

EVIDENCE_FOLDER = "TC-TEL-05_Evidence"

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

selected_subject = ""
selected_lead_id = ""
selected_lead_name = ""

current_step = "Precondition"

deadline = None

test_start = time.monotonic()

precondition_passed = False
main_failed = False

email_sent = False
email_verified = False

send_time = None

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

EMAILS_LINK = (
    By.XPATH,
    "//li[contains(@class,'ps-menuitem-root')]"
    "[.//*[normalize-space()='Emails']]"
)

ASSIGNED_TITLE = (
    By.XPATH,
    "//*[normalize-space()='ASSIGNED LEADS']"
)

SEND_BUTTON = (
    By.XPATH,
    ".//button[translate(normalize-space(.),"
    "'abcdefghijklmnopqrstuvwxyz',"
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='SEND']"
)

ROW_SELECTOR = (
    ".MuiDataGrid-row, "
    "table tbody tr, "
    "[role='rowgroup'] [role='row']"
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

        else:

            print("Screenshot could not be saved.")

    except Exception as error:

        print(f"Screenshot error: {error}")


# ==========================================
# RECORD TEST RESULT
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
        "Lead ID": selected_lead_id or "N/A",
        "Recipient": RECIPIENT,
        "Subject": selected_subject or "N/A",
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
# EXECUTE TEST STEP
# ==========================================

def execute_step(
    step,
    description,
    action
):

    global current_step
    global deadline

    current_step = f"Step {step}: {description}"

    start = start_timer()

    print()
    print("===================================")
    print(current_step)
    print(f"TIME LIMIT: {TIMEOUT} SECONDS")
    print("===================================")

    status = "PASSED"
    details = ""

    try:

        result = action()

        check_timer()

        details = (
            str(result)
            if result
            else "Step completed successfully."
        )

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

    except Exception as error:

        status = "FAILED"

        details = str(error)

    finally:

        elapsed = time.monotonic() - start

        deadline = None

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

    if status != "PASSED":

        raise RuntimeError(
            f"Step {step} failed: {details}"
        )


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
# GET VISIBLE TABLE ROWS
# ==========================================

def get_rows():

    check_timer()

    rows = driver.find_elements(
        By.CSS_SELECTOR,
        ROW_SELECTOR
    )

    return [
        row for row in rows
        if row.is_displayed()
    ]


# ==========================================
# GET LEAD CELL VALUE
# ==========================================

def get_cell_value(row, field_names):

    cells = row.find_elements(
        By.CSS_SELECTOR,
        "[data-field]"
    )

    for cell in cells:

        field = cell.get_attribute(
            "data-field"
        ) or ""

        normalized = re.sub(
            r"[^a-z0-9]",
            "",
            field.lower()
        )

        if normalized in field_names:

            return cell.text.strip()

    return ""


# ==========================================
# FIND LEAD WITH REQUIRED RECIPIENT
# ==========================================

def find_recipient_lead():

    global selected_lead_id
    global selected_lead_name

    print()
    print(f"Searching for recipient: {RECIPIENT}")

    def locate(browser):

        check_timer()

        for row in get_rows():

            cells = row.find_elements(
                By.CSS_SELECTOR,
                "td, [role='gridcell'], [role='cell']"
            )

            for cell in cells:

                if (
                    cell.text.strip().lower()
                    == RECIPIENT.lower()
                ):

                    return row

        return False

    row = step_wait().until(locate)

    selected_lead_id = get_cell_value(
        row,
        ["id", "leadid"]
    )

    selected_lead_name = get_cell_value(
        row,
        ["name", "leadname"]
    )

    if not selected_lead_id:

        cells = row.find_elements(
            By.CSS_SELECTOR,
            "td, [role='gridcell']"
        )

        data_cells = [
            cell for cell in cells
            if not cell.find_elements(
                By.CSS_SELECTOR,
                "input[type='checkbox'], "
                "[role='checkbox']"
            )
        ]

        if len(data_cells) >= 2:

            selected_lead_id = (
                data_cells[0].text.strip()
            )

            selected_lead_name = (
                data_cells[1].text.strip()
            )

    print(f"Lead ID: {selected_lead_id}")
    print(f"Lead Name: {selected_lead_name}")
    print(f"Recipient: {RECIPIENT}")

    screenshot(
        "Precondition_Recipient_Lead_Found.png"
    )

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
# VERIFY EMAIL RECIPIENT
# ==========================================

def verify_recipient():

    form = get_email_form()

    fields = form.find_elements(
        By.CSS_SELECTOR,
        "input, textarea"
    )

    for field in fields:

        if not field.is_displayed():

            continue

        value = (
            field.get_attribute("value") or ""
        ).strip()

        if value.lower() == RECIPIENT.lower():

            print(f"Recipient verified: {RECIPIENT}")

            return True

    # Support recipient fields displayed as text.

    text = form.text

    for line in text.splitlines():

        normalized = line.strip().lower()

        if normalized in [
            RECIPIENT.lower(),
            f"to: {RECIPIENT.lower()}"
        ]:

            print(f"Recipient verified: {RECIPIENT}")

            return True

    raise AssertionError(
        "The compose form does not show the "
        "required recipient. Email will not be sent."
    )


# ==========================================
# STEP 1 - CLICK EMAIL ICON
# ==========================================

def click_email_icon():

    row = find_recipient_lead()

    email_buttons = row.find_elements(
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

    email_buttons = [
        button for button in email_buttons
        if button.is_displayed()
        and button.is_enabled()
    ]

    if len(email_buttons) == 1:

        email_button = email_buttons[0]

    elif len(email_buttons) == 0:

        action_cells = row.find_elements(
            By.CSS_SELECTOR,
            '[data-field="actions"], '
            'td:last-child, '
            '[role="gridcell"]:last-child'
        )

        if len(action_cells) != 1:

            raise AssertionError(
                "Actions column could not be identified."
            )

        buttons = action_cells[0].find_elements(
            By.CSS_SELECTOR,
            "button, [role='button']"
        )

        buttons = [
            button for button in buttons
            if button.is_displayed()
        ]

        if len(buttons) != 4:

            raise AssertionError(
                "Expected four action buttons: "
                "View, Edit, Call and Email."
            )

        email_button = buttons[3]

    else:

        raise AssertionError(
            "Multiple email buttons were found."
        )

    driver.execute_script(
        "arguments[0].scrollIntoView("
        "{block:'center', inline:'center'});",
        email_button
    )

    email_button.click()

    get_email_form()

    verify_recipient()

    print("Email compose form opened successfully.")

    return (
        f"Email compose form opened for {RECIPIENT}."
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

        containers = dropdown.find_elements(
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

                if "subject" in label.text.lower():

                    return dropdown

    if len(dropdowns) == 1:

        return dropdowns[0]

    raise AssertionError(
        "Subject dropdown could not be identified."
    )


# ==========================================
# CHECK TEMPLATE OPTION
# ==========================================

def valid_template(text):

    normalized = text.strip().lower()

    placeholders = [
        "",
        "subject",
        "select",
        "select subject",
        "select a subject",
        "select template",
        "select a template",
        "choose subject",
        "choose a subject",
        "none"
    ]

    return normalized not in placeholders


# ==========================================
# GET SELECTED SUBJECT
# ==========================================

def get_subject_value():

    dropdown = get_subject_dropdown()

    if dropdown.tag_name.lower() == "select":

        return Select(
            dropdown
        ).first_selected_option.text.strip()

    return (
        dropdown.text.strip()
        or dropdown.get_attribute("value")
        or ""
    )


# ==========================================
# STEP 2 - SELECT TEMPLATE SUBJECT
# ==========================================

def select_subject():

    global selected_subject

    dropdown = get_subject_dropdown()

    if dropdown.tag_name.lower() == "select":

        select = Select(dropdown)

        valid_options = [
            option for option in select.options
            if option.is_enabled()
            and valid_template(option.text)
        ]

        if not valid_options:

            raise AssertionError(
                "No existing email templates found."
            )

        selected_subject = (
            valid_options[0].text.strip()
        )

        select.select_by_visible_text(
            selected_subject
        )

    else:

        dropdown.click()

        def find_templates(browser):

            options = browser.find_elements(
                By.CSS_SELECTOR,
                "[role='option']"
            )

            valid_options = [
                option for option in options
                if option.is_displayed()
                and option.is_enabled()
                and option.get_attribute(
                    "aria-disabled"
                ) != "true"
                and valid_template(option.text)
            ]

            return valid_options or False

        templates = step_wait().until(
            find_templates
        )

        selected_subject = (
            templates[0].text.strip()
        )

        templates[0].click()

    step_wait().until(
        lambda d: (
            get_subject_value().strip()
            == selected_subject
        )
    )

    print(f"Selected Subject: {selected_subject}")

    return (
        f"Template subject selected: "
        f"{selected_subject}"
    )


# ==========================================
# FIND EMAIL BODY FIELD
# ==========================================

def get_body_field():

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
            and field.is_enabled()
            and field.get_attribute(
                "readonly"
            ) is None
        ]

        if len(fields) == 1:

            return fields[0]

    raise AssertionError(
        "Email body field could not be identified."
    )


# ==========================================
# GET EMAIL BODY VALUE
# ==========================================

def get_body_value():

    field = get_body_field()

    if field.get_attribute(
        "contenteditable"
    ) == "true":

        return field.text.strip()

    return (
        field.get_attribute("value") or ""
    ).strip()


# ==========================================
# STEP 3 - REPLACE EMAIL BODY
# ==========================================

def replace_email_body():

    field = get_body_field()

    field.click()

    field.send_keys(
        Keys.CONTROL,
        "a"
    )

    field.send_keys(
        Keys.BACKSPACE
    )

    field.send_keys(EMAIL_BODY)

    actual_body = get_body_value()

    if actual_body != EMAIL_BODY:

        raise AssertionError(
            "Email body verification failed."
        )

    print("Email body successfully replaced.")
    print()
    print(f"To: {RECIPIENT}")
    print(f"Subject: {selected_subject}")
    print(f"Body: {EMAIL_BODY}")

    screenshot(
        "Step_03_Email_Composed.png"
    )

    return (
        "Existing template body was replaced "
        "with the specified test message."
    )


# ==========================================
# SUCCESS MESSAGE PATTERN
# ==========================================

SUCCESS_PATTERN = (
    r"email\s+(?:has\s+been\s+)?"
    r"sent(?:\s+successfully)?"
    r"|successfully\s+sent"
    r"|sent\s+successfully"
    r"|send\s+successfully"
    r"|email\s+successfully\s+sent"
    r"|email\s+sent\s+successful"
)


# ==========================================
# INSTALL NOTIFICATION MONITOR
# ==========================================

def install_notification_monitor():

    driver.execute_script(r"""
        if (window.__tel05Observer) {
            window.__tel05Observer.disconnect();
        }

        window.__tel05Messages = [];

        const selector =
            '[role="alert"], ' +
            '[role="status"], ' +
            '.MuiAlert-message, ' +
            '.MuiSnackbar-root, ' +
            '.Toastify__toast, ' +
            '.swal2-popup';

        function inspect(node) {

            if (!node) return;

            if (node.nodeType === Node.TEXT_NODE) {

                const message =
                    node.textContent.trim();

                if (message) {
                    window.__tel05Messages.push(
                        message
                    );
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

                    window.__tel05Messages.push(
                        message
                    );
                }
            }
        }

        window.__tel05Observer =
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

        window.__tel05Observer.observe(
            document.body,
            {
                childList: true,
                subtree: true,
                characterData: true
            }
        );
    """)


# ==========================================
# GET NOTIFICATION MESSAGES
# ==========================================

def get_notification_messages():

    messages = driver.execute_script("""
        return window.__tel05Messages || [];
    """)

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "[role='alert'], "
        "[role='status'], "
        ".MuiAlert-message, "
        ".MuiSnackbar-root, "
        ".Toastify__toast, "
        ".swal2-popup"
    )

    for element in elements:

        try:

            if element.is_displayed():

                messages.append(
                    element.text.strip()
                )

        except StaleElementReferenceException:

            continue

    return messages


# ==========================================
# CHECK EMAIL FORM VALIDATION
# ==========================================

def get_validation_errors():

    form = find_visible_email_form(driver)

    if not form:

        return []

    return driver.execute_script("""
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


# ==========================================
# CHECK EMAIL SUBMISSION OUTCOME
# ==========================================

def check_send_outcome(browser):

    check_timer()

    messages = get_notification_messages()

    failure_pattern = (
        r"failed to send"
        r"|email not sent"
        r"|unable to send"
        r"|error sending"
        r"|sending failed"
        r"|could not send"
        r"|unsuccessful"
    )

    for message in messages:

        if re.search(
            failure_pattern,
            message,
            re.IGNORECASE
        ):

            return "FAILED", message

    for message in messages:

        if re.search(
            SUCCESS_PATTERN,
            message,
            re.IGNORECASE
        ):

            return "SUCCESS", message

    errors = get_validation_errors()

    if errors:

        return "VALIDATION", errors

    return False


# ==========================================
# STEP 4 - CLICK SEND
# ==========================================

def send_email():

    global email_sent
    global send_time

    verify_recipient()

    if get_subject_value() != selected_subject:

        raise AssertionError(
            "Incorrect email subject."
        )

    if get_body_value() != EMAIL_BODY:

        raise AssertionError(
            "Incorrect email body."
        )

    errors = get_validation_errors()

    if errors:

        raise AssertionError(
            f"Email form validation failed: {errors}"
        )

    form = get_email_form()

    buttons = form.find_elements(
        *SEND_BUTTON
    )

    buttons = [
        button for button in buttons
        if button.is_displayed()
        and button.is_enabled()
    ]

    if len(buttons) != 1:

        raise AssertionError(
            "SEND button could not be identified."
        )

    screenshot(
        "Step_04_Before_Send.png"
    )

    # Capture success notification before
    # clicking SEND.

    install_notification_monitor()

    send_time = datetime.now()

    buttons[0].click()

    print("SEND button clicked.")
    print("Checking email submission result...")

    # Do not automatically retry SEND.
    # Retrying could send duplicate emails.

    outcome, message = step_wait().until(
        check_send_outcome
    )

    if outcome != "SUCCESS":

        raise AssertionError(
            f"Email submission failed: {message}"
        )

    email_sent = True

    print()
    print("EMAIL SENT SUCCESSFULLY")
    print(f"Notification: {message}")
    print(f"Recipient: {RECIPIENT}")
    print(f"Subject: {selected_subject}")
    print(f"Sent At: {send_time}")

    screenshot(
        "Step_04_Email_Success_Notification.png"
    )

    return (
        f"Email submission confirmed: {message}"
    )


# ==========================================
# FIND SENT EMAIL RECORD
# ==========================================

def find_sent_email_record(browser):

    check_timer()

    rows = get_rows()

    for row in rows:

        cells = row.find_elements(
            By.CSS_SELECTOR,
            "td, [role='gridcell'], [role='cell']"
        )

        values = [
            cell.text.strip()
            for cell in cells
        ]

        recipient_found = any(
            value.lower() == RECIPIENT.lower()
            for value in values
        )

        subject_found = any(
            value == selected_subject
            for value in values
        )

        if recipient_found and subject_found:

            return row

    return False


# ==========================================
# STEP 5 - OPEN EMAILS TAB
# ==========================================

def open_emails_tab():

    global email_verified

    print("Opening Emails tab...")

    # Wait for compose modal to close.

    step_wait().until(
        lambda d: not find_visible_email_form(d)
    )

    # Use sidebar navigation instead of
    # driver.refresh() or direct route access.

    step_wait().until(
        EC.element_to_be_clickable(
            EMAILS_LINK
        )
    ).click()

    print("Emails sidebar clicked.")

    # If there is an Emails Sent tab,
    # open it automatically.

    sent_tabs = driver.find_elements(
        By.XPATH,
        "//*[self::button or @role='tab' or self::a]"
        "[translate(normalize-space(.),"
        "'abcdefghijklmnopqrstuvwxyz',"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='EMAILS SENT'"
        " or translate(normalize-space(.),"
        "'abcdefghijklmnopqrstuvwxyz',"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='SENT EMAILS']"
    )

    for tab in sent_tabs:

        if tab.is_displayed() and tab.is_enabled():

            tab.click()

            break

    print("Searching for the sent email...")

    screenshot(
        "Step_05_Emails_Page.png"
    )

    row = step_wait().until(
        find_sent_email_record
    )

    driver.execute_script(
        "arguments[0].scrollIntoView("
        "{block:'center'});",
        row
    )

    print()
    print("MATCHING EMAIL RECORD FOUND")
    print("-----------------------------------")
    print(row.text)
    print("-----------------------------------")

    # Verify that the body appears in the
    # matching sent record, if displayed.

    if EMAIL_BODY in row.text:

        print("Email body matches the test message.")

    else:

        print(
            "Email body is not visible in the list. "
            "Only recipient and subject were verified."
        )

    email_verified = True

    screenshot(
        "Step_05_Sent_Email_Record.png"
    )

    return (
        "Emails tab opened successfully. "
        "Matching recipient and subject found "
        "in the email records."
    )


# ==========================================
# MAIN TEST EXECUTION
# ==========================================

try:

    print("===================================")
    print("TC-TEL-05")
    print("SEND EMAIL")
    print(f"TIMEOUT: {TIMEOUT} SECONDS")
    print("===================================")

    # ======================================
    # PRECONDITION - AUTOMATIC LOGIN
    # ======================================

    current_step = "Precondition: Login"

    start_timer()

    login()

    # ======================================
    # PRECONDITION - OPEN ASSIGNED LEADS
    # ======================================

    current_step = "Precondition: Assigned Leads"

    start_timer()

    open_assigned_leads()

    # ======================================
    # PRECONDITION - FIND RECIPIENT LEAD
    # ======================================

    current_step = "Precondition: Recipient Lead"

    start_timer()

    find_recipient_lead()

    deadline = None

    precondition_passed = True

    # ======================================
    # STEP 1
    # CLICK EMAIL ICON
    # ======================================

    execute_step(
        1,
        "Click Email Icon on Lead Row",
        click_email_icon
    )

    # ======================================
    # STEP 2
    # SELECT TEMPLATE SUBJECT
    # ======================================

    execute_step(
        2,
        "Select Existing Template Subject",
        select_subject
    )

    # ======================================
    # STEP 3
    # REPLACE EMAIL BODY
    # ======================================

    execute_step(
        3,
        "Replace Email Body Text",
        replace_email_body
    )

    # ======================================
    # STEP 4
    # CLICK SEND
    # ======================================

    execute_step(
        4,
        "Click SEND and Verify Success",
        send_email
    )

    # ======================================
    # STEP 5
    # OPEN EMAILS TAB
    # ======================================

    execute_step(
        5,
        "Open Emails Tab and Verify Sent Email",
        open_emails_tab
    )

    screenshot(
        "Final_Test_Result.png"
    )


# ==========================================
# TIMEOUT ERROR HANDLER
# ==========================================

except TimeoutException:

    main_failed = True

    print()
    print("===================================")
    print("TC-TEL-05: FAILED")
    print("===================================")
    print(f"Failed at: {current_step}")
    print("Reason: EXECUTION TIMEOUT")
    print(f"Time Limit: {TIMEOUT} seconds")
    print("===================================")

    screenshot(
        "TC-TEL-05_FAILED_Timeout.png"
    )


# ==========================================
# GENERAL ERROR HANDLER
# ==========================================

except Exception as error:

    main_failed = True

    print()
    print("===================================")
    print("TC-TEL-05: EXECUTION STOPPED")
    print("===================================")
    print(f"Stopped at: {current_step}")
    print(f"Reason: {error}")
    print("===================================")

    screenshot(
        "TC-TEL-05_Execution_Stopped.png"
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
    print("TC-TEL-05: FINAL TEST SUMMARY")
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

    print("Total Test Steps: 5")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Timeout Failures: {timed_out}")
    print(f"Not Executed: {not_executed}")

    print("-----------------------------------")

    print(
        f"Lead ID: "
        f"{selected_lead_id or 'N/A'}"
    )

    print(
        f"Lead Name: "
        f"{selected_lead_name or 'N/A'}"
    )

    print(f"Recipient: {RECIPIENT}")

    print(
        f"Subject: "
        f"{selected_subject or 'N/A'}"
    )

    print(f"Email Body: {EMAIL_BODY}")

    print(
        "Email Send Confirmed: "
        + ("YES" if email_sent else "NO")
    )

    print(
        "Matching Email Record Found: "
        + ("YES" if email_verified else "NO")
    )

    print(
        f"Total Execution Time: "
        f"{total_execution_time:.2f} seconds"
    )

    print("-----------------------------------")

    if not precondition_passed:

        final_result = "BLOCKED"

    elif main_failed or failed > 0:

        final_result = "FAILED"

    elif passed == 5:

        final_result = "PASSED"

    else:

        final_result = "NOT FULLY VERIFIED"

    print(f"FINAL RESULT: {final_result}")

    # ======================================
    # EXPORT TEST RESULTS CSV
    # ======================================

    csv_path = os.path.join(
        EVIDENCE_FOLDER,
        "TC-TEL-05_Test_Results.csv"
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
                "Recipient",
                "Subject",
                "Status",
                "Details",
                "Execution Time (Seconds)"
            ]
        )

        writer.writeheader()

        writer.writerows(results)

    # ======================================
    # EXPORT EMAIL TEST DATA
    # ======================================

    email_csv = os.path.join(
        EVIDENCE_FOLDER,
        "TC-TEL-05_Email_Details.csv"
    )

    with open(
        email_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow([
            "Lead ID",
            "Lead Name",
            "Recipient",
            "Subject",
            "Email Body",
            "Send Time",
            "Send Confirmed",
            "Matching Record Found",
            "Final Result"
        ])

        writer.writerow([
            selected_lead_id,
            selected_lead_name,
            RECIPIENT,
            selected_subject,
            EMAIL_BODY,
            str(send_time or ""),
            "Yes" if email_sent else "No",
            "Yes" if email_verified else "No",
            final_result
        ])

    print()
    print(f"Test Results: {csv_path}")
    print(f"Email Details: {email_csv}")
    print(f"Evidence Folder: {EVIDENCE_FOLDER}")
    print("===================================")

    try:

        input(
            "\nPress Enter to close the browser..."
        )

    finally:

        driver.quit()
