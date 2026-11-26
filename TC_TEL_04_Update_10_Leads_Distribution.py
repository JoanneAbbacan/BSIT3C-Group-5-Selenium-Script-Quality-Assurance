
import os
import csv
import re
import time

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
# TC-TEL-04
# UPDATE 10 LEADS X DISTRIBUTION
# ==========================================

URL = "https://sortrleaddistribution-client.onrender.com/"

EMAIL = "dranheirdejesus@gmail.com"
PASSWORD = "ABCabc123!"

TIMEOUT = 120

EXPECTED_LEADS = 10

CALL_DISPOSITION = "Do Not Call"
REMARKS = "Test batch"

# Add approved test lead IDs here if their names
# do not begin with "Selenium Test Lead".
APPROVED_TEST_IDS = {
    "8e95",
    "5583",
    "8004"
}

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

original_leads = []
updated_leads = []
new_leads = []

deadline = None
current_step = "Precondition"

test_start = time.monotonic()

# ==========================================
# SCREENSHOT EVIDENCE
# ==========================================

EVIDENCE_FOLDER = "TC-TEL-04_Evidence"

os.makedirs(
    EVIDENCE_FOLDER,
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

ASSIGNED_TITLE = (
    By.XPATH,
    "//*[normalize-space()='ASSIGNED LEADS']"
)

ARCHIVED_BUTTON = (
    By.XPATH,
    "//button[contains("
    "translate(normalize-space(.),"
    "'abcdefghijklmnopqrstuvwxyz',"
    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),"
    "'ARCHIVED LEADS')]"
)

UPDATE_BUTTON = (
    By.XPATH,
    ".//button[normalize-space()='UPDATE'"
    " or normalize-space()='Update']"
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

    deadline = time.monotonic() + TIMEOUT

    return time.monotonic()


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
    lead_id,
    status,
    details,
    elapsed
):

    results.append({
        "Step": step,
        "Test Scenario": description,
        "Lead ID": lead_id or "N/A",
        "Status": status,
        "Details": details,
        "Execution Time (Seconds)": round(elapsed, 2)
    })

    print("-----------------------------------")
    print(f"STEP {step}: {status}")
    print(f"Lead ID: {lead_id or 'N/A'}")
    print(f"Details: {details}")
    print(f"Execution Time: {elapsed:.2f} seconds")
    print(f"Time Limit: {TIMEOUT} seconds")
    print("-----------------------------------")

    screenshot(
        f"Step_{step:02d}_{status}.png"
    )


# ==========================================
# GENERIC STEP EXECUTION
# ==========================================

def execute_step(
    step,
    description,
    action,
    lead_id=None
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
            lead_id,
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

    print()
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

    screenshot("Precondition_Login_Success.png")


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
# GET CELL VALUE
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

    return None


# ==========================================
# EXTRACT LEAD INFORMATION
# ==========================================

def extract_lead(row):

    lead_id = get_cell_value(
        row,
        ["id", "leadid"]
    )

    name = get_cell_value(
        row,
        ["name", "leadname"]
    )

    disposition = get_cell_value(
        row,
        ["calldisposition", "disposition"]
    )

    remarks = get_cell_value(
        row,
        ["remarks", "remark"]
    )

    # Fallback: visible column order

    cells = row.find_elements(
        By.CSS_SELECTOR,
        "td, [role='gridcell'], [role='cell']"
    )

    data_cells = []

    for cell in cells:

        checkboxes = cell.find_elements(
            By.CSS_SELECTOR,
            "input[type='checkbox'], [role='checkbox']"
        )

        if not checkboxes:

            data_cells.append(cell)

    if lead_id is None and len(data_cells) >= 1:

        lead_id = data_cells[0].text.strip()

    if name is None and len(data_cells) >= 2:

        name = data_cells[1].text.strip()

    return {
        "id": lead_id or "",
        "name": name or "",
        "disposition": disposition,
        "remarks": remarks
    }


# ==========================================
# GET TABLE LEADS
# ==========================================

def get_table_leads():

    leads = []

    seen_ids = set()

    for row in get_rows():

        lead = extract_lead(row)

        if (
            lead["id"]
            and lead["id"] not in seen_ids
        ):

            leads.append(lead)

            seen_ids.add(lead["id"])

    return leads


# ==========================================
# GET TOTAL LEAD COUNT
# ==========================================

def get_total_count():

    pagination = driver.find_elements(
        By.CSS_SELECTOR,
        ".MuiTablePagination-displayedRows, "
        ".MuiDataGrid-footerContainer"
    )

    for element in pagination:

        if not element.is_displayed():

            continue

        text = element.text.strip()

        match = re.search(
            r"\bof\s+([\d,]+)\b",
            text,
            re.IGNORECASE
        )

        if match:

            return int(
                match.group(1).replace(",", "")
            )

    return None


# ==========================================
# VERIFY INITIAL BATCH
# ==========================================

def verify_initial_batch():

    global original_leads

    print()
    print("Checking initial assigned leads...")

    original_leads = step_wait().until(
        lambda d: get_table_leads() or False
    )

    total = step_wait().until(
        lambda d: (
            get_total_count()
            if get_total_count() is not None
            else False
        )
    )

    print(f"Initial assigned lead count: {total}")

    screenshot(
        "Precondition_Initial_Lead_Count.png"
    )

    if total != EXPECTED_LEADS:

        raise RuntimeError(
            f"PRECONDITION FAILED: Expected "
            f"{EXPECTED_LEADS} active leads, "
            f"but found {total}."
        )

    if len(original_leads) != EXPECTED_LEADS:

        raise RuntimeError(
            "Could not read all 10 lead rows. "
            "Set Rows per page to at least 10."
        )

    # Only modify designated test records.

    for lead in original_leads:

        approved = (
            lead["id"] in APPROVED_TEST_IDS
            or lead["name"].lower().startswith(
                "selenium test lead"
            )
        )

        if not approved:

            raise RuntimeError(
                "PRECONDITION FAILED: "
                f"Lead {lead['id']} - "
                f"{lead['name']} is not identified "
                "as an approved test record."
            )

    print()
    print("ORIGINAL BATCH OF 10 LEADS")

    for index, lead in enumerate(
        original_leads,
        start=1
    ):

        print(
            f"{index}. ID: {lead['id']} | "
            f"Name: {lead['name']}"
        )

    print("Initial batch verification: PASSED")


# ==========================================
# FIND ORIGINAL LEAD BY ID
# ==========================================

def find_lead_row(lead_id):

    def locate(browser):

        check_timer()

        for row in get_rows():

            lead = extract_lead(row)

            if lead["id"] == lead_id:

                return row

        return False

    return step_wait().until(locate)


# ==========================================
# FIND UPDATE LEAD MODAL
# ==========================================

def find_visible_form(browser):

    containers = browser.find_elements(
        By.CSS_SELECTOR,
        "[role='dialog'], .MuiModal-root, form"
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

    return step_wait().until(
        find_visible_form
    )


# ==========================================
# CLICK EDIT ICON
# ==========================================

def open_update_lead(lead_id):

    check_timer()

    row = find_lead_row(lead_id)

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
        button for button in edit_buttons
        if button.is_displayed()
        and button.is_enabled()
    ]

    if len(edit_buttons) == 1:

        edit_button = edit_buttons[0]

    elif len(edit_buttons) == 0:

        action_cells = row.find_elements(
            By.CSS_SELECTOR,
            '[data-field="actions"], '
            'td:last-child, '
            '[role="gridcell"]:last-child'
        )

        if len(action_cells) != 1:

            raise AssertionError(
                "Could not identify Actions column."
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
                "Expected four action buttons."
            )

        # View, Edit, Call, Email

        edit_button = buttons[1]

    else:

        raise AssertionError(
            "Multiple Edit buttons found."
        )

    driver.execute_script(
        "arguments[0].scrollIntoView("
        "{block:'center', inline:'center'});",
        edit_button
    )

    edit_button.click()

    get_form()

    print(f"Lead ID: {lead_id}")
    print("Update Lead modal opened.")

    return "Update Lead modal opened successfully."


# ==========================================
# FIND CALL DISPOSITION DROPDOWN
# ==========================================

def get_disposition_dropdown():

    form = get_form()

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
            dropdown.get_attribute("id") or "",
            dropdown.get_attribute("name") or "",
            dropdown.get_attribute("aria-label") or "",
            dropdown.get_attribute(
                "aria-labelledby"
            ) or ""
        ])

        normalized = re.sub(
            r"[^a-z]",
            "",
            attributes.lower()
        )

        if "calldisposition" in normalized:

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

                if "call disposition" in label.text.lower():

                    return dropdown

    # First dropdown: Type
    # Second dropdown: Call Disposition

    if len(dropdowns) == 2:

        return dropdowns[1]

    raise AssertionError(
        "Call Disposition dropdown not found."
    )


# ==========================================
# GET SELECTED CALL DISPOSITION
# ==========================================

def get_disposition_value():

    dropdown = get_disposition_dropdown()

    if dropdown.tag_name.lower() == "select":

        return Select(
            dropdown
        ).first_selected_option.text.strip()

    return dropdown.text.strip()


# ==========================================
# SELECT DO NOT CALL
# ==========================================

def select_call_disposition():

    check_timer()

    dropdown = get_disposition_dropdown()

    if get_disposition_value() == CALL_DISPOSITION:

        return f"Call Disposition: {CALL_DISPOSITION}"

    if dropdown.tag_name.lower() == "select":

        Select(dropdown).select_by_visible_text(
            CALL_DISPOSITION
        )

    else:

        dropdown.click()

        def find_option(browser):

            options = browser.find_elements(
                By.CSS_SELECTOR,
                "[role='option']"
            )

            for option in options:

                if (
                    option.is_displayed()
                    and option.text.strip()
                    == CALL_DISPOSITION
                ):

                    return option

            return False

        option = step_wait().until(
            find_option
        )

        option.click()

    step_wait().until(
        lambda d: (
            get_disposition_value()
            == CALL_DISPOSITION
        )
    )

    print(f"Call Disposition: {CALL_DISPOSITION}")

    return f"Call Disposition selected: {CALL_DISPOSITION}"


# ==========================================
# FIND REMARKS FIELD
# ==========================================

def get_remarks_field():

    form = get_form()

    for name in ["remarks", "remark"]:

        fields = form.find_elements(
            By.NAME,
            name
        )

        for field in fields:

            if field.is_displayed():

                return field

    textareas = form.find_elements(
        By.TAG_NAME,
        "textarea"
    )

    textareas = [
        field for field in textareas
        if field.is_displayed()
    ]

    if len(textareas) == 1:

        return textareas[0]

    raise AssertionError(
        "Remarks field not found."
    )


# ==========================================
# ENTER REMARKS
# ==========================================

def enter_remarks():

    check_timer()

    field = get_remarks_field()

    field.click()

    field.send_keys(
        Keys.CONTROL,
        "a"
    )

    field.send_keys(
        Keys.BACKSPACE
    )

    field.send_keys(REMARKS)

    actual = field.get_attribute(
        "value"
    ) or ""

    if actual != REMARKS:

        raise AssertionError(
            "Remarks input verification failed."
        )

    print(f"Remarks: {REMARKS}")

    return f"Remarks entered: {REMARKS}"


# ==========================================
# INSTALL SUCCESS NOTIFICATION MONITOR
# ==========================================

def install_success_monitor():

    driver.execute_script(r"""
        if (window.__tel04Observer) {
            window.__tel04Observer.disconnect();
        }

        window.__tel04Success = '';

        const pattern =
            /^(upadate successfully|update successfully|updated successfully|successfully updated|lead updated|lead successfully updated|lead has been updated|update successful)[!.\s]*$/i;

        function inspect(node) {

            if (!node) return;

            if (node.nodeType === Node.TEXT_NODE) {

                const message = node.textContent.trim();

                if (pattern.test(message)) {
                    window.__tel04Success = message;
                }

                return;
            }

            if (node.nodeType !== Node.ELEMENT_NODE) {
                return;
            }

            const elements = [
                node,
                ...node.querySelectorAll(
                    '[role="alert"], ' +
                    '[role="status"], ' +
                    '.MuiAlert-message, ' +
                    '.MuiSnackbar-root, ' +
                    '.Toastify__toast, ' +
                    '.swal2-popup'
                )
            ];

            for (const element of elements) {

                const message = (
                    element.innerText ||
                    element.textContent ||
                    ''
                ).trim();

                if (pattern.test(message)) {

                    window.__tel04Success = message;

                    return;
                }
            }
        }

        window.__tel04Observer =
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

        window.__tel04Observer.observe(
            document.body,
            {
                childList: true,
                subtree: true,
                characterData: true
            }
        );
    """)


# ==========================================
# GET SUCCESS MESSAGE
# ==========================================

def get_success_message():

    check_timer()

    captured = driver.execute_script("""
        return window.__tel04Success || '';
    """)

    if captured:

        return captured

    success_messages = [
        "upadate successfully",
        "update successfully",
        "updated successfully",
        "successfully updated",
        "lead updated",
        "lead successfully updated",
        "lead has been updated",
        "update successful"
    ]

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "[role='alert'], "
        "[role='status'], "
        ".MuiAlert-root, "
        ".MuiAlert-message, "
        ".MuiSnackbar-root, "
        ".MuiSnackbarContent-message, "
        ".Toastify__toast, "
        ".Toastify__toast-body, "
        ".swal2-popup"
    )

    for element in elements:

        try:

            if not element.is_displayed():

                continue

            message = element.text.strip()

            normalized = (
                message.lower().rstrip("!.").strip()
            )

            if normalized in success_messages:

                return message

        except StaleElementReferenceException:

            continue

    return False


# ==========================================
# CHECK FORM VALIDATION
# ==========================================

def get_validation_errors():

    form = find_visible_form(driver)

    if not form:

        return []

    errors = driver.execute_script("""
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

    return errors


# ==========================================
# VERIFY SUBMISSION OUTCOME
# ==========================================

def check_update_outcome(browser):

    check_timer()

    success = get_success_message()

    if success:

        return "SUCCESS", success

    errors = get_validation_errors()

    if errors:

        return "VALIDATION", errors

    return False


# ==========================================
# CLICK UPDATE AND VERIFY SUCCESS
# ==========================================

def submit_update(lead_id):

    check_timer()

    if get_disposition_value() != CALL_DISPOSITION:

        raise AssertionError(
            "Incorrect Call Disposition."
        )

    if get_remarks_field().get_attribute(
        "value"
    ) != REMARKS:

        raise AssertionError(
            "Incorrect Remarks."
        )

    screenshot(
        f"Lead_{lead_id}_Before_Update.png"
    )

    form = get_form()

    buttons = form.find_elements(
        *UPDATE_BUTTON
    )

    buttons = [
        button for button in buttons
        if button.is_displayed()
    ]

    if len(buttons) != 1:

        raise AssertionError(
            "Could not identify UPDATE button."
        )

    update_button = buttons[0]

    if not update_button.is_enabled():

        raise AssertionError(
            "UPDATE button is disabled."
        )

    # Ensure an old notification is not mistaken
    # for the result of the current update.

    driver.execute_script("""
        window.__tel04Success = '';
    """)

    step_wait().until(
        lambda d: not get_success_message()
    )

    install_success_monitor()

    update_button.click()

    print("UPDATE button clicked.")
    print("Checking submission result...")

    outcome, message = step_wait().until(
        check_update_outcome
    )

    if outcome != "SUCCESS":

        raise AssertionError(
            f"Update rejected: {message}"
        )

    print(
        f"Success notification detected: {message}"
    )

    screenshot(
        f"Lead_{lead_id}_Success_Notification.png"
    )

    # Wait for Update Lead modal to close.
    # No page refresh or direct URL navigation.

    step_wait().until(
        lambda d: not find_visible_form(d)
    )

    # Confirm the completed lead disappears
    # from the Assigned Leads table.

    step_wait().until(
        lambda d: all(
            lead["id"] != lead_id
            for lead in get_table_leads()
        )
    )

    if lead_id not in updated_leads:

        updated_leads.append(lead_id)

    print(f"Lead {lead_id} successfully updated.")
    print("Lead removed from Assigned Leads.")

    print(
        f"Completed Leads: "
        f"{len(updated_leads)}/{EXPECTED_LEADS}"
    )

    screenshot(
        f"Lead_{lead_id}_Removed_From_Assigned.png"
    )

    return (
        f"{message} | Lead {lead_id} "
        "removed from Assigned Leads."
    )


# ==========================================
# COMPLETE UPDATE FOR LEADS 2 TO 10
# ==========================================

def update_complete_lead(lead_id):

    open_update_lead(lead_id)

    select_call_disposition()

    enter_remarks()

    return submit_update(lead_id)


# ==========================================
# STEP 14: VERIFY NEW DISTRIBUTION
# ==========================================

def verify_new_distribution():

    global new_leads

    print()
    print("Checking automatic lead distribution...")

    if len(updated_leads) != EXPECTED_LEADS:

        raise AssertionError(
            "Not all original 10 leads were updated."
        )

    original_ids = {
        lead["id"]
        for lead in original_leads
    }

    def check_new_batch(browser):

        check_timer()

        current_leads = get_table_leads()

        current_total = get_total_count()

        if current_total != EXPECTED_LEADS:

            return False

        if len(current_leads) != EXPECTED_LEADS:

            return False

        current_ids = {
            lead["id"]
            for lead in current_leads
        }

        if len(current_ids) != EXPECTED_LEADS:

            return False

        # Verify that none of the original
        # ten leads are in the new batch.

        if original_ids.intersection(current_ids):

            return False

        return current_leads

    new_leads = step_wait().until(
        check_new_batch
    )

    print()
    print("===================================")
    print("NEW BATCH SUCCESSFULLY DISTRIBUTED")
    print("===================================")

    print(f"Original Lead Count: {len(original_leads)}")
    print(f"Completed Leads: {len(updated_leads)}")
    print(f"New Lead Count: {len(new_leads)}")

    print()
    print("NEWLY DISTRIBUTED LEADS")

    for index, lead in enumerate(
        new_leads,
        start=1
    ):

        print(
            f"{index}. ID: {lead['id']} | "
            f"Name: {lead['name']}"
        )

    screenshot(
        "Step_14_New_Batch_Distribution.png"
    )

    return (
        "A new batch of 10 unique leads was "
        "automatically distributed. No original "
        "lead IDs were included in the new batch."
    )


# ==========================================
# GET ARCHIVED LEADS TABLE
# ==========================================

def get_archive_container():

    dialogs = driver.find_elements(
        By.CSS_SELECTOR,
        "[role='dialog'], .MuiModal-root"
    )

    for dialog in dialogs:

        if not dialog.is_displayed():

            continue

        if "ARCHIVED LEADS" in dialog.text.upper():

            grids = dialog.find_elements(
                By.CSS_SELECTOR,
                ".MuiDataGrid-root, table, [role='grid']"
            )

            if grids:

                return dialog

    headings = driver.find_elements(
        By.XPATH,
        "//*[self::h1 or self::h2 or self::h3 "
        "or self::h4 or self::h5 or self::h6]"
        "[translate(normalize-space(.),"
        "'abcdefghijklmnopqrstuvwxyz',"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='ARCHIVED LEADS']"
    )

    if any(
        heading.is_displayed()
        for heading in headings
    ):

        grids = driver.find_elements(
            By.CSS_SELECTOR,
            ".MuiDataGrid-root, table, [role='grid']"
        )

        grids = [
            grid for grid in grids
            if grid.is_displayed()
        ]

        if len(grids) == 1:

            return grids[0]

    return False


# ==========================================
# GET ARCHIVED LEAD RECORDS
# ==========================================

def read_archived_leads(container):

    rows = container.find_elements(
        By.CSS_SELECTOR,
        ROW_SELECTOR
    )

    archived = {}

    for row in rows:

        if not row.is_displayed():

            continue

        lead = extract_lead(row)

        if lead["id"]:

            archived[lead["id"]] = lead

    return archived


# ==========================================
# FIND ARCHIVE NEXT PAGE BUTTON
# ==========================================

def find_archive_next_button(container):

    buttons = container.find_elements(
        By.CSS_SELECTOR,
        'button[aria-label="Go to next page"], '
        'button[aria-label="Next page"], '
        'button[title="Go to next page"]'
    )

    for button in buttons:

        if (
            button.is_displayed()
            and button.is_enabled()
            and button.get_attribute(
                "aria-disabled"
            ) != "true"
        ):

            return button

    return False


# ==========================================
# STEP 15: VERIFY ARCHIVED LEADS
# ==========================================

def verify_archived_leads():

    print()
    print("Opening Archived Leads...")

    step_wait().until(
        EC.element_to_be_clickable(
            ARCHIVED_BUTTON
        )
    ).click()

    container = step_wait().until(
        lambda d: get_archive_container()
    )

    original_ids = {
        lead["id"]
        for lead in original_leads
    }

    archived_records = {}

    # Wait for archived data to load.

    step_wait().until(
        lambda d: read_archived_leads(
            get_archive_container()
        ) or False
    )

    page_number = 1

    while True:

        check_timer()

        container = get_archive_container()

        if not container:

            raise AssertionError(
                "Archived Leads table not found."
            )

        page_records = read_archived_leads(
            container
        )

        archived_records.update(page_records)

        screenshot(
            f"Step_15_Archived_Page_{page_number}.png"
        )

        if original_ids.issubset(
            archived_records.keys()
        ):

            break

        next_button = find_archive_next_button(
            container
        )

        if not next_button:

            break

        previous_ids = set(
            page_records.keys()
        )

        next_button.click()

        step_wait().until(
            lambda d: (
                get_archive_container()
                and set(
                    read_archived_leads(
                        get_archive_container()
                    ).keys()
                ) != previous_ids
            )
        )

        page_number += 1

    print()
    print("VERIFYING ORIGINAL 10 ARCHIVED LEADS")
    print("-----------------------------------")

    verified_count = 0

    problems = []

    for lead in original_leads:

        lead_id = lead["id"]

        archived = archived_records.get(
            lead_id
        )

        if not archived:

            problems.append(
                f"Lead {lead_id} not found in archive."
            )

            print(f"{lead_id}: NOT FOUND")

            continue

        disposition = archived["disposition"]
        remarks = archived["remarks"]

        if disposition != CALL_DISPOSITION:

            problems.append(
                f"Lead {lead_id}: Incorrect or "
                f"unreadable disposition: {disposition}"
            )

            continue

        if remarks != REMARKS:

            problems.append(
                f"Lead {lead_id}: Incorrect or "
                f"unreadable remarks: {remarks}"
            )

            continue

        verified_count += 1

        print(f"Lead ID: {lead_id}")
        print(f"Name: {archived['name']}")
        print(f"Call Disposition: {disposition}")
        print(f"Remarks: {remarks}")
        print("Archive Verification: PASSED")
        print("-----------------------------------")

    print(
        f"Verified Archived Leads: "
        f"{verified_count}/{EXPECTED_LEADS}"
    )

    if problems:

        raise AssertionError(
            " | ".join(problems)
        )

    screenshot(
        "Step_15_Archived_Leads_Verified.png"
    )

    return (
        "All 10 original leads were found in "
        "Archived Leads with Call Disposition "
        "'Do Not Call' and Remarks 'Test batch'."
    )


# ==========================================
# MAIN TEST EXECUTION
# ==========================================

main_failed = False

precondition_passed = False

try:

    print("===================================")
    print("TC-TEL-04")
    print("UPDATE 10 LEADS X DISTRIBUTION")
    print(f"TIMEOUT: {TIMEOUT} SECONDS")
    print("===================================")

    # ======================================
    # PRECONDITION: AUTOMATIC LOGIN
    # ======================================

    current_step = "Precondition: Login"

    start_timer()

    login()

    # ======================================
    # PRECONDITION: OPEN ASSIGNED LEADS
    # ======================================

    current_step = "Precondition: Assigned Leads"

    start_timer()

    open_assigned_leads()

    # ======================================
    # PRECONDITION: VERIFY 10 TEST LEADS
    # ======================================

    current_step = "Precondition: Initial Batch"

    start_timer()

    verify_initial_batch()

    deadline = None

    precondition_passed = True

    first_lead_id = original_leads[0]["id"]

    # ======================================
    # STEP 1: CLICK EDIT ON FIRST LEAD
    # ======================================

    execute_step(
        1,
        "Click Edit Icon on First Lead",
        lambda: open_update_lead(first_lead_id),
        first_lead_id
    )

    # ======================================
    # STEP 2: SELECT CALL DISPOSITION
    # ======================================

    execute_step(
        2,
        "Select Do Not Call",
        select_call_disposition,
        first_lead_id
    )

    # ======================================
    # STEP 3: ENTER REMARKS
    # ======================================

    execute_step(
        3,
        "Enter Remarks: Test batch",
        enter_remarks,
        first_lead_id
    )

    # ======================================
    # STEP 4: CLICK UPDATE
    # ======================================

    execute_step(
        4,
        "Update First Lead",
        lambda: submit_update(first_lead_id),
        first_lead_id
    )

    # ======================================
    # STEP 5: UPDATE SECOND LEAD
    # ======================================

    second_lead_id = original_leads[1]["id"]

    execute_step(
        5,
        "Update Second Lead",
        lambda: update_complete_lead(second_lead_id),
        second_lead_id
    )

    # ======================================
    # STEP 6: UPDATE THIRD LEAD
    # ======================================

    third_lead_id = original_leads[2]["id"]

    execute_step(
        6,
        "Update Third Lead",
        lambda: update_complete_lead(third_lead_id),
        third_lead_id
    )

    # ======================================
    # STEP 7: UPDATE FOURTH LEAD
    # ======================================

    fourth_lead_id = original_leads[3]["id"]

    execute_step(
        7,
        "Update Fourth Lead",
        lambda: update_complete_lead(fourth_lead_id),
        fourth_lead_id
    )

    # ======================================
    # STEP 8: UPDATE FIFTH LEAD
    # ======================================

    fifth_lead_id = original_leads[4]["id"]

    execute_step(
        8,
        "Update Fifth Lead",
        lambda: update_complete_lead(fifth_lead_id),
        fifth_lead_id
    )

    # ======================================
    # STEP 9: UPDATE SIXTH LEAD
    # ======================================

    sixth_lead_id = original_leads[5]["id"]

    execute_step(
        9,
        "Update Sixth Lead",
        lambda: update_complete_lead(sixth_lead_id),
        sixth_lead_id
    )

    # ======================================
    # STEP 10: UPDATE SEVENTH LEAD
    # ======================================

    seventh_lead_id = original_leads[6]["id"]

    execute_step(
        10,
        "Update Seventh Lead",
        lambda: update_complete_lead(seventh_lead_id),
        seventh_lead_id
    )

    # ======================================
    # STEP 11: UPDATE EIGHTH LEAD
    # ======================================

    eighth_lead_id = original_leads[7]["id"]

    execute_step(
        11,
        "Update Eighth Lead",
        lambda: update_complete_lead(eighth_lead_id),
        eighth_lead_id
    )

    # ======================================
    # STEP 12: UPDATE NINTH LEAD
    # ======================================

    ninth_lead_id = original_leads[8]["id"]

    execute_step(
        12,
        "Update Ninth Lead",
        lambda: update_complete_lead(ninth_lead_id),
        ninth_lead_id
    )

    # ======================================
    # STEP 13: UPDATE TENTH LEAD
    # ======================================

    tenth_lead_id = original_leads[9]["id"]

    execute_step(
        13,
        "Update Tenth Lead",
        lambda: update_complete_lead(tenth_lead_id),
        tenth_lead_id
    )

    # ======================================
    # STEP 14: OBSERVE ASSIGNED LEADS
    # ======================================

    execute_step(
        14,
        "Verify New Batch of 10 Leads",
        verify_new_distribution
    )

    # ======================================
    # STEP 15: OPEN ARCHIVED LEADS
    # ======================================

    execute_step(
        15,
        "Verify Original 10 Archived Leads",
        verify_archived_leads
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
    print("TC-TEL-04: FAILED")
    print("===================================")
    print(f"Failed at: {current_step}")
    print("Reason: EXECUTION TIMEOUT")
    print(f"Time Limit: {TIMEOUT} seconds")
    print("===================================")

    screenshot(
        "TC-TEL-04_FAILED_Timeout.png"
    )

# ==========================================
# GENERAL ERROR HANDLER
# ==========================================

except Exception as error:

    main_failed = True

    print()
    print("===================================")
    print("TC-TEL-04: EXECUTION STOPPED")
    print("===================================")
    print(f"Stopped at: {current_step}")
    print(f"Reason: {error}")
    print("===================================")

    screenshot(
        "TC-TEL-04_Execution_Stopped.png"
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
    print("TC-TEL-04: FINAL TEST SUMMARY")
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
            f"Execution Time: "
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

    not_executed = 15 - len(results)

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

    print("Total Test Steps: 15")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Timeout Failures: {timed_out}")
    print(f"Not Executed: {not_executed}")

    print("-----------------------------------")

    print(
        f"Original Leads: {len(original_leads)}"
    )

    print(
        f"Confirmed Updated Leads: {len(updated_leads)}"
    )

    print(
        f"Newly Distributed Leads: {len(new_leads)}"
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

    elif passed == 15:

        final_result = "PASSED"

    else:

        final_result = "NOT FULLY VERIFIED"

    print(f"FINAL RESULT: {final_result}")

    # ======================================
    # EXPORT TEST RESULTS CSV
    # ======================================

    csv_path = os.path.join(
        EVIDENCE_FOLDER,
        "TC-TEL-04_Test_Results.csv"
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

    # ======================================
    # EXPORT ORIGINAL LEADS
    # ======================================

    original_csv = os.path.join(
        EVIDENCE_FOLDER,
        "Original_10_Leads.csv"
    )

    with open(
        original_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow([
            "Lead ID",
            "Lead Name",
            "Confirmed Updated"
        ])

        for lead in original_leads:

            writer.writerow([
                lead["id"],
                lead["name"],
                "Yes"
                if lead["id"] in updated_leads
                else "No"
            ])

    # ======================================
    # EXPORT NEWLY DISTRIBUTED LEADS
    # ======================================

    new_csv = os.path.join(
        EVIDENCE_FOLDER,
        "Newly_Distributed_Leads.csv"
    )

    with open(
        new_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow([
            "Lead ID",
            "Lead Name"
        ])

        for lead in new_leads:

            writer.writerow([
                lead["id"],
                lead["name"]
            ])

    print()
    print(f"Test Results: {csv_path}")
    print(f"Original Leads: {original_csv}")
    print(f"New Leads: {new_csv}")
    print(f"Evidence Folder: {EVIDENCE_FOLDER}")
    print("===================================")

    # Keep browser open for inspection.

    try:

        input(
            "\nPress Enter to close the browser..."
        )

    finally:

        driver.quit()
