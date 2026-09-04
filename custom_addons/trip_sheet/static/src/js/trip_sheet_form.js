/** @odoo-module **/
// It imports Odoo’s rpc function for server calls
import { rpc } from "@web/core/network/rpc";
var CellStatus;
(function (CellStatus) {
    CellStatus["Orange"] = "orange";
    CellStatus["Green"] = "green";
    CellStatus["Red"] = "red";
})(CellStatus || (CellStatus = {}));
// Declares columns (the table headers).
const columns = [
    "Date",
    "Km before",
    "Km after",
    "Km diff",
    "Liters",
    "Refill",
    "FuelEndDay",
];
// Keeps a global array dailyRecords to store all rows
let dailyRecords = [];
// 2. Utility functions
// getElementOrThrow: safely fetches a DOM element 
// by selector, throws an error if missing
function getElementOrThrow(selector) {
    const element = document.querySelector(selector);
    if (!element) {
        throw new Error(`Element not found: ${selector}`);
    }
    return element;
}
// parseNumber: converts string input into a number,
// handling commas and invalid values.
function parseNumber(value) {
    const normalizedValue = value.trim().replace(",", ".");
    const parsedValue = Number(normalizedValue);
    return Number.isFinite(parsedValue)
        ? parsedValue
        : 0;
}
// setCellStatus: applies CSS classes 
// to a cell depending on its status
function setCellStatus(cell, status) {
    cell.classList.remove("cellUser", "cellCommon", "cellError");
    switch (status) {
        case CellStatus.Orange:
            cell.classList.add("cellUser");
            break;
        case CellStatus.Green:
            cell.classList.add("cellCommon");
            break;
        case CellStatus.Red:
            cell.classList.add("cellError");
            break;
    }
}
// createCell: builds an <input> element with the right type,
// placeholder, read-only flag, and status
function createCell(type, placeholder, status, readOnly = false) {
    const input = document.createElement("input");
    input.type = type;
    input.placeholder = placeholder;
    input.readOnly = readOnly;
    if (type === "number") {
        input.inputMode = "decimal";
        input.step = "any";
    }
    setCellStatus(input, status);
    return input;
}
// 3. Generating the trip sheet
// Finds the container #kmRow and the starting fuel input #fuelstart
function generateRows(year, month) {
    // kmRow is the container div where all daily rows will be generated
    const kmRow = getElementOrThrow("#kmRow");
    // prevFuelInput is the input field for starting fuel at the beginning of the month
    const prevFuelInput = getElementOrThrow("#fuelstart");
    // Clears previous rows and resets dailyRecords.
    kmRow.innerHTML = "";
    dailyRecords = [];
    const gridTemplate = "120px 100px 100px 100px 100px 100px 100px";
    // Creates a header row with column names.
    const headerRow = document.createElement("div");
    headerRow.style.display = "grid";
    headerRow.style.gridTemplateColumns =
        gridTemplate;
    headerRow.style.gap = "5px";
    headerRow.style.fontWeight = "bold";
    headerRow.style.marginBottom = "8px";
    columns.forEach((text) => {
        const cell = document.createElement("input");
        cell.value = text;
        cell.readOnly = true;
        cell.style.textAlign = "center";
        cell.style.fontWeight = "bold";
        cell.style.backgroundColor = "#f0f0f0";
        headerRow.appendChild(cell);
    });
    kmRow.appendChild(headerRow);
    // Calculates how many days are in the selected month
    const daysInMonth = new Date(year, month, 0).getDate();
    // For each day:
    for (let day = 1; day <= daysInMonth; day++) {
        const row = document.createElement("div");
        row.style.display = "grid";
        row.style.gridTemplateColumns =
            gridTemplate;
        row.style.gap = "5px";
        row.style.marginBottom = "5px";
        const formattedDay = String(day).padStart(2, "0");
        const formattedMonth = String(month).padStart(2, "0");
        const dateStr = `${formattedDay}.${formattedMonth}.${String(year).slice(-2)}`;
        const jsDate = new Date(year, month - 1, day);
        const isWeekend = jsDate.getDay() === 0 ||
            jsDate.getDay() === 6;
        // Builds a row with inputs for date, km before/after,
        //  km diff, liters, refill, fuel end day.
        const dateField = createCell("text", "Date", CellStatus.Green, true);
        dateField.value = dateStr;
        const kmBefore = createCell("number", "Km before", CellStatus.Orange);
        const kmAfter = createCell("number", "Km after", CellStatus.Orange);
        const kmDiff = createCell("number", "Km diff", CellStatus.Green, true);
        const liters = createCell("number", "Liters", CellStatus.Green, true);
        const refill = createCell("number", "Refill", CellStatus.Orange);
        const fuelEndDay = createCell("number", "FuelEndDay", CellStatus.Green, true);
        row.append(dateField, kmBefore, kmAfter, kmDiff, liters, refill, fuelEndDay);
        // Creates a DailyRecord object with initial values.
        const record = {
            date: dateStr,
            isWeekend,
            kmBefore: 0,
            kmAfter: 0,
            kmDiff: 0,
            liters: 0,
            refill: 0,
            fuelEndDay: 0,
            status: CellStatus.Orange,
            validationErrors: [],
        };
        // Why updateDiff() is inside generateRows(year, month):  
        // Each row needs its own calculation logic tied to its inputs. 
        // Defining updateDiff inside the loop gives it access to that row’s specific record
        //  and input elements. It’s scoped locally, so each row has its own handler.
        function updateDiff() {
            record.validationErrors = [];
            const before = parseNumber(kmBefore.value);
            const after = parseNumber(kmAfter.value);
            const refillValue = parseNumber(refill.value);
            const diff = after - before;
            const fuelUsed = diff * 0.08;
            // UI = string. kmDiff.value and liters.value are input field values, 
            // which must be strings (HTML input expects text).
            kmDiff.value = String(diff);
            liters.value = String(fuelUsed);
            // internal logic = number. record.kmDiff is data model properties,
            // which are numbers (for calculations).
            record.kmBefore = before;
            record.kmAfter = after;
            record.kmDiff = diff;
            record.liters = fuelUsed;
            record.refill = refillValue;
            // If it’s the first day, use the starting fuel from the input. Otherwise, take 
            // the fuelEndDay of the previous record (day - 2 because arrays are zero‑indexed). 
            // ?? 0 means if that value is missing, default to 0.
            const previousFuel = day === 1
                ? parseNumber(prevFuelInput.value)
                : dailyRecords[day - 2]?.fuelEndDay ?? 0;
            record.fuelEndDay =
                previousFuel +
                    refillValue -
                    fuelUsed;
            fuelEndDay.value =
                String(record.fuelEndDay);
            setCellStatus(kmBefore, CellStatus.Orange);
            setCellStatus(kmAfter, CellStatus.Orange);
            setCellStatus(kmDiff, CellStatus.Green);
            setCellStatus(liters, CellStatus.Green);
            setCellStatus(refill, CellStatus.Orange);
            setCellStatus(fuelEndDay, CellStatus.Green);
            record.status = CellStatus.Orange;
            // Marks cells red and adds error messages if rules are broken.
            if (isWeekend && diff !== 0) {
                setCellStatus(kmBefore, CellStatus.Red);
                setCellStatus(kmAfter, CellStatus.Red);
                record.status = CellStatus.Red;
                record.validationErrors.push("Weekend mileage must be zero.");
            }
            if (before <= 0 ||
                after <= 0 ||
                after < before) {
                setCellStatus(kmBefore, CellStatus.Red);
                setCellStatus(kmAfter, CellStatus.Red);
                record.status = CellStatus.Red;
                record.validationErrors.push("Mileage must be greater than zero and Km After must not be less than Km Before.");
            }
            if (refillValue < 0) {
                setCellStatus(refill, CellStatus.Red);
                record.status = CellStatus.Red;
                record.validationErrors.push("Refill cannot be negative.");
            }
            if (record.fuelEndDay < 0) {
                setCellStatus(fuelEndDay, CellStatus.Red);
                record.status = CellStatus.Red;
                record.validationErrors.push("Fuel at the end of the day cannot be negative.");
            }
        }
        // Attaches updateDiff to input events on kmBefore, 
        // kmAfter, and refill
        kmBefore.addEventListener("input", updateDiff);
        kmAfter.addEventListener("input", updateDiff);
        refill.addEventListener("input", updateDiff);
        // Appends the row to the DOM and 
        // pushes the record into dailyRecords.
        kmRow.appendChild(row);
        dailyRecords.push(record);
    }
    console.log("Daily records generated:", dailyRecords);
}
// 4. Saving the trip sheet.  It takes the form element, finds the month picker input inside it, 
// and later uses it to build the payload for saving (JSON object containing:
// The selected month, The starting fuel value,  The array of all daily records. That payload is then sent to the backend via RPC.).
// By declaring Promise<void>, you’re telling TypeScript: 
// This function runs asynchronously, 
// but when its done, theres no return value you need to use.
async function saveTripSheet(form) {
    // Gets month and fuel start inputs
    const monthInput = form.querySelector("#monthPicker");
    const fuelStartInput = form.querySelector("#fuelstart");
    // Validates that they exist and have values
    if (!monthInput || !fuelStartInput) {
        console.error("Month or starting fuel input is missing.");
        return;
    }
    // If the user tries to save without selecting a month, the code alerts them and then calls .focus() 
    // to move the cursor into the month input field, guiding them to fix the mistake
    if (!monthInput.value) {
        alert("Please select a month.");
        monthInput.focus();
        return;
    }
    // Ensures rows were generated.
    if (dailyRecords.length === 0) {
        alert("Select a month to generate daily records.");
        return;
    }
    // Collects invalid records (status Red or with errors).
    const invalidRecords = dailyRecords.filter((record) => record.status === CellStatus.Red ||
        record.validationErrors.length > 0);
    if (invalidRecords.length > 0) {
        console.error("Invalid records:", invalidRecords);
        alert("Please correct the red fields before saving.");
        return;
    }
    const fuelStart = parseNumber(fuelStartInput.value);
    // Calls Odoo backend via rpc("/trip_sheet/save", {...}).
    // try runs code that might fail (like the RPC call).
    try {
        const result = await rpc("/trip_sheet/save", {
            month: monthInput.value,
            fuel_start: fuelStart,
            records: dailyRecords,
        });
        if (!result.success) {
            throw new Error(result.message ||
                "The trip sheet could not be saved.");
        }
        console.log("Trip sheet saved:", result);
        // If successful, alerts with the saved record ID.
        alert(`Trip sheet saved. Record ID: ${result.id}`);
        // If failed, shows an error message.
        // catch handles errors if they occur.
        // error instanceof Error checks if the caught object is a real Error. 
        // If yes, use its .message. If not, show a generic “Unknown error”. 
        // This prevents crashes when unexpected values are thrown.
    }
    catch (error) {
        const message = error instanceof Error
            ? error.message
            : "Unknown error while saving.";
        console.error("Saving failed:", error);
        alert(message);
    }
}
// 5. Initialization
function initializeTripSheetForm() {
    // Finds the form #kmForm.
    const form = document.querySelector("#kmForm");
    // Exits if not present. This asset also loads on other website pages.
    if (!form) {
        return;
    }
    // Gets month picker and fuel start inputs.
    const monthPicker = form.querySelector("#monthPicker");
    const fuelStartInput = form.querySelector("#fuelstart");
    if (!monthPicker || !fuelStartInput) {
        console.error("Trip Sheet form is missing required elements.");
        return;
    }
    // 10. “Prevents double initialization using a dataset flag.” 
    //  The form has a custom attribute form.dataset.tripSheetInitialized. If it’s already "true", the code skips initialization. 
    // This avoids attaching duplicate event listeners if the script runs twice.
    if (form.dataset.tripSheetInitialized ===
        "true") {
        return;
    }
    form.dataset.tripSheetInitialized =
        "true";
    // Adds a change listener to monthPicker. This means: when the user selects a new month in the picker, the callback runs. 
    // It parses the year/month and regenerates the rows for that month.
    monthPicker.addEventListener("change", () => {
        // Parses year and month.
        const [yearText, monthText] = monthPicker.value.split("-");
        const year = Number(yearText);
        const month = Number(monthText);
        // Validates them
        if (!Number.isInteger(year) ||
            !Number.isInteger(month) ||
            month < 1 ||
            month > 12) {
            console.error("Invalid month:", monthPicker.value);
            return;
        }
        generateRows(year, month);
    });
    // Adds a submit listener to the form. when the user clicks “Save” or submits the form, 
    // the callback runs. It prevents the default browser submit (page reload) 
    // and instead calls saveTripSheet(form) to send data via RPC.
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        void saveTripSheet(form);
    });
    console.log("Trip Sheet form initialized.");
}
// 6. DOM ready check. If the document is still loading, 
// waits for DOMContentLoaded then runs initializeTripSheetForm.
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeTripSheetForm, {
        once: true,
    }); // Otherwise, runs it immediately.
}
else {
    initializeTripSheetForm();
}
//# sourceMappingURL=trip_sheet_form.js.map