
import os
import csv
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException
)

# ==========================================
# TC-TEL-03
# UPDATE LEAD WITH EMPTY REQUIRED FIELDS
# ==========================================

# LOGIN CREDENTIALS

EMAIL = "dranheirdejesus@gmail.com"
PASSWORD = "ABCabc123!"

URL = "https://sortrleaddistribution-client.onrender.com/"

# ==========================================
# TIMEOUT CONFIGURATION
# ==========================================

TIMEOUT = 120

scenario_deadline = None

# ==========================================
# DESIGNATED SELENIUM TEST LEADS
# ==========================================

TEST_LEAD_IDS = [
    "8e95",
    "5583",
    "8004"
]

used_leads = set()

# ==========================================
# AUSTRALIAN TEST DATA
# ==========================================

LEAD_NAME = "Only Drans"
LEAD_TYPE = "Hotel"

PHONE = "0491570006"

STREET = "100 Example Street"
CITY = "Sydney"
POSTCODE = "2000"

LEAD_EMAIL = "onlydrans@example.com"

CALL_DISPOSITION = "Warm Lead"

REMARKS = (
    "Interested in hotel services. "
    "Follow up next week."
)

TEST_DATA = {
    "name": LEAD_NAME,
    "type": LEAD_TYPE,
    "phonenumber": PHONE,
    "streetaddress": STREET,
    "city": CITY,
    "postcode": POSTCODE,
    "emailaddress": LEAD_EMAIL,
    "calldisposition": CALL_DISPOSITION,
    "remarks": REMARKS
}

FIELD_LABELS = {
    "name": "Lead Name",
    "type": "Type",
    "phonenumber": "Phone Number",
    "streetaddress": "Street Address",
    "city": "City",
    "postcode": "Postcode",
    "emailaddress": "Email Address",
    "calldisposition": "Call Disposition",
    "remarks": "Remarks"
}

DROPDOWN_FIELDS = [
    "type",
    "calldisposition"
]

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

results = []

current_step = "Step 1"

main_failed = False

# ==========================================
# SCREENSHOT EVIDENCE FOLDER
# ==========================================

SCREENSHOT_FOLDER = "TC-TEL-03_Evidence"

os.makedirs(
    SCREENSHOT_FOLDER,
    exist_ok=True
)

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

ASSIGNED_LEADS_TITLE = (
    By.XPATH,
    "//*[normalize-space()='ASSIGNED LEADS']"
)

UPDATE_BUTTON = (
    By.XPATH,
    ".//button["
    "translate(normalize-space(.),"
    "'abcdefghijklmnopqrstuvwxyz',"
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='UPDATE'"
    " or "
    "translate(normalize-space(.),"
    "'abcdefghijklmnopqrstuvwxyz',"
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='SEND'"
    "]"
)

ROW_SELECTOR = (
    "table tbody tr, "
    "[role='rowgroup'] [role='row'], "
    ".MuiDataGrid-row"
)

# ==========================================
# TIMER FUNCTIONS
# ==========================================

def remaining_time():

    if scenario_deadline is None:

        return TIMEOUT

    remaining = (
        scenario_deadline - time.monotonic()
    )

    if remaining <= 0:

        raise TimeoutException(
            f"Execution exceeded {TIMEOUT} seconds."
        )

    return remaining


def scenario_wait():

    return WebDriverWait(
        driver,
        remaining_time(),
        poll_frequency=0.25,
        ignored_exceptions=(
            StaleElementReferenceException,
        )
    )


def check_timer():

    remaining_time()


# ==========================================
# SCREENSHOT FUNCTION
# ==========================================

def screenshot(filename):

    path = os.path.join(
        SCREENSHOT_FOLDER,
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
    lead_id,
    status,
    reason,
    elapsed
):

    results.append({
        "Step": step,
        "Test Scenario": description,
        "Lead ID": lead_id or "N/A",
        "Status": status,
        "Details": reason,
        "Execution Time (Seconds)": round(
            elapsed,
            2
        )
    })

    print("-----------------------------------")
    print(f"STEP {step}: {status}")
    print(f"Details: {reason}")
    print(f"Execution Time: {elapsed:.2f} seconds")
    print(f"Time Limit: {TIMEOUT} seconds")
    print("-----------------------------------")


# ==========================================
# OPEN ASSIGNED LEADS PAGE
# ==========================================

def open_leads():

    scenario_wait().until(
        EC.element_to_be_clickable(
            LEADS_LINK
        )
    ).click()

    scenario_wait().until(
        EC.visibility_of_element_located(
            ASSIGNED_LEADS_TITLE
        )
    )

    scenario_wait().until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "table, [role='grid'], "
                ".MuiDataGrid-root"
            )
        )
    )

    print("Assigned Leads page opened.")


# ==========================================
# AUTOMATICALLY FIND TEST LEAD
# ==========================================

def find_test_lead():

    available_ids = [
        lead_id
        for lead_id in TEST_LEAD_IDS
        if lead_id not in used_leads
    ]

    if not available_ids:

        raise AssertionError(
            "No unused designated test leads remain."
        )

    def locate(browser):

        check_timer()

        rows = browser.find_elements(
            By.CSS_SELECTOR,
            ROW_SELECTOR
        )

        for lead_id in available_ids:

            for row in rows:

                if not row.is_displayed():

                    continue

                cells = row.find_elements(
                    By.CSS_SELECTOR,
                    "td, [role='cell'], "
                    "[role='gridcell']"
                )

                for cell in cells:

                    if cell.text.strip() == lead_id:

                        return lead_id, row

        return False

    lead_id, row = scenario_wait().until(
        locate
    )

    print(f"Automatically selected lead: {lead_id}")

    return lead_id, row


# ==========================================
# FIND UPDATE LEAD MODAL
# ==========================================

def find_visible_form(browser):

    containers = browser.find_elements(
        By.CSS_SELECTOR,
        "[role='dialog'], "
        ".MuiModal-root, "
        "form"
    )

    for container in containers:

        try:

            if not container.is_displayed():

                continue

            buttons = container.find_elements(
                *UPDATE_BUTTON
            )

            if any(
                button.is_displayed()
                for button in buttons
            ):

                return container

        except StaleElementReferenceException:

            continue

    return False


def get_form():

    return scenario_wait().until(
        find_visible_form
    )


# ==========================================
# OPEN UPDATE LEAD MODAL
# ==========================================

def open_update_lead(row):

    check_timer()

    edit_buttons = row.find_elements(
        By.XPATH,
        ".//button["
        ".//*[@data-testid='EditIcon']"
        " or .//*[@data-testid='ModeEditIcon']"
        " or .//*[@data-testid='EditOutlinedIcon']"
        " or .//*[@data-testid='ModeEditOutlineIcon']"
        " or contains("
        "translate(@aria-label,'EDIT','edit'),'edit')"
        " or contains("
        "translate(@title,'EDIT','edit'),'edit')"
        "]"
    )

    edit_buttons = [
        button
        for button in edit_buttons
        if button.is_displayed()
        and button.is_enabled()
    ]

    if len(edit_buttons) == 1:

        edit_button = edit_buttons[0]

    elif len(edit_buttons) == 0:

        # Fallback:
        # View, Edit, Call, Email

        action_cells = row.find_elements(
            By.CSS_SELECTOR,
            '[data-field="actions"], '
            'td:last-child, '
            '[role="gridcell"]:last-child'
        )

        assert len(action_cells) == 1, (
            "Could not identify Actions column."
        )

        action_buttons = action_cells[0].find_elements(
            By.CSS_SELECTOR,
            "button, [role='button']"
        )

        action_buttons = [
            button
            for button in action_buttons
            if button.is_displayed()
        ]

        assert len(action_buttons) == 4, (
            "Expected four action buttons: "
            "View, Edit, Call and Email."
        )

        edit_button = action_buttons[1]

    else:

        raise AssertionError(
            "Multiple Edit buttons detected."
        )

    driver.execute_script(
        "arguments[0].scrollIntoView("
        "{block:'center', inline:'center'});",
        edit_button
    )

    check_timer()

    edit_button.click()

    get_form()

    print("Update Lead modal opened.")


# ==========================================
# FIND TEXT INPUT FIELD
# ==========================================

def get_field(field_name):

    check_timer()

    form = get_form()

    aliases = {
        "name": [
            "name",
            "leadName",
            "leadname"
        ],
        "phonenumber": [
            "phonenumber",
            "phoneNumber",
            "phone"
        ],
        "streetaddress": [
            "streetaddress",
            "streetAddress",
            "street"
        ],
        "city": [
            "city"
        ],
        "postcode": [
            "postcode",
            "postCode",
            "postalCode"
        ],
        "emailaddress": [
            "emailaddress",
            "emailAddress",
            "email"
        ],
        "remarks": [
            "remarks",
            "remark"
        ]
    }

    for name in aliases.get(
        field_name,
        [field_name]
    ):

        fields = form.find_elements(
            By.NAME,
            name
        )

        for field in fields:

            if field.is_displayed():

                return field

    # Locate field using its label

    label_text = FIELD_LABELS[field_name]

    labels = form.find_elements(
        By.TAG_NAME,
        "label"
    )

    for label in labels:

        actual_label = (
            label.text.replace("*", "").strip()
        )

        if actual_label.lower() != label_text.lower():

            continue

        field_id = label.get_attribute("for")

        if field_id:

            fields = form.find_elements(
                By.ID,
                field_id
            )

            for field in fields:

                if field.is_displayed():

                    return field

        containers = label.find_elements(
            By.XPATH,
            "./ancestor::*[contains(@class,"
            "'MuiFormControl-root')][1]"
        )

        for container in containers:

            fields = container.find_elements(
                By.CSS_SELECTOR,
                "input, textarea"
            )

            for field in fields:

                if field.is_displayed():

                    return field

    # Remarks textarea fallback

    if field_name == "remarks":

        textareas = form.find_elements(
            By.TAG_NAME,
            "textarea"
        )

        textareas = [
            element
            for element in textareas
            if element.is_displayed()
        ]

        if len(textareas) == 1:

            return textareas[0]

    raise AssertionError(
        f"Field not found: {label_text}"
    )


# ==========================================
# NORMALIZE FIELD VALUES
# ==========================================

def normalize_value(field_name, value):

    if field_name == "phonenumber":

        return re.sub(
            r"\D",
            "",
            value
        )

    return value.strip()


# ==========================================
# ENTER OR CLEAR TEXT FIELD
# ==========================================

def set_field(field_name, value):

    check_timer()

    field = get_field(field_name)

    actual = field.get_attribute(
        "value"
    ) or ""

    if normalize_value(
        field_name,
        actual
    ) == normalize_value(
        field_name,
        value
    ):

        print(
            f"{FIELD_LABELS[field_name]}: "
            f"{actual if actual else '[EMPTY]'}"
        )

        return

    if (
        not field.is_enabled()
        or field.get_attribute("readonly") is not None
    ):

        raise AssertionError(
            f"{FIELD_LABELS[field_name]} "
            "is read-only or disabled."
        )

    driver.execute_script(
        "arguments[0].scrollIntoView("
        "{block:'center'});",
        field
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

    check_timer()

    actual = field.get_attribute(
        "value"
    ) or ""

    assert normalize_value(
        field_name,
        actual
    ) == normalize_value(
        field_name,
        value
    ), (
        f"{FIELD_LABELS[field_name]} "
        "input verification failed."
    )

    print(
        f"{FIELD_LABELS[field_name]}: "
        f"{actual if actual else '[EMPTY]'}"
    )


# ==========================================
# FIND DROPDOWN FIELD
# ==========================================

def get_dropdown(field_name):

    check_timer()

    form = get_form()

    label_text = FIELD_LABELS[field_name]

    dropdowns = form.find_elements(
        By.CSS_SELECTOR,
        "[role='combobox'], select"
    )

    dropdowns = [
        dropdown
        for dropdown in dropdowns
        if dropdown.is_displayed()
    ]

    for dropdown in dropdowns:

        attributes = " ".join([
            dropdown.get_attribute("id") or "",
            dropdown.get_attribute("name") or "",
            dropdown.get_attribute("aria-label") or "",
            dropdown.get_attribute("aria-labelledby") or ""
        ])

        normalized = re.sub(
            r"[^a-z]",
            "",
            attributes.lower()
        )

        if field_name in normalized:

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

                actual_label = (
                    label.text.replace("*", "").strip()
                )

                if actual_label.lower() == label_text.lower():

                    return dropdown

    # First dropdown: Type
    # Second dropdown: Call Disposition

    if len(dropdowns) == 2:

        if field_name == "type":

            return dropdowns[0]

        if field_name == "calldisposition":

            return dropdowns[1]

    raise AssertionError(
        f"Dropdown not found: {label_text}"
    )


# ==========================================
# GET DROPDOWN VALUE
# ==========================================

def dropdown_value(dropdown):

    if dropdown.tag_name.lower() == "select":

        selected = Select(
            dropdown
        ).first_selected_option

        if selected.get_attribute("value") == "":

            return ""

        return selected.text.strip()

    return dropdown.text.strip()


def is_empty_dropdown(value):

    return value.strip().lower() in (
        "",
        "none",
        "select",
        "type",
        "call disposition",
        "call disposition *",
        "select type",
        "select disposition",
        "select call disposition",
        "please select"
    )


# ==========================================
# SELECT OR CLEAR DROPDOWN
# ==========================================

def set_dropdown(field_name, value):

    check_timer()

    dropdown = get_dropdown(field_name)

    current = dropdown_value(dropdown)

    if value and current == value:

        print(
            f"{FIELD_LABELS[field_name]}: {value}"
        )

        return

    if not value and is_empty_dropdown(current):

        print(
            f"{FIELD_LABELS[field_name]}: [EMPTY]"
        )

        return

    if (
        not dropdown.is_enabled()
        or dropdown.get_attribute("aria-disabled") == "true"
    ):

        raise AssertionError(
            f"{FIELD_LABELS[field_name]} is disabled."
        )

    # Native HTML select

    if dropdown.tag_name.lower() == "select":

        select = Select(dropdown)

        if value:

            select.select_by_visible_text(value)

        else:

            select.select_by_value("")

    else:

        # Material UI dropdown

        dropdown.click()

        scenario_wait().until(
            EC.visibility_of_any_elements_located(
                (
                    By.CSS_SELECTOR,
                    "[role='option']"
                )
            )
        )

        options = driver.find_elements(
            By.CSS_SELECTOR,
            "[role='option']"
        )

        selected_option = None

        for option in options:

            if not option.is_displayed():

                continue

            if option.get_attribute("aria-disabled") == "true":

                continue

            if value:

                if option.text.strip() == value:

                    selected_option = option
                    break

                if option.get_attribute(
                    "data-value"
                ) == value:

                    selected_option = option
                    break

            else:

                if (
                    option.get_attribute("data-value") == ""
                    or is_empty_dropdown(option.text)
                ):

                    selected_option = option
                    break

        if selected_option is None:

            driver.switch_to.active_element.send_keys(
                Keys.ESCAPE
            )

            raise AssertionError(
                f"No selectable option for "
                f"{FIELD_LABELS[field_name]} = "
                f"{value if value else '[EMPTY]'}"
            )

        driver.execute_script(
            "arguments[0].scrollIntoView("
            "{block:'center'});",
            selected_option
        )

        selected_option.click()

    def verify(browser):

        check_timer()

        actual = dropdown_value(
            get_dropdown(field_name)
        )

        if value:

            return actual == value

        return is_empty_dropdown(actual)

    scenario_wait().until(verify)

    print(
        f"{FIELD_LABELS[field_name]}: "
        f"{value if value else '[EMPTY]'}"
    )


# ==========================================
# PREPARE FORM DATA
# ==========================================

def prepare_form(empty_fields):

    for field_name, valid_value in TEST_DATA.items():

        check_timer()

        value = (
            ""
            if field_name in empty_fields
            else valid_value
        )

        if field_name in DROPDOWN_FIELDS:

            set_dropdown(
                field_name,
                value
            )

        else:

            set_field(
                field_name,
                value
            )

    print("All test inputs prepared.")


# ==========================================
# VERIFY FORM DATA
# ==========================================

def verify_form(empty_fields):

    for field_name, valid_value in TEST_DATA.items():

        check_timer()

        expected = (
            ""
            if field_name in empty_fields
            else valid_value
        )

        if field_name in DROPDOWN_FIELDS:

            actual = dropdown_value(
                get_dropdown(field_name)
            )

            if expected:

                assert actual == expected, (
                    f"{field_name} value mismatch."
                )

            else:

                assert is_empty_dropdown(actual), (
                    f"{field_name} is not empty."
                )

        else:

            actual = get_field(
                field_name
            ).get_attribute("value") or ""

            assert normalize_value(
                field_name,
                actual
            ) == normalize_value(
                field_name,
                expected
            ), (
                f"{field_name} value mismatch."
            )

    print("All form values verified.")


# ==========================================
# NATIVE VALIDATION EVENT MONITOR
# ==========================================

def install_validation_monitor():

    driver.execute_script("""
        window.__seleniumValidationErrors = [];

        if (!window.__seleniumValidationInstalled) {

            document.addEventListener(
                'invalid',
                function(event) {

                    const field = event.target;

                    const container = field.closest(
                        '.MuiFormControl-root'
                    );

                    const label = container
                        ? container.querySelector('label')
                        : null;

                    window.__seleniumValidationErrors.push({
                        name: field.name || '',
                        id: field.id || '',
                        label: label
                            ? label.textContent.trim()
                            : '',
                        message: field.validationMessage || '',
                        valueMissing: Boolean(
                            field.validity &&
                            field.validity.valueMissing
                        )
                    });

                },
                true
            );

            window.__seleniumValidationInstalled = true;
        }
    """)


def get_native_validation_events():

    return driver.execute_script("""
        return window.__seleniumValidationErrors || [];
    """)


# ==========================================
# SUCCESS NOTIFICATION MONITOR
# ==========================================

def install_success_monitor():

    # Observe success notifications even if they
    # disappear before Selenium's next check.

    driver.execute_script("""
        if (window.__seleniumSuccessObserver) {
            window.__seleniumSuccessObserver.disconnect();
        }

        window.__seleniumSuccessMessage = '';

        const pattern =
            /^(upadate successfully|update successfully|updated successfully|successfully updated|lead updated|lead successfully updated|successfully saved|update successful|lead has been updated)[!.\\s]*$/i;

        const selector = [
            '[role="alert"]',
            '[role="status"]',
            '.MuiAlert-root',
            '.MuiAlert-message',
            '.MuiSnackbar-root',
            '.MuiSnackbarContent-message',
            '.Toastify__toast',
            '.Toastify__toast-body',
            '.swal2-popup'
        ].join(',');

        function inspect(node) {

            if (!node) return;

            if (node.nodeType === Node.TEXT_NODE) {

                const message = node.textContent.trim();

                if (pattern.test(message)) {
                    window.__seleniumSuccessMessage = message;
                }

                return;
            }

            if (node.nodeType !== Node.ELEMENT_NODE) {
                return;
            }

            const candidates = [node];

            if (node.querySelectorAll) {
                candidates.push(
                    ...node.querySelectorAll(selector)
                );
            }

            for (const element of candidates) {

                const message = (
                    element.innerText ||
                    element.textContent ||
                    ''
                ).trim();

                if (pattern.test(message)) {

                    window.__seleniumSuccessMessage = message;

                    return;
                }
            }
        }

        window.__seleniumSuccessObserver =
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

        window.__seleniumSuccessObserver.observe(
            document.body,
            {
                childList: true,
                subtree: true,
                characterData: true
            }
        );
    """)


# ==========================================
# IMPROVED VALIDATION MESSAGE DETECTION
# ==========================================

def get_validation_message(field_name):

    check_timer()

    if field_name in DROPDOWN_FIELDS:

        field = get_dropdown(field_name)

    else:

        field = get_field(field_name)

    events = get_native_validation_events()

    expected_label = re.sub(
        r"[^a-z]",
        "",
        FIELD_LABELS[field_name].lower()
    )

    field_id = field.get_attribute("id") or ""

    for event in events:

        event_attributes = " ".join([
            event.get("name", ""),
            event.get("id", ""),
            event.get("label", "")
        ])

        normalized = re.sub(
            r"[^a-z]",
            "",
            event_attributes.lower()
        )

        if (
            field_name in normalized
            or expected_label in normalized
            or (
                field_id
                and field_id == event.get("id")
            )
        ):

            if event.get("message"):

                return event["message"]

    # Check Material UI container

    containers = field.find_elements(
        By.XPATH,
        "./ancestor::*[contains(@class,"
        "'MuiFormControl-root')][1]"
    )

    for container in containers:

        inputs = container.find_elements(
            By.CSS_SELECTOR,
            "input, select, textarea"
        )

        for input_field in inputs:

            input_name = input_field.get_attribute(
                "name"
            ) or ""

            input_id = input_field.get_attribute(
                "id"
            ) or ""

            for event in events:

                same_input = (
                    input_name
                    and input_name == event.get("name")
                ) or (
                    input_id
                    and input_id == event.get("id")
                )

                if same_input and event.get("message"):

                    return event["message"]

        errors = container.find_elements(
            By.CSS_SELECTOR,
            ".MuiFormHelperText-root.Mui-error"
        )

        for error in errors:

            if (
                error.is_displayed()
                and error.text.strip()
            ):

                return error.text.strip()

    # Accessibility validation messages

    if field.get_attribute("aria-invalid") == "true":

        described_by = field.get_attribute(
            "aria-describedby"
        ) or ""

        for element_id in described_by.split():

            elements = driver.find_elements(
                By.ID,
                element_id
            )

            for element in elements:

                if (
                    element.is_displayed()
                    and element.text.strip()
                ):

                    return element.text.strip()

    return ""


# ==========================================
# UPDATED SUCCESS MESSAGE DETECTION
# FIX FOR STEP 15
# ==========================================

def get_success_message():

    check_timer()

    # Check captured notification first

    captured_message = driver.execute_script("""
        return window.__seleniumSuccessMessage || '';
    """)

    if captured_message:

        print(
            f"Success notification detected: "
            f"{captured_message}"
        )

        return captured_message

    # Check visible notification elements

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "[role='alert'], "
        "[role='status'], "
        ".MuiAlert-root, "
        ".MuiAlert-message, "
        ".MuiAlert-standardSuccess, "
        ".MuiAlert-filledSuccess, "
        ".MuiAlert-outlinedSuccess, "
        ".MuiSnackbar-root, "
        ".MuiSnackbarContent-message, "
        ".swal2-popup, "
        ".Toastify__toast, "
        ".Toastify__toast-body"
    )

    success_messages = [
        "upadate successfully",
        "update successfully",
        "updated successfully",
        "successfully updated",
        "lead updated",
        "lead successfully updated",
        "successfully saved",
        "update successful",
        "lead has been updated"
    ]

    for element in elements:

        try:

            if not element.is_displayed():

                continue

            message = element.text.strip()

            normalized_message = (
                message.lower().rstrip("!.").strip()
            )

            if normalized_message in success_messages:

                print(
                    f"Success notification detected: "
                    f"{message}"
                )

                return message

        except StaleElementReferenceException:

            continue

    # Fallback: Check visible page text

    page_text = driver.find_element(
        By.TAG_NAME,
        "body"
    ).text

    for line in page_text.splitlines():

        normalized_line = (
            line.lower().rstrip("!.").strip()
        )

        if normalized_line in success_messages:

            print(
                f"Success notification detected: "
                f"{line}"
            )

            return line.strip()

    return ""


# ==========================================
# CHECK SUBMISSION OUTCOME
# ==========================================

def check_submission(empty_fields):

    check_timer()

    # Check success notification first

    success_message = get_success_message()

    if success_message:

        return "SUCCESS", success_message

    # Check if modal is still open

    if not find_visible_form(driver):

        return False

    validation_messages = {}

    fields_to_check = (
        empty_fields
        if empty_fields
        else list(TEST_DATA.keys())
    )

    for field_name in fields_to_check:

        check_timer()

        try:

            message = get_validation_message(
                field_name
            )

        except StaleElementReferenceException:

            return False

        if message:

            validation_messages[
                FIELD_LABELS[field_name]
            ] = message

    if validation_messages:

        return (
            "VALIDATION",
            validation_messages
        )

    # Handle native required-field validation

    if empty_fields:

        events = get_native_validation_events()

        missing_events = [
            event
            for event in events
            if event.get("valueMissing")
            and event.get("message")
        ]

        # Fix for unnamed native MUI
        # Call Disposition input

        if (
            empty_fields == ["calldisposition"]
            and len(missing_events) == 1
        ):

            return (
                "VALIDATION",
                {
                    "Call Disposition":
                    missing_events[0]["message"]
                }
            )

        # All required fields empty

        if (
            len(empty_fields) == len(TEST_DATA)
            and missing_events
        ):

            return (
                "VALIDATION",
                missing_events
            )

    return False


# ==========================================
# CLOSE UPDATE MODAL
# NO PAGE REFRESH
# NO DIRECT ROUTE NAVIGATION
# ==========================================

def close_update_modal():

    print("Closing Update Lead modal...")

    if not find_visible_form(driver):

        print("Update modal already closed.")

        return

    # Attempt 1: Cancel or Close button

    form = get_form()

    close_buttons = form.find_elements(
        By.XPATH,
        ".//button["
        "normalize-space()='Cancel'"
        " or normalize-space()='Close'"
        " or @aria-label='Close'"
        " or @aria-label='close'"
        " or .//*[@data-testid='CloseIcon']"
        "]"
    )

    for button in close_buttons:

        if (
            button.is_displayed()
            and button.is_enabled()
        ):

            button.click()

            time.sleep(0.5)

            if not find_visible_form(driver):

                print(
                    "Modal closed using Close button."
                )

                return

    # Attempt 2: Escape key

    driver.switch_to.active_element.send_keys(
        Keys.ESCAPE
    )

    time.sleep(0.5)

    if not find_visible_form(driver):

        print("Modal closed using Escape key.")

        return

    # Attempt 3: Click outside modal

    backdrops = driver.find_elements(
        By.CSS_SELECTOR,
        ".MuiBackdrop-root"
    )

    for backdrop in backdrops:

        if backdrop.is_displayed():

            width = backdrop.size["width"]
            height = backdrop.size["height"]

            ActionChains(driver).move_to_element_with_offset(
                backdrop,
                int(-width / 2 + 20),
                int(-height / 2 + 20)
            ).click().perform()

            time.sleep(0.5)

            if not find_visible_form(driver):

                print("Modal closed using backdrop.")

                return

    # Wait for modal dismissal

    scenario_wait().until(
        lambda d: not find_visible_form(d)
    )

    print("Update Lead modal closed.")


# ==========================================
# RESET FOR NEXT SCENARIO
# STAY ON ASSIGNED LEADS PAGE
# ==========================================

def reset_page():

    print()
    print("Preparing for next test scenario...")

    # No driver.refresh()
    # No driver.get('/AgentLeads')

    close_update_modal()

    scenario_wait().until(
        EC.visibility_of_element_located(
            ASSIGNED_LEADS_TITLE
        )
    )

    scenario_wait().until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "table, [role='grid'], "
                ".MuiDataGrid-root"
            )
        )
    )

    print("Still on Assigned Leads page.")
    print("Ready for next test scenario.")


# ==========================================
# EXECUTE INDIVIDUAL TEST SCENARIO
# ==========================================

def run_scenario(
    step,
    description,
    empty_fields
):

    global scenario_deadline

    start_time = time.monotonic()

    scenario_deadline = start_time + TIMEOUT

    lead_id = None
    submitted = False

    status = "BLOCKED"
    reason = ""

    print()
    print("===================================")
    print(f"STEP {step}: {description}")
    print(f"TIME LIMIT: {TIMEOUT} SECONDS")
    print("===================================")

    try:

        # Close previous Update Lead modal

        reset_page()

        # Automatically select test lead

        lead_id, row = find_test_lead()

        print(f"Testing Lead ID: {lead_id}")

        # Click Edit icon

        open_update_lead(row)

        # Fill required fields

        prepare_form(empty_fields)

        # Verify all test input values

        verify_form(empty_fields)

        # Capture evidence before submission

        screenshot(
            f"Step_{step}_Before_Update.png"
        )

        check_timer()

        form = get_form()

        buttons = form.find_elements(
            *UPDATE_BUTTON
        )

        buttons = [
            button
            for button in buttons
            if button.is_displayed()
        ]

        assert len(buttons) == 1, (
            "Could not identify a unique Update button."
        )

        update_button = buttons[0]

        driver.execute_script(
            "arguments[0].scrollIntoView("
            "{block:'center'});",
            update_button
        )

        check_timer()

        # Check disabled Update button

        if not update_button.is_enabled():

            if empty_fields:

                status = "PASSED"

                reason = (
                    "Update button disabled with "
                    "empty required fields."
                )

            else:

                status = "FAILED"

                reason = (
                    "Update button disabled despite "
                    "valid required information."
                )

        else:

            # Monitor native validation events

            install_validation_monitor()

            # Monitor success notifications
            # before clicking UPDATE

            install_success_monitor()

            submitted = True

            update_button.click()

            print("UPDATE button clicked.")
            print("Checking submission result...")

            outcome, message = scenario_wait().until(
                lambda d: check_submission(
                    empty_fields
                )
            )

            # NEGATIVE TEST SCENARIOS

            if empty_fields:

                if outcome == "SUCCESS":

                    status = "FAILED"

                    reason = (
                        "DEFECT FOUND: Update accepted "
                        "despite empty required fields. "
                        f"{message}"
                    )

                    used_leads.add(lead_id)

                elif outcome == "VALIDATION":

                    status = "PASSED"

                    reason = (
                        "Update prevented. "
                        f"Validation: {message}"
                    )

            # POSITIVE TEST SCENARIO

            else:

                if outcome == "SUCCESS":

                    status = "PASSED"

                    reason = (
                        f"Update successful: {message}"
                    )

                    used_leads.add(lead_id)

                elif outcome == "VALIDATION":

                    status = "FAILED"

                    reason = (
                        "Valid update rejected. "
                        f"Validation: {message}"
                    )

        check_timer()

    # ==========================================
    # TIMEOUT HANDLER
    # ==========================================

    except TimeoutException:

        status = "FAILED"

        reason = (
            "TIMEOUT: Test scenario did not complete "
            f"within {TIMEOUT} seconds."
        )

        if submitted and lead_id:

            used_leads.add(lead_id)

        print()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"STEP {step}: FAILED")
        print("REASON: EXECUTION TIMEOUT")
        print(f"TIME LIMIT: {TIMEOUT} SECONDS")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    # ==========================================
    # OTHER AUTOMATION ERRORS
    # ==========================================

    except Exception as error:

        status = "BLOCKED"

        reason = str(error)

        if submitted and lead_id:

            used_leads.add(lead_id)

    finally:

        elapsed = (
            time.monotonic() - start_time
        )

        scenario_deadline = None

        if elapsed >= TIMEOUT:

            status = "FAILED"

            reason = (
                f"TIMEOUT: Execution exceeded "
                f"{TIMEOUT} seconds."
            )

            if submitted and lead_id:

                used_leads.add(lead_id)

        # Record result

        record_result(
            step,
            description,
            lead_id,
            status,
            reason,
            elapsed
        )

        # Capture screenshot evidence

        if status == "FAILED" and "TIMEOUT" in reason:

            screenshot(
                f"Step_{step}_FAILED_Timeout.png"
            )

        else:

            screenshot(
                f"Step_{step}_{status}.png"
            )

        if step != 15:

            print("Proceeding to next scenario...")


# ==========================================
# EXECUTE LOGIN AND NAVIGATION STEPS
# ==========================================

def run_setup_step(
    step,
    description,
    action
):

    global scenario_deadline
    global current_step

    current_step = (
        f"Step {step}: {description}"
    )

    start_time = time.monotonic()

    scenario_deadline = start_time + TIMEOUT

    status = "PASSED"
    reason = ""

    print()
    print("===================================")
    print(current_step)
    print("===================================")

    try:

        action()

        check_timer()

        reason = "Step completed successfully."

    except TimeoutException:

        status = "FAILED"

        reason = (
            f"TIMEOUT: Step exceeded "
            f"{TIMEOUT} seconds."
        )

    except Exception as error:

        status = "FAILED"

        reason = str(error)

    finally:

        elapsed = (
            time.monotonic() - start_time
        )

        scenario_deadline = None

        if elapsed >= TIMEOUT:

            status = "FAILED"

            reason = (
                f"TIMEOUT: Step exceeded "
                f"{TIMEOUT} seconds."
            )

        record_result(
            step,
            description,
            None,
            status,
            reason,
            elapsed
        )

        screenshot(
            f"Step_{step:02d}_{status}.png"
        )

    return status == "PASSED"


# ==========================================
# STEP 1: OPEN LOGIN PAGE
# ==========================================

def step_1():

    driver.get(URL)

    scenario_wait().until(
        EC.visibility_of_element_located(
            EMAIL_FIELD
        )
    )

    print("Login page opened.")


# ==========================================
# STEP 2: ENTER REGISTERED EMAIL
# ==========================================

def step_2():

    email_field = scenario_wait().until(
        EC.visibility_of_element_located(
            EMAIL_FIELD
        )
    )

    email_field.clear()

    email_field.send_keys(EMAIL)

    assert email_field.get_attribute(
        "value"
    ) == EMAIL

    print("Registered Telemarketer email entered.")


# ==========================================
# STEP 3: ENTER VALID PASSWORD
# ==========================================

def step_3():

    password_field = scenario_wait().until(
        EC.visibility_of_element_located(
            PASSWORD_FIELD
        )
    )

    password_field.clear()

    password_field.send_keys(PASSWORD)

    assert password_field.get_attribute(
        "value"
    ) == PASSWORD

    print("Valid password entered.")


# ==========================================
# STEP 4: CLICK LOG IN
# ==========================================

def step_4():

    login_button = scenario_wait().until(
        EC.element_to_be_clickable(
            LOGIN_BUTTON
        )
    )

    login_button.click()

    scenario_wait().until(
        EC.element_to_be_clickable(
            LEADS_LINK
        )
    )

    print("Login successful.")


# ==========================================
# STEP 5: CLICK LEADS SIDEBAR
# ==========================================

def step_5():

    open_leads()


# ==========================================
# MAIN TEST EXECUTION
# ==========================================

test_start_time = time.monotonic()

try:

    print("===================================")
    print("TC-TEL-03")
    print("UPDATE LEAD WITH EMPTY REQUIRED FIELDS")
    print(f"TIMEOUT: {TIMEOUT} SECONDS")
    print("===================================")

    # ==========================================
    # STEP 1
    # ==========================================

    if not run_setup_step(
        1,
        "Open Login Page",
        step_1
    ):

        raise RuntimeError(
            "Step 1 failed."
        )

    # ==========================================
    # STEP 2
    # ==========================================

    if not run_setup_step(
        2,
        "Enter Registered Telemarketer Email",
        step_2
    ):

        raise RuntimeError(
            "Step 2 failed."
        )

    # ==========================================
    # STEP 3
    # ==========================================

    if not run_setup_step(
        3,
        "Enter Valid Password",
        step_3
    ):

        raise RuntimeError(
            "Step 3 failed."
        )

    # ==========================================
    # STEP 4
    # ==========================================

    if not run_setup_step(
        4,
        "Click Log In",
        step_4
    ):

        raise RuntimeError(
            "Step 4 failed."
        )

    # ==========================================
    # STEP 5
    # ==========================================

    if not run_setup_step(
        5,
        "Open Assigned Leads",
        step_5
    ):

        raise RuntimeError(
            "Step 5 failed."
        )

    # ==========================================
    # STEP 6: EMPTY LEAD NAME
    # ==========================================

    current_step = "Step 6: Empty Lead Name"

    run_scenario(
        6,
        "Empty Lead Name",
        ["name"]
    )

    # ==========================================
    # STEP 7: EMPTY PHONE NUMBER
    # ==========================================

    current_step = "Step 7: Empty Phone Number"

    run_scenario(
        7,
        "Empty Phone Number",
        ["phonenumber"]
    )

    # ==========================================
    # STEP 8: EMPTY STREET ADDRESS
    # ==========================================

    current_step = "Step 8: Empty Street Address"

    run_scenario(
        8,
        "Empty Street Address",
        ["streetaddress"]
    )

    # ==========================================
    # STEP 9: EMPTY CITY
    # ==========================================

    current_step = "Step 9: Empty City"

    run_scenario(
        9,
        "Empty City",
        ["city"]
    )

    # ==========================================
    # STEP 10: EMPTY POSTCODE
    # ==========================================

    current_step = "Step 10: Empty Postcode"

    run_scenario(
        10,
        "Empty Postcode",
        ["postcode"]
    )

    # ==========================================
    # STEP 11: EMPTY EMAIL ADDRESS
    # ==========================================

    current_step = "Step 11: Empty Email Address"

    run_scenario(
        11,
        "Empty Email Address",
        ["emailaddress"]
    )

    # ==========================================
    # STEP 12: EMPTY CALL DISPOSITION
    # ==========================================

    current_step = "Step 12: Empty Call Disposition"

    run_scenario(
        12,
        "Empty Call Disposition",
        ["calldisposition"]
    )

    # ==========================================
    # STEP 13: EMPTY REMARKS
    # ==========================================

    current_step = "Step 13: Empty Remarks"

    run_scenario(
        13,
        "Empty Remarks",
        ["remarks"]
    )

    # ==========================================
    # STEP 14: ALL REQUIRED FIELDS EMPTY
    # ==========================================

    current_step = "Step 14: All Required Fields Empty"

    run_scenario(
        14,
        "All Required Fields Empty",
        [
            "name",
            "type",
            "phonenumber",
            "streetaddress",
            "city",
            "postcode",
            "emailaddress",
            "calldisposition",
            "remarks"
        ]
    )

    # ==========================================
    # STEP 15: ALL FIELDS VALID
    # ==========================================

    current_step = "Step 15: All Fields Valid"

    run_scenario(
        15,
        "All Fields Valid",
        []
    )

    screenshot(
        "Final_Test_Result.png"
    )

# ==========================================
# MAIN TIMEOUT HANDLER
# ==========================================

except TimeoutException:

    main_failed = True

    print()
    print("===================================")
    print("TC-TEL-03: TEST FAILED")
    print("===================================")
    print(f"Failed at: {current_step}")
    print("Reason: EXECUTION TIMEOUT")
    print(f"Time Limit: {TIMEOUT} seconds")
    print("===================================")

    screenshot(
        "Test_FAILED_Timeout.png"
    )

# ==========================================
# MAIN AUTOMATION ERROR HANDLER
# ==========================================

except Exception as error:

    main_failed = True

    print()
    print("===================================")
    print("TC-TEL-03: TEST FAILED")
    print("===================================")
    print(f"Failed at: {current_step}")
    print(f"Error: {error}")
    print("===================================")

    screenshot(
        "Unexpected_Error.png"
    )

# ==========================================
# FINAL TEST SUMMARY
# ==========================================

finally:

    total_execution_time = (
        time.monotonic() - test_start_time
    )

    print()
    print("===================================")
    print("TC-TEL-03: FINAL TEST SUMMARY")
    print("===================================")

    for result in results:

        print(
            f"Step {result['Step']}: "
            f"{result['Test Scenario']}"
        )

        print(
            f"Lead ID: {result['Lead ID']}"
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

    not_executed = 15 - len(results)

    print("===================================")
    print("TOTAL TEST RESULTS")
    print("===================================")

    print("Total Test Steps: 15")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Blocked: {blocked}")
    print(f"Timeout Failures: {timed_out}")
    print(f"Not Executed: {not_executed}")

    print(
        f"Total Execution Time: "
        f"{total_execution_time:.2f} seconds"
    )

    print("-----------------------------------")

    if failed > 0 or main_failed:

        final_result = "FAILED"

    elif passed == 15:

        final_result = "PASSED"

    else:

        final_result = "NOT FULLY VERIFIED"

    print(f"FINAL RESULT: {final_result}")

    # ==========================================
    # EXPORT CSV REPORT
    # ==========================================

    csv_path = os.path.join(
        SCREENSHOT_FOLDER,
        "TC-TEL-03_Test_Results.csv"
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
    print(f"Results exported to: {csv_path}")
    print(f"Evidence folder: {SCREENSHOT_FOLDER}")
    print("===================================")

    # Keep browser open for final inspection

    try:

        input(
            "\nPress Enter to close the browser..."
        )

    finally:

        driver.quit()
