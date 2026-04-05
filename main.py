/* ═══════════════════════════════════════════════════════════════
   app.js — ReSan Private Bank
   This file is the brain of the frontend.
   It connects every button, form and page in index.html
   to the FastAPI backend running on Render.com.
   Every function here either:
     1. Calls the backend via api() and shows the result, OR
     2. Controls what the user sees on screen (pages, modals, toasts)
═══════════════════════════════════════════════════════════════ */

"use strict";
// Enables JavaScript strict mode for the entire file
// This catches silent errors — e.g. using an undeclared variable throws an error
// instead of silently creating a global variable (which causes hard-to-find bugs)


/* ─── CONFIG ─────────────────────────────────────────────────── */

const BASE_URL = "https://resan-bank-management-app-2.onrender.com";
// The base URL of our FastAPI backend running on Render.com
// Every API call in this file is: BASE_URL + "/api/some-route"
// ⚠️ If you redeploy to a new Render URL, update this one line


/* ─── SESSION MANAGEMENT ─────────────────────────────────────── */
// We use localStorage to remember who is logged in across page refreshes
// localStorage persists until the user clears browser data or we delete it
// Keys used:
//   "resan_session" → account number of logged-in user (e.g. "RSN4821")
//   "resan_name"    → full name (e.g. "Richa") for display in sidebar
//   "resan_pin"     → PIN cached for re-fetching dashboard after refresh

function setSession(accNo) {
  localStorage.setItem("resan_session", accNo);
  // Saves account number to browser storage after successful login or signup
  // This is our "session token" — if this value exists, user is logged in
  // accNo example: "RSN4821"
}

function getSession() {
  return localStorage.getItem("resan_session");
  // Returns the account number if user is logged in, or null if not logged in
  // Used by: loadDashboard(), handleDeposit(), handleWithdraw() etc.
  // to check whether to refresh the logged-in user's dashboard
}

function clearSession() {
  localStorage.removeItem("resan_session");
  // Removes the session token — effectively logs the user out
  // Called by logout() and handleClose() (when user closes their own account)
}


/* ─── API HELPER ─────────────────────────────────────────────── */

async function api(endpoint, method = "GET", body = null) {
  // Universal function for all JSON API calls to the backend
  // Used by: login, signup, deposit, withdraw, details, update, close, stats
  // Parameters:
  //   endpoint → the route path e.g. "/api/deposit"
  //   method   → HTTP verb: "GET", "POST", "PUT", "DELETE" (default: "GET")
  //   body     → JavaScript object to send as JSON (null for GET requests)

  const options = {
    method,
    // Sets the HTTP method for the fetch request (GET, POST etc.)

    headers: { "Content-Type": "application/json" },
    // Tells the backend this request contains JSON data
    // Required for FastAPI to parse the request body correctly
  };

  if (body) {
    options.body = JSON.stringify(body);
    // Convert the JavaScript object to a JSON string for transmission
    // Example: { acc_no: "RSN4821", pin: 1234 } → '{"acc_no":"RSN4821","pin":1234}'
    // The backend's Pydantic models then parse this string back into Python objects
  }

  const res = await fetch(BASE_URL + endpoint, options);
  // Makes the actual HTTP request to the backend
  // fetch() is the browser's built-in function for making network requests
  // await means "wait here until the response arrives before continuing"
  // Full URL example: "https://resan-bank-management-app-2.onrender.com/api/deposit"

  const data = await res.json();
  // Parse the response body from JSON string into a JavaScript object
  // await needed because reading the response body is also asynchronous

  if (!res.ok) {
    // res.ok is true when HTTP status is 200-299 (success)
    // res.ok is false when status is 400, 401, 404, 422, 500 etc. (error)
    throw new Error(data.detail || "Something went wrong.");
    // data.detail is the error message from our FastAPI HTTPException
    // e.g. "Incorrect PIN." or "Account not found." or "Insufficient balance."
    // This thrown error is caught by the try/catch in each calling function
    // and displayed to the user as a red toast notification
  }

  return data;
  // Return the parsed response object to the calling function
  // e.g. { accountNo: "RSN4821", name: "Richa", balance: 5000, ... }
}

async function apiForm(endpoint, formData) {
  // Separate function for file upload requests (cannot use JSON for files)
  // Used only by: verifyAndCreate() to upload Aadhaar, PAN, Address Proof PDFs
  // FormData automatically sets Content-Type to "multipart/form-data"

  const res  = await fetch(BASE_URL + endpoint, { method: "POST", body: formData });
  // Sends the files + form fields to the backend's /api/docs/upload route
  // No Content-Type header needed — fetch sets it automatically for FormData

  const data = await res.json();
  // Parse the JSON response from the backend

  if (!res.ok) throw new Error(data.detail || "Upload failed.");
  // Throw error if upload failed (e.g. wrong PIN, account not found)

  return data;
  // Returns { message: "Documents uploaded successfully!" } on success
}


/* ─── PAGE NAVIGATION ─────────────────────────────────────────── */

function showPage(pageId) {
  // Shows one page and hides all others
  // Called by: sidebar nav links (onclick="showPage('home')" in index.html)
  // Each page is a <section class="page" id="page-XXXX"> element

  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  // Remove "active" class from ALL page sections
  // The CSS rule .page { display: none } hides all pages by default
  // Only the page with class "active" is shown (.page.active { display: block })

  const target = document.getElementById("page-" + pageId);
  // Find the specific page section e.g. "page-deposit" → <section id="page-deposit">

  if (target) target.classList.add("active");
  // Add "active" class to make this page visible
  // CSS handles the actual show/hide via the .page.active selector in style.css

  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  // Remove "active" highlight from all sidebar nav items

  const navItem = document.querySelector(`[data-page="${pageId}"]`);
  // Find the nav item with matching data-page attribute
  // e.g. data-page="deposit" on the Deposit nav link in index.html

  if (navItem) navItem.classList.add("active");
  // Highlight the current page's nav item with the gold active style

  document.getElementById("sidebar").classList.remove("open");
  // Close the mobile sidebar after navigation
  // On mobile, the sidebar slides in — this closes it automatically after a tap
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
  // Opens or closes the mobile sidebar
  // Called by the hamburger button (☰) at the top of the page on mobile
  // CSS transitions handle the slide-in animation
}


/* ─── MODAL CONTROL ──────────────────────────────────────────── */
// Modals are the popup overlays for Login, Signup, and Login OTP
// They float above the page content when "open"

let currentModal = null;
// Tracks which modal is currently open (by its ID string)
// e.g. "login", "signup", "otp-login"
// Used by closeModal() to know which modal to hide

function showModal(id) {
  // Opens a specific modal by its ID
  // Called by: Login/Signup buttons in sidebar, nav hero buttons, modal switch links

  closeModal();
  // Close any currently open modal first (prevents stacking two modals)

  const overlay = document.getElementById("modal-overlay");
  // The dark semi-transparent backdrop behind the modal (in index.html)

  const modal = document.getElementById("modal-" + id);
  // Find the modal element e.g. "modal-login" → <div id="modal-login">
  // Modals defined in index.html: modal-login, modal-signup, modal-otp-login

  if (!modal) return;
  // Safety check: if modal doesn't exist in HTML, do nothing

  overlay.classList.add("active");
  // Show the dark overlay (CSS dims the background)

  modal.style.display = "block";
  // Make the modal element visible before applying the animation class

  requestAnimationFrame(() => modal.classList.add("active"));
  // Add "active" class on the next animation frame
  // This tiny delay allows the CSS transition to animate (fade + slide up)
  // Without requestAnimationFrame the transition doesn't play on first open

  currentModal = id;
  // Remember which modal is open so closeModal() knows what to close
}

function closeModal() {
  // Closes whichever modal is currently open
  // Called by: ✕ buttons in modals, clicking the overlay, after login/signup success

  if (!currentModal) return;
  // No modal is open — nothing to close

  document.getElementById("modal-overlay").classList.remove("active");
  // Hide the dark backdrop overlay

  const modal = document.getElementById("modal-" + currentModal);
  // Get the currently open modal element

  if (modal) {
    modal.classList.remove("active");
    // Remove "active" class to trigger the CSS fade-out transition

    setTimeout(() => (modal.style.display = "none"), 250);
    // After the 250ms fade-out animation completes, fully hide the element
    // Matching the --transition: 0.25s duration defined in style.css
  }

  currentModal = null;
  // Reset the tracker — no modal is open anymore
}


/* ─── TOAST NOTIFICATIONS ─────────────────────────────────────── */
// Toast = small popup notification at bottom-right of screen
// Used throughout the app to show success/error/info messages
// The toast element is <div class="toast" id="toast"> in index.html

let toastTimer = null;
// Stores the setTimeout reference so we can cancel it if a new toast appears

function showToast(msg, type = "info") {
  // Displays a notification message to the user
  // type: "success" (green), "error" (red), "info" (default gold)
  // Called after every API call with the result message

  const toast = document.getElementById("toast");
  // Get the toast container element from index.html

  document.getElementById("toast-msg").textContent = msg;
  // Set the message text e.g. "₹5000 deposited successfully!"

  toast.className = "toast " + type;
  // Set the color class: "toast success", "toast error", or "toast info"
  // CSS in style.css styles each type with a different background color

  toast.classList.add("show");
  // Add "show" class — CSS transitions the toast in from the bottom

  clearTimeout(toastTimer);
  // Cancel any existing hide timer (prevents a previous toast from hiding this one)

  toastTimer = setTimeout(() => toast.classList.remove("show"), 3500);
  // Automatically hide the toast after 3.5 seconds
  // Removes "show" class → CSS transitions it back out
}


/* ─── AUTH UI UPDATE ─────────────────────────────────────────── */

function refreshAuthUI() {
  // Updates the sidebar footer to show either:
  //   A) Login/Signup buttons (when user is NOT logged in)
  //   B) User avatar + name + Logout button (when user IS logged in)
  // Called on: page load, after login, after signup, after logout

  const accNo    = getSession();
  // Check if a session exists in localStorage
  // Returns account number string if logged in, null if not

  const authBtns = document.getElementById("auth-buttons");
  // The div containing Login and Sign Up buttons in the sidebar footer

  const userInfo = document.getElementById("user-info");
  // The div containing user avatar, name, and Logout button

  if (accNo) {
    // User IS logged in

    authBtns.style.display = "none";
    // Hide the Login/Signup buttons

    userInfo.style.display = "block";
    // Show the user info section

    const cachedName = localStorage.getItem("resan_name") || accNo;
    // Get the cached name from localStorage (stored during login/signup)
    // Falls back to account number if name isn't cached for some reason

    document.getElementById("user-avatar").textContent = cachedName[0].toUpperCase();
    // Set the circular avatar to the first letter of the user's name
    // e.g. "Richa" → "R" displayed in the gold circle in the sidebar

    document.getElementById("user-name").textContent = cachedName;
    // Show the full name below the avatar e.g. "Richa"

  } else {
    // User is NOT logged in

    authBtns.style.display = "block";
    // Show the Login and Sign Up buttons

    userInfo.style.display = "none";
    // Hide the user info section
  }
}

function logout() {
  // Logs out the current user and returns to the Home page
  // Called by the Logout button in the sidebar footer

  clearSession();
  // Remove the session token from localStorage

  localStorage.removeItem("resan_name");
  // Clear the cached name from localStorage

  localStorage.removeItem("resan_pin");
  // Clear the cached PIN from localStorage

  refreshAuthUI();
  // Update the sidebar to show Login/Signup buttons again

  showPage("home");
  // Navigate back to the Home page

  showToast("Logged out successfully.", "success");
  // Show green confirmation toast
}


/* ─── INPUT VALIDATORS ───────────────────────────────────────── */
// These functions run on oninput events in index.html form fields
// They add visual "valid" (green border) or "error" (red border) classes
// in real-time as the user types, giving instant feedback

function validateNameInput(input) {
  // Validates name fields (su-name and su-gname in signup form)
  // Rules: letters and spaces only, minimum 2 characters

  const val   = input.value;
  const valid = /^[a-zA-Z\s]*$/.test(val);
  // Regex: only allows a-z, A-Z, and spaces
  // /^...$/ = must match from start to end of string
  // Returns true if all characters are letters or spaces

  input.classList.toggle("error", !valid && val.length > 0);
  // Add "error" class (red border) if: input has characters BUT they're invalid

  input.classList.toggle("valid", valid && val.trim().length >= 2);
  // Add "valid" class (green border) if: all valid characters AND at least 2 letters

  if (!valid) input.value = val.replace(/[^a-zA-Z\s]/g, "");
  // Auto-remove any invalid characters as user types
  // e.g. if user types "Richa123", it becomes "Richa" automatically
}

function validateAgeInput(input) {
  // Validates the age field (su-age in signup form)
  // Also shows/hides the minor guardian section based on age

  const val      = parseInt(input.value);
  // Parse input as integer (strips decimals)

  const validInt = Number.isInteger(val) && val >= 1 && val <= 120;
  // Valid if: is a whole number AND between 1 and 120

  input.classList.toggle("error", !validInt && input.value.length > 0);
  input.classList.toggle("valid", validInt);
  // Show green/red border based on validity

  if (input.value.includes(".")) input.value = Math.floor(parseFloat(input.value));
  // If user types a decimal like "17.5", auto-round down to "17"
  // Age must be a whole number as required by the backend model

  const minorSection = document.getElementById("minor-section");
  // The guardian details section in the signup form (index.html)

  if (minorSection) {
    minorSection.style.display = (validInt && val < 18) ? "block" : "none";
    // Show guardian section if age is valid AND less than 18
    // Hide it if age is 18+ (no guardian needed for adults)
  }
}

function validateEmailInput(input) {
  // Validates email format fields (su-email, su-gemail, upd-email)

  const val   = input.value.trim();
  const valid = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val);
  // Regex checks for: something@something.something (basic email format)
  // [^\s@]+ = one or more characters that aren't spaces or @
  // \.[^\s@]{2,}$ = dot followed by 2+ domain characters at the end

  input.classList.toggle("error", !valid && val.length > 0);
  input.classList.toggle("valid", valid);
  // Show green/red border in real-time as user types
}

function validatePinInput(input) {
  // Validates PIN fields (su-pin, login-pin, dep-pin, with-pin etc.)
  // PIN must be exactly 4 digits

  input.value = input.value.replace(/\D/g, "");
  // Strip any non-digit characters the user might type
  // /\D/g = any character that is NOT a digit, globally (all occurrences)

  const valid = /^\d{4}$/.test(input.value);
  // Valid if exactly 4 digits: /^\d{4}$/ = start, 4 digits, end

  input.classList.toggle("error", !valid && input.value.length > 0);
  input.classList.toggle("valid", valid);
}

function validatePhoneInput(input) {
  // Validates phone number fields (su-phone, su-gphone)
  // Must be exactly 10 digits (Indian mobile format)

  input.value = input.value.replace(/\D/g, "");
  // Strip any non-digit characters automatically

  const valid = /^\d{10}$/.test(input.value);
  // Valid if exactly 10 digits

  input.classList.toggle("error", !valid && input.value.length > 0);
  input.classList.toggle("valid", valid);
}

function validateAmount(input, maxVal) {
  // Validates amount fields (dep-amount and with-amount)
  // maxVal: 100000 for deposit (max ₹1 lakh), Infinity for withdraw

  let val = parseFloat(input.value);
  // Parse as float first to handle decimal inputs

  if (!Number.isFinite(val) || val <= 0) {
    input.classList.add("error");
    return;
    // If not a valid positive number, show error and stop
  }

  val = Math.floor(val);
  // Round down to integer — no paise allowed, only whole rupees

  input.value = val;
  // Update the input to show the rounded value

  input.classList.toggle("error", val < 1 || val > maxVal);
  // Error if below ₹1 or above the maximum allowed

  input.classList.toggle("valid", val >= 1 && val <= maxVal);
  // Valid if within range
}

function formatAccNo(input) {
  input.value = input.value.toUpperCase();
  // Auto-converts account number input to uppercase as user types
  // So "rsn4821" becomes "RSN4821" matching our backend's .upper() call
  // Applied to: dep-acc, with-acc inputs via oninput="formatAccNo(this)"
}


/* ─── FILE UPLOAD HELPERS ─────────────────────────────────────── */
// Used in signup Step 2 for document uploads (Aadhaar, PAN, Address Proof)

function triggerFile(inputId) {
  document.getElementById(inputId).click();
  // Programmatically clicks the hidden file input when user clicks the styled upload box
  // The actual <input type="file"> is hidden with style="display:none;" in index.html
  // We show a custom-styled div instead, and this function bridges the two
}

function handleFile(input, labelId) {
  // Called when user selects a file from the file picker
  // Validates the file and updates the upload box label

  const file = input.files[0];
  // Get the first (and only) selected file

  const box = input.parentElement;
  // The file-upload-box div containing this input

  if (!file) return;
  // User opened the picker but didn't select anything — do nothing

  if (file.type !== "application/pdf") {
    // Only PDF files are accepted for bank documents
    showToast("Only PDF files are accepted.", "error");
    input.value = "";
    // Clear the file input so user must reselect
    return;
  }

  if (file.size > 2 * 1024 * 1024) {
    // File must be under 2MB (2 * 1024 * 1024 bytes)
    showToast("File too large. Maximum size is 2MB.", "error");
    input.value = "";
    return;
  }

  document.getElementById(labelId).textContent =
    `✓ ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
  // Update the upload box text to show: "✓ aadhaar.pdf (345.2 KB)"
  // labelId is the ID of the div showing the upload status text

  box.classList.add("uploaded");
  // Add "uploaded" class to the box — CSS turns the border green
}


/* ─── OTP INPUT BOXES ─────────────────────────────────────────── */
// The OTP entry uses 6 individual single-character input boxes
// (otp0–otp5 for signup, lotp0–lotp5 for login in index.html)

function otpAdvance(input, index, prefix = "") {
  // Auto-advances focus to the next OTP box after a digit is entered
  // Called by oninput on each OTP box in index.html

  input.value = input.value.replace(/\D/g, "");
  // Strip any non-digit character (OTP boxes should only contain digits)

  if (input.value.length === 1 && index < 5) {
    // If this box has a digit AND it's not the last box (index 5)
    const nextId = (prefix === "login" ? "lotp" : "otp") + (index + 1);
    // Build the ID of the next box:
    //   Signup: "otp0" → "otp1" → "otp2" etc.
    //   Login:  "lotp0" → "lotp1" → "lotp2" etc.
    const next = document.getElementById(nextId);
    if (next) next.focus();
    // Move keyboard focus to the next box automatically
  }
}

function readOTPBoxes(prefix) {
  // Reads all 6 OTP box values and combines them into one string
  // prefix: "" for signup OTP boxes, "login" for login OTP boxes

  const ids = prefix === "login"
    ? ["lotp0","lotp1","lotp2","lotp3","lotp4","lotp5"]
    // IDs of the 6 login OTP boxes in index.html modal-otp-login
    : ["otp0","otp1","otp2","otp3","otp4","otp5"];
    // IDs of the 6 signup OTP boxes in index.html modal-signup step 3

  return ids.map(id => document.getElementById(id).value).join("");
  // Get the value from each box and join all into a single 6-char string
  // e.g. ["4","8","2","9","5","1"] → "482951"
}

let otpCountdown = null;
// Stores the setInterval reference for the OTP countdown timer
// Stored globally so we can clear it if user requests a resend

function startOTPTimer() {
  // Starts the 30-second countdown shown in signup step 3
  // After countdown reaches 0, the "Resend" button appears

  let seconds = 30;
  // Countdown starts at 30 seconds

  document.getElementById("otp-countdown").textContent = seconds;
  // Display "30" in the "Resend OTP in 30s" text in index.html

  document.getElementById("resend-btn").style.display = "none";
  // Hide the Resend button while countdown is active

  clearInterval(otpCountdown);
  // Cancel any existing countdown timer before starting a new one
  // Prevents multiple timers running simultaneously if user resends

  otpCountdown = setInterval(() => {
    // Run every 1000ms (1 second)
    seconds--;
    // Decrease countdown by 1

    document.getElementById("otp-countdown").textContent = seconds;
    // Update the displayed countdown number

    if (seconds <= 0) {
      clearInterval(otpCountdown);
      // Stop the interval when countdown reaches 0

      document.getElementById("resend-btn").style.display = "inline";
      // Show the Resend OTP button so user can request a new OTP
    }
  }, 1000);
}


/* ─── SIGNUP FLOW ─────────────────────────────────────────────── */
// The signup process has 3 steps shown in the modal-signup in index.html:
//   Step 1: Personal info (name, age, guardian if minor, email, phone, PIN)
//   Step 2: Document uploads (Aadhaar, PAN, Address Proof PDFs)
//   Step 3: OTP verification (6-digit code sent to phone)

async function goStep2() {
  // Called when user clicks "Continue →" on Step 1 of signup
  // Validates all Step 1 inputs before allowing progression to Step 2

  const name  = document.getElementById("su-name").value.trim();
  // User's full name from the su-name input field

  const age   = parseInt(document.getElementById("su-age").value);
  // User's age as integer from su-age input

  const email = document.getElementById("su-email").value.trim();
  // Email from su-email input

  const phone = document.getElementById("su-phone").value.trim();
  // 10-digit phone from su-phone input (OTP will be sent here)

  const pin   = document.getElementById("su-pin").value;
  // 4-digit PIN from su-pin input

  // ── Validation checks before proceeding ──
  if (!name || name.length < 2)
    return showToast("Enter your full name (min 2 letters).", "error");
  // Name must exist and be at least 2 characters

  if (!/^[a-zA-Z\s]+$/.test(name))
    return showToast("Name must contain only letters.", "error");
  // Name must only contain letters and spaces (no numbers, symbols)

  if (!Number.isInteger(age) || age < 1 || age > 120)
    return showToast("Enter a valid age (1–120).", "error");
  // Age must be a whole number between 1 and 120

  if (age < 18) {
    // Extra validation for minor accounts — guardian details must be complete
    const gname  = document.getElementById("su-gname").value.trim();
    const gage   = parseInt(document.getElementById("su-gage").value);
    const rel    = document.getElementById("su-relation").value;
    const gphone = document.getElementById("su-gphone").value.trim();
    const gemail = document.getElementById("su-gemail").value.trim();
    const gdoc   = document.getElementById("guardian-doc").files[0];
    // All guardian fields from the minor-section div in index.html

    if (!gname)
      return showToast("Guardian name is required.", "error");
    if (!Number.isInteger(gage) || gage < 18)
      return showToast("Guardian must be 18 or older.", "error");
    if (!rel)
      return showToast("Select guardian relationship.", "error");
    if (!/^\d{10}$/.test(gphone))
      return showToast("Guardian phone must be 10 digits.", "error");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(gemail))
      return showToast("Enter a valid guardian email.", "error");
    if (!gdoc)
      return showToast("Upload guardian ID PDF.", "error");
    // All minor-specific fields must be filled before proceeding
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email))
    return showToast("Enter a valid email address.", "error");

  if (!/^\d{10}$/.test(phone))
    return showToast("Phone must be exactly 10 digits.", "error");

  if (!/^\d{4}$/.test(pin))
    return showToast("PIN must be exactly 4 digits.", "error");

  // ── All validations passed — show Step 2 ──
  document.getElementById("signup-step1").style.display = "none";
  // Hide Step 1 personal info form

  document.getElementById("signup-step2").style.display = "block";
  // Show Step 2 document upload form

  document.getElementById("step1-dot").classList.add("done");
  // Mark Step 1 indicator as completed in the steps-bar at top of modal

  document.getElementById("step2-dot").classList.add("active");
  // Mark Step 2 indicator as currently active
}

function goStep1() {
  // Called when user clicks "← Back" on Step 2
  // Takes user back to Step 1 without losing their entered data

  document.getElementById("signup-step2").style.display = "none";
  // Hide Step 2

  document.getElementById("signup-step1").style.display = "block";
  // Show Step 1 again (data is preserved because we didn't clear the inputs)

  document.getElementById("step2-dot").classList.remove("active");
  // Deactivate the Step 2 indicator in the steps-bar
}

async function goStep3() {
  // Called when user clicks "Continue →" on Step 2
  // Validates that all required PDFs are uploaded, then sends OTP

  if (!document.getElementById("aadhaar-doc").files[0])
    return showToast("Upload Aadhaar PDF.", "error");
  // Aadhaar is required for all accounts — must be selected before proceeding

  if (!document.getElementById("pan-doc").files[0])
    return showToast("Upload PAN Card PDF.", "error");
  // PAN card is required for all accounts

  if (!document.getElementById("address-doc").files[0])
    return showToast("Upload Address Proof PDF.", "error");
  // Address proof is required for all accounts

  const phone = document.getElementById("su-phone").value.trim();
  // Get the phone number entered in Step 1 — OTP will be sent here

  try {
    const res = await api("/api/otp/send", "POST", { phone });
    // Call the backend to generate and (in production) send the OTP
    // Backend route: POST /api/otp/send in main.py

    startOTPTimer();
    // Start the 30-second countdown in the OTP step

    document.getElementById("otp-phone-display").textContent = "+91 " + phone;
    // Show "OTP sent to +91 9876543210" in the Step 3 info box

    document.getElementById("signup-step2").style.display = "none";
    // Hide Step 2 document upload

    document.getElementById("signup-step3").style.display = "block";
    // Show Step 3 OTP verification

    document.getElementById("step2-dot").classList.add("done");
    // Mark Step 2 as completed

    document.getElementById("step3-dot").classList.add("active");
    // Mark Step 3 as active

    showToast(`OTP sent! Dev OTP: ${res.dev_otp}`, "info");
    // Show the OTP in a toast for testing purposes
    // res.dev_otp is sent back by the backend (development mode only)

  } catch (err) {
    showToast(err.message, "error");
    // Show any backend error as a red toast
  }
}

async function resendOTP() {
  // Called when user clicks the "Resend" button that appears after countdown
  // Sends a fresh OTP to the same phone number

  const phone = document.getElementById("su-phone").value.trim();

  try {
    const res = await api("/api/otp/send", "POST", { phone });
    // Request a new OTP from the backend

    startOTPTimer();
    // Restart the 30-second countdown

    showToast(`OTP resent! Dev OTP: ${res.dev_otp}`, "info");
    // Show the new OTP in the toast
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function verifyAndCreate() {
  // Called when user clicks "Verify & Create Account" in signup Step 3
  // This is the final step — it creates the actual bank account

  const enteredOTP = readOTPBoxes("");
  // Collect all 6 digits from otp0–otp5 boxes into one string e.g. "482951"

  if (enteredOTP.length < 6)
    return showToast("Enter the full 6-digit OTP.", "error");
  // Must have all 6 digits before submitting

  const age     = parseInt(document.getElementById("su-age").value);
  const isMinor = age < 18;
  // Determine if this is a minor account to include guardian fields

  // ── Build the request payload ──
  const payload = {
    name:  document.getElementById("su-name").value.trim(),   // From su-name input
    age,                                                        // Parsed age integer
    email: document.getElementById("su-email").value.trim(),  // From su-email input
    phone: document.getElementById("su-phone").value.trim(),  // From su-phone input
    pin:   parseInt(document.getElementById("su-pin").value), // 4-digit PIN as integer
    otp:   enteredOTP,
    // The 6-digit OTP string for backend to verify against otp_store
  };

  if (isMinor) {
    // Add guardian fields to payload for minor accounts
    payload.guardian_name     = document.getElementById("su-gname").value.trim();
    payload.guardian_age      = parseInt(document.getElementById("su-gage").value);
    payload.guardian_relation = document.getElementById("su-relation").value;
    // The selected option from the relationship dropdown
    payload.guardian_phone    = document.getElementById("su-gphone").value.trim();
    payload.guardian_email    = document.getElementById("su-gemail").value.trim();
  }

  try {
    const res = await api("/api/account/create", "POST", payload);
    // Call backend to create the account
    // Backend verifies OTP, creates account record, returns accountNo
    // Route: POST /api/account/create in main.py

    // ── Upload documents immediately after account creation ──
    const formData = new FormData();
    // FormData is used for multipart requests (files + text fields together)

    formData.append("acc_no", res.accountNo);
    // Include the newly created account number so backend can find the account

    formData.append("pin", payload.pin);
    // Include PIN for backend security verification before accepting docs

    formData.append("aadhaar", document.getElementById("aadhaar-doc").files[0]);
    // Attach the Aadhaar PDF file selected in Step 2

    formData.append("pan", document.getElementById("pan-doc").files[0]);
    // Attach the PAN Card PDF selected in Step 2

    formData.append("address_proof", document.getElementById("address-doc").files[0]);
    // Attach the Address Proof PDF selected in Step 2

    if (isMinor && document.getElementById("guardian-doc").files[0]) {
      formData.append("guardian_doc", document.getElementById("guardian-doc").files[0]);
      // Attach guardian ID PDF only for minor accounts
    }

    await apiForm("/api/docs/upload", formData);
    // Send all PDFs to backend
    // Uses apiForm() instead of api() because files can't be sent as JSON
    // Route: POST /api/docs/upload in main.py

    // ── Auto-login after successful signup ──
    setSession(res.accountNo);
    // Store account number in localStorage as session token
    // User is now considered logged in

    localStorage.setItem("resan_name", payload.name);
    // Cache name for sidebar display

    localStorage.setItem("resan_pin", payload.pin);
    // Cache PIN for dashboard auto-refresh on page reload

    refreshAuthUI();
    // Update sidebar to show user info instead of Login/Signup buttons

    closeModal();
    // Close the signup modal

    showPage("dashboard");
    // Navigate to the Dashboard page

    await loadDashboard();
    // Load and display the new account's dashboard data

    showToast(`Welcome, ${payload.name}! Acct: ${res.accountNo}`, "success");
    // Green welcome toast showing the new account number

  } catch (err) {
    showToast(err.message, "error");
    // Show backend error (e.g. "Invalid or expired OTP.")
  }
}


/* ─── LOGIN FLOW ─────────────────────────────────────────────── */
// Login happens in 2 steps:
//   Step 1 (modal-login): Enter account number + PIN → sends OTP
//   Step 2 (modal-otp-login): Enter 6-digit OTP → logs in

async function initiateLogin() {
  // Called when user clicks "Send OTP & Login" on the login modal
  // Validates credentials with backend, then shows OTP modal

  const accNo = document.getElementById("login-acc").value.trim().toUpperCase();
  // Account number entered by user — .toUpperCase() normalizes "rsn4821" to "RSN4821"

  const pin = parseInt(document.getElementById("login-pin").value);
  // 4-digit PIN as integer

  if (!accNo)
    return showToast("Enter your account number.", "error");
  if (isNaN(pin))
    return showToast("Enter your 4-digit PIN.", "error");
  // Basic frontend validation before calling backend

  try {
    const res = await api("/api/login/otp", "POST", { acc_no: accNo, pin });
    // Call backend to:
    //   1. Verify account exists and PIN is correct
    //   2. Generate and (in production) send OTP to registered phone
    // Route: POST /api/login/otp in main.py

    localStorage.setItem("resan_pin", pin);
    // Cache PIN for loadDashboard() to use after successful login

    closeModal();
    // Close the login form modal

    setTimeout(() => showModal("otp-login"), 300);
    // Open the OTP verification modal after a 300ms delay
    // The delay allows the close animation to complete before opening the next modal

    showToast(`OTP sent! Dev OTP: ${res.dev_otp}`, "info");
    // Show the dev OTP in a toast for testing
    // In production: OTP is sent via SMS, no dev_otp in response

  } catch (err) {
    showToast(err.message, "error");
    // e.g. "Account not found." or "Incorrect PIN." shown as red toast
  }
}

async function verifyLoginOTP() {
  // Called when user clicks "Verify & Login" on the OTP login modal
  // Completes the login process

  const entered = readOTPBoxes("login");
  // Read all 6 digits from lotp0–lotp5 boxes

  if (entered.length < 6)
    return showToast("Enter the full 6-digit OTP.", "error");

  const accNo = document.getElementById("login-acc").value.trim().toUpperCase();
  const pin   = parseInt(document.getElementById("login-pin").value);
  // Re-read account number and PIN from the login form
  // These fields are still populated from step 1

  try {
    const res = await api("/api/login/verify", "POST", {
      acc_no: accNo,
      pin,
      otp: entered
      // Send OTP string to backend for verification
    });
    // Route: POST /api/login/verify in main.py
    // Backend verifies OTP matches what was stored, then returns account info

    setSession(res.accountNo);
    // Store account number as session token in localStorage

    localStorage.setItem("resan_name", res.name);
    // Cache the user's name for sidebar display

    localStorage.setItem("resan_pin", pin);
    // Cache PIN for dashboard auto-reload

    refreshAuthUI();
    // Update sidebar to show user info (avatar, name, logout button)

    closeModal();
    // Close the OTP modal

    showPage("dashboard");
    // Navigate to Dashboard page

    await loadDashboard();
    // Fetch and display account data on the dashboard

    showToast(`Welcome back, ${res.name}!`, "success");
    // Green welcome toast e.g. "Welcome back, Richa!"

  } catch (err) {
    showToast(err.message, "error");
    // e.g. "Invalid or expired OTP." shown as red error
  }
}


/* ─── DASHBOARD ──────────────────────────────────────────────── */

async function loadDashboard() {
  // Fetches account data from backend and renders the Dashboard page
  // Called after: login, signup, clicking Dashboard in sidebar
  // Fills: balance card, account info stats, recent transactions list

  const accNo = getSession();
  // Get logged-in account number from localStorage

  const pin = parseInt(localStorage.getItem("resan_pin") || "0");
  // Get cached PIN from localStorage

  if (!accNo || !pin) return;
  // Not logged in or PIN not available — skip loading (nothing to show)

  try {
    const user = await api("/api/account/details", "POST", { acc_no: accNo, pin });
    // Fetch complete account data from backend
    // Returns: accountNo, name, age, email, balance, accountType, transactions, guardian

    document.getElementById("dash-balance").textContent =
      "₹" + user.balance.toLocaleString("en-IN", { minimumFractionDigits: 2 });
    // Format balance as Indian currency e.g. "₹1,05,000.00"
    // toLocaleString("en-IN") uses Indian number formatting (lakhs/crores)
    // Displayed in the large balance-amount div on the Dashboard

    document.getElementById("dash-accno").textContent  = user.accountNo;
    // Show account number chip below the balance e.g. "RSN4821"

    document.getElementById("dash-name").textContent   = user.name;
    // Account holder name in the stats row

    document.getElementById("dash-age").textContent    = user.age;
    // Age in the stats row

    document.getElementById("dash-email").textContent  = user.email;
    // Email in the stats row

    document.getElementById("dash-type").textContent   = user.accountType;
    // "Savings Account" or "Minor Account" in the stats row

    // ── Render transaction history ──
    const list   = document.getElementById("txn-list");
    // The div where transaction rows are rendered in index.html

    const myTxns = user.transactions || [];
    // Transaction array — default to empty array if not present

    list.innerHTML = myTxns.length === 0
      ? `<p class="muted">No transactions yet.</p>`
      // Show this placeholder when no transactions have been made yet
      : myTxns.map(t => `
          <div class="txn-item">
            <div>
              <div class="txn-type">${t.type}</div>
              <!-- "Deposit" or "Withdrawal" shown in transaction row -->
              <div class="txn-date">${t.date}</div>
              <!-- Date/time string e.g. "05 Apr 2025, 02:30 PM" -->
            </div>
            <div class="txn-amt ${t.type === "Deposit" ? "credit" : "debit"}">
              ${t.type === "Deposit" ? "+" : "−"}₹${t.amount.toLocaleString("en-IN")}
              <!-- Green "+₹5,000" for deposits, Red "−₹1,000" for withdrawals -->
              <!-- "credit" and "debit" CSS classes control green/red color in style.css -->
            </div>
          </div>
        `).join("");
    // .map() creates an HTML string for each transaction
    // .join("") combines all strings into one without separators
    // list.innerHTML renders them all at once

  } catch (err) {
    showToast("Could not load dashboard: " + err.message, "error");
    // Show error if backend is sleeping or returned an error
  }
}


/* ─── DEPOSIT ────────────────────────────────────────────────── */

async function handleDeposit() {
  // Called when user clicks "Deposit Now" on the Deposit page
  // Reads form inputs → validates → calls backend → shows result

  const accNo  = document.getElementById("dep-acc").value.trim().toUpperCase();
  // Account number from dep-acc input, normalized to uppercase

  const pin    = parseInt(document.getElementById("dep-pin").value);
  // 4-digit PIN from dep-pin input

  const amount = parseInt(document.getElementById("dep-amount").value);
  // Amount in rupees from dep-amount input (HTML input type="number")

  if (!accNo)
    return showToast("Enter your account number.", "error");
  if (isNaN(pin))
    return showToast("Enter your 4-digit PIN.", "error");
  if (!Number.isFinite(amount) || amount < 1)
    return showToast("Enter a valid amount.", "error");
  // Frontend validation before hitting the backend

  try {
    const res = await api("/api/deposit", "POST", { acc_no: accNo, pin, amount });
    // Call backend deposit route
    // Backend verifies PIN, adds to balance, records transaction
    // Route: POST /api/deposit in main.py

    showToast(res.message, "success");
    // Green toast: "₹5000 deposited successfully!"

    ["dep-acc","dep-pin","dep-amount"].forEach(id =>
      document.getElementById(id).value = "");
    // Clear all deposit form fields after success

    if (getSession() === accNo) await loadDashboard();
    // If the user just deposited into their OWN account,
    // refresh the dashboard to show the updated balance

  } catch (err) {
    showToast(err.message, "error");
    // e.g. "Incorrect PIN." or "Account not found."
  }
}


/* ─── WITHDRAW ───────────────────────────────────────────────── */

async function handleWithdraw() {
  // Called when user clicks "Withdraw" on the Withdraw page
  // Same flow as deposit but deducts money

  const accNo  = document.getElementById("with-acc").value.trim().toUpperCase();
  const pin    = parseInt(document.getElementById("with-pin").value);
  const amount = parseInt(document.getElementById("with-amount").value);

  if (!accNo)
    return showToast("Enter your account number.", "error");
  if (isNaN(pin))
    return showToast("Enter your 4-digit PIN.", "error");
  if (!Number.isFinite(amount) || amount < 1)
    return showToast("Enter a valid amount.", "error");

  try {
    const res = await api("/api/withdraw", "POST", { acc_no: accNo, pin, amount });
    // Call backend withdrawal route
    // Backend verifies PIN, checks sufficient balance, deducts, records transaction
    // Route: POST /api/withdraw in main.py

    showToast(res.message, "success");
    // Green toast: "₹2000 withdrawn successfully!"

    ["with-acc","with-pin","with-amount"].forEach(id =>
      document.getElementById(id).value = "");
    // Clear all withdraw form fields after success

    if (getSession() === accNo) await loadDashboard();
    // Refresh dashboard if user withdrew from their own account

  } catch (err) {
    showToast(err.message, "error");
    // e.g. "Insufficient balance." shown as red error toast
  }
}


/* ─── ACCOUNT DETAILS ────────────────────────────────────────── */

async function handleDetails() {
  // Called when user clicks "View Details" on the My Details page
  // Fetches and displays complete account information

  const accNo = document.getElementById("det-acc").value.trim().toUpperCase();
  const pin   = parseInt(document.getElementById("det-pin").value);

  if (!accNo || isNaN(pin))
    return showToast("Enter account number and PIN.", "error");

  try {
    const user = await api("/api/account/details", "POST", { acc_no: accNo, pin });
    // Fetch complete account data from backend
    // Route: POST /api/account/details in main.py

    document.getElementById("details-result").style.display = "block";
    // Show the results card (hidden by default with display:none in index.html)

    document.getElementById("det-balance").textContent =
      "₹" + user.balance.toLocaleString("en-IN", { minimumFractionDigits: 2 });
    // Show formatted balance in the results balance card

    document.getElementById("det-accno-chip").textContent = user.accountNo;
    // Show account number chip

    // ── Build the info table rows ──
    let fields = [
      ["Name",          user.name],
      ["Age",           user.age],
      ["Email",         user.email],
      ["Phone",         "+91 " + user.phone],
      // Phone displayed with Indian country code prefix
      ["Account Type",  user.accountType],
      ["Account No.",   user.accountNo],
      ["Docs Uploaded", user.docsUploaded ? "Yes ✓" : "No ✗"],
      // Shows checkmark or cross based on whether PDFs were uploaded
      ["Member Since",  new Date(user.createdAt).toLocaleDateString("en-IN")],
      // Convert ISO date string to Indian format e.g. "5/4/2025"
    ];

    if (user.guardian) {
      // Add guardian information rows for minor accounts
      fields.push(
        ["Guardian Name",  user.guardian.name],
        ["Relationship",   user.guardian.relationship],
        ["Guardian Phone", "+91 " + user.guardian.phone],
        ["Guardian Email", user.guardian.email],
      );
    }

    document.getElementById("details-table").innerHTML = fields.map(([k, v]) =>
      `<div class="info-row">
         <span class="info-key">${k}</span>
         <span class="info-val">${v}</span>
       </div>`
    ).join("");
    // Render all field rows as HTML in the details-table div
    // Each row has a label (info-key) and value (info-val)
    // Style.css handles the two-column layout for these rows

  } catch (err) {
    showToast(err.message, "error");
  }
}


/* ─── UPDATE ACCOUNT ─────────────────────────────────────────── */

async function handleUpdate() {
  // Called when user clicks "Save Changes" on the Update page
  // Only sends fields that the user actually filled in

  const accNo    = document.getElementById("upd-acc").value.trim().toUpperCase();
  const pin      = parseInt(document.getElementById("upd-pin").value);
  const newName  = document.getElementById("upd-name").value.trim();
  const newEmail = document.getElementById("upd-email").value.trim();
  const newPinRaw = document.getElementById("upd-newpin").value;
  const newPin   = newPinRaw ? parseInt(newPinRaw) : null;
  // null means "don't change PIN" — only update if user typed something

  if (!accNo || isNaN(pin))
    return showToast("Enter account number and current PIN.", "error");

  if (newEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(newEmail))
    return showToast("New email format is invalid.", "error");
  // Only validate email if user actually entered one (optional field)

  try {
    const res = await api("/api/account/update", "PUT", {
      acc_no:    accNo,
      pin,
      new_name:  newName  || null,
      // Send null if empty string — backend ignores null fields
      new_email: newEmail || null,
      new_pin:   newPin,
    });
    // Route: PUT /api/account/update in main.py

    showToast(res.message, "success");
    // Green toast: "Account updated successfully!"

    ["upd-acc","upd-pin","upd-name","upd-email","upd-newpin"]
      .forEach(id => document.getElementById(id).value = "");
    // Clear all update form fields after success

    if (newName && getSession() === accNo) {
      // If user updated their OWN name while logged in
      localStorage.setItem("resan_name", newName);
      // Update cached name in localStorage

      refreshAuthUI();
      // Immediately update the sidebar to show the new name
    }

  } catch (err) {
    showToast(err.message, "error");
  }
}


/* ─── CLOSE ACCOUNT ──────────────────────────────────────────── */

async function handleClose() {
  // Called when user clicks "Close My Account" on the Close Account page
  // Permanently deletes the account — user must tick the checkbox first

  const accNo   = document.getElementById("cls-acc").value.trim().toUpperCase();
  const pin     = parseInt(document.getElementById("cls-pin").value);
  const confirm = document.getElementById("cls-confirm").checked;
  // The checkbox in index.html that user must tick to confirm deletion

  if (!accNo || isNaN(pin))
    return showToast("Enter account number and PIN.", "error");

  if (!confirm)
    return showToast("Please tick the confirmation checkbox.", "error");
  // Cannot proceed without explicitly confirming the irreversible action

  try {
    const res = await api("/api/account/close", "DELETE", { acc_no: accNo, pin });
    // Send DELETE request to backend
    // Route: DELETE /api/account/close in main.py
    // Backend verifies PIN then deletes the account from accounts_db

    showToast(res.message, "success");
    // Green toast: "Account RSN4821 closed successfully."

    if (getSession() === accNo) {
      // If user just closed their OWN logged-in account
      clearSession();
      // Remove session token — they are no longer a customer

      localStorage.removeItem("resan_name");
      localStorage.removeItem("resan_pin");
      // Clear all cached data for this account

      refreshAuthUI();
      // Update sidebar back to Login/Signup buttons

      showPage("home");
      // Redirect to home page since they're no longer a member
    }

    ["cls-acc","cls-pin"].forEach(id => document.getElementById(id).value = "");
    document.getElementById("cls-confirm").checked = false;
    // Clear the form fields after submission

  } catch (err) {
    showToast(err.message, "error");
    // e.g. "Incorrect PIN." or "Account not found."
  }
}


/* ─── HOME PAGE STATS ────────────────────────────────────────── */

async function loadStats() {
  // Called on page load to populate live bank statistics on the Home page
  // Triggered in DOMContentLoaded below
  // Displays total number of accounts and total money in the bank

  try {
    const res = await api("/api/stats");
    // GET request to backend — no body needed
    // Route: GET /api/stats in main.py
    // Returns: { total_accounts: 5, total_balance: 125000 }

    const totalEl   = document.getElementById("stat-total-accounts");
    const balanceEl = document.getElementById("stat-total-balance");
    // Elements on the Home page that display the statistics

    if (totalEl)   totalEl.textContent   = res.total_accounts;
    // e.g. shows "5" for total accounts

    if (balanceEl) balanceEl.textContent = "₹" + res.total_balance.toLocaleString("en-IN");
    // e.g. shows "₹1,25,000" for total balance across all accounts

  } catch (_) {
    // Silently ignore errors — stats are non-critical
    // If backend is sleeping, the page still loads fine without stats
  }
}


/* ─── INITIALISATION ──────────────────────────────────────────── */

document.addEventListener("DOMContentLoaded", () => {
  // This runs once when the browser has fully loaded and parsed index.html
  // It's the entry point that starts up the entire application

  refreshAuthUI();
  // Check if user was already logged in from a previous session
  // If localStorage has "resan_session", show user info in sidebar immediately

  loadStats();
  // Fetch and display the bank's total accounts and balance on the Home page
  // Happens in the background — page is usable while this loads

  document.addEventListener("click", (e) => {
    // Global click listener for closing the mobile sidebar
    const sidebar   = document.getElementById("sidebar");
    const hamburger = document.querySelector(".hamburger");
    // The sidebar panel and the ☰ button that opens it

    if (
      sidebar.classList.contains("open") &&
      // Sidebar is currently open
      !sidebar.contains(e.target) &&
      // User clicked OUTSIDE the sidebar
      !hamburger.contains(e.target)
      // User did not click the hamburger button itself
    ) {
      sidebar.classList.remove("open");
      // Close the sidebar when user taps outside it on mobile
    }
  });
});