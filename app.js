/* ═══════════════════════════════════════════════════════════════
   app.js — ReSan Private Bank
   Frontend logic: calls Python FastAPI backend for all data ops.
   OTP and accounts are handled server-side via /api/* routes.
═══════════════════════════════════════════════════════════════ */

"use strict"; // Enable strict mode to catch silent JS errors

/* ─── CONFIG ─────────────────────────────────────────────────── */

// Base URL of the Python FastAPI backend.
// Change this to your deployed URL when going live (e.g. Render/Railway).
const BASE_URL = "http://localhost:8000";

/* ─── SESSION (localStorage) ─────────────────────────────────── */

function setSession(accNo) {
  localStorage.setItem("resan_session", accNo);  // Save account number as session token
}

function getSession() {
  return localStorage.getItem("resan_session");  // Retrieve session (null if not logged in)
}

function clearSession() {
  localStorage.removeItem("resan_session");      // Remove session on logout
}

/* ─── API HELPER ─────────────────────────────────────────────── */

// Generic JSON API call — wraps fetch with error handling
async function api(endpoint, method = "GET", body = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" }, // Tell server we're sending JSON
  };
  if (body) options.body = JSON.stringify(body);     // Stringify JS object to JSON

  const res  = await fetch(BASE_URL + endpoint, options); // Make HTTP request
  const data = await res.json();                         // Parse JSON response

  if (!res.ok) throw new Error(data.detail || "Something went wrong."); // Server error

  return data;
}

// Multipart form upload — for PDF file uploads (cannot use JSON for files)
async function apiForm(endpoint, formData) {
  const res  = await fetch(BASE_URL + endpoint, { method: "POST", body: formData });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Upload failed.");
  return data;
}

/* ─── PAGE NAVIGATION ─────────────────────────────────────────── */

function showPage(pageId) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active")); // Hide all pages
  const target = document.getElementById("page-" + pageId);
  if (target) target.classList.add("active");     // Show the target page

  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active")); // Clear highlights
  const navItem = document.querySelector(`[data-page="${pageId}"]`);
  if (navItem) navItem.classList.add("active");   // Highlight active nav item

  document.getElementById("sidebar").classList.remove("open"); // Close mobile sidebar
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open"); // Open/close mobile sidebar
}

/* ─── MODAL CONTROL ──────────────────────────────────────────── */

let currentModal = null; // Track which modal is open

function showModal(id) {
  closeModal();                                   // Close any open modal first
  const overlay = document.getElementById("modal-overlay");
  const modal   = document.getElementById("modal-" + id);
  if (!modal) return;
  overlay.classList.add("active");               // Show dark overlay behind modal
  modal.style.display = "block";
  requestAnimationFrame(() => modal.classList.add("active")); // Trigger CSS transition
  currentModal = id;
}

function closeModal() {
  if (!currentModal) return;
  document.getElementById("modal-overlay").classList.remove("active");
  const modal = document.getElementById("modal-" + currentModal);
  if (modal) {
    modal.classList.remove("active");
    setTimeout(() => (modal.style.display = "none"), 250); // Wait for fade-out
  }
  currentModal = null;
}

/* ─── TOAST NOTIFICATIONS ─────────────────────────────────────── */

let toastTimer = null;

function showToast(msg, type = "info") {
  const toast = document.getElementById("toast");
  document.getElementById("toast-msg").textContent = msg;
  toast.className = "toast " + type;             // Set color based on type
  toast.classList.add("show");                   // Slide up
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3500); // Auto-hide after 3.5s
}

/* ─── AUTH UI ─────────────────────────────────────────────────── */

async function refreshAuthUI() {
  const accNo    = getSession();
  const authBtns = document.getElementById("auth-buttons");
  const userInfo = document.getElementById("user-info");

  if (accNo) {
    authBtns.style.display = "none";             // Hide login/signup buttons
    userInfo.style.display  = "block";           // Show user info
    const cachedName = localStorage.getItem("resan_name") || accNo;
    document.getElementById("user-avatar").textContent = cachedName[0].toUpperCase(); // First letter
    document.getElementById("user-name").textContent   = cachedName;
  } else {
    authBtns.style.display = "block";            // Show login/signup buttons
    userInfo.style.display  = "none";
  }
}

function logout() {
  clearSession();                                // Remove session token
  localStorage.removeItem("resan_name");         // Clear cached name
  localStorage.removeItem("resan_pin");          // Clear cached PIN
  refreshAuthUI();
  showPage("home");
  showToast("Logged out successfully.", "success");
}

/* ─── INPUT VALIDATORS ───────────────────────────────────────── */

function validateNameInput(input) {
  const val   = input.value;
  const valid = /^[a-zA-Z\s]*$/.test(val);      // Letters and spaces only
  input.classList.toggle("error", !valid && val.length > 0);
  input.classList.toggle("valid", valid && val.trim().length >= 2);
  if (!valid) input.value = val.replace(/[^a-zA-Z\s]/g, ""); // Auto-strip invalid chars
}

function validateAgeInput(input) {
  const val      = parseInt(input.value);
  const validInt = Number.isInteger(val) && val >= 1 && val <= 120; // Must be whole number 1–120
  input.classList.toggle("error", !validInt && input.value.length > 0);
  input.classList.toggle("valid", validInt);
  if (input.value.includes(".")) input.value = Math.floor(parseFloat(input.value)); // Force integer
  const minorSection = document.getElementById("minor-section");
  if (minorSection) minorSection.style.display = (validInt && val < 18) ? "block" : "none"; // Show guardian form
}

function validateEmailInput(input) {
  const val   = input.value.trim();
  const valid = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val); // Standard email regex
  input.classList.toggle("error", !valid && val.length > 0);
  input.classList.toggle("valid", valid);
}

function validatePinInput(input) {
  input.value = input.value.replace(/\D/g, ""); // Strip non-digits
  const valid = /^\d{4}$/.test(input.value);    // Exactly 4 digits
  input.classList.toggle("error", !valid && input.value.length > 0);
  input.classList.toggle("valid", valid);
}

function validatePhoneInput(input) {
  input.value = input.value.replace(/\D/g, ""); // Strip non-digits
  const valid = /^\d{10}$/.test(input.value);   // Exactly 10 digits
  input.classList.toggle("error", !valid && input.value.length > 0);
  input.classList.toggle("valid", valid);
}

function validateAmount(input, maxVal) {
  let val = parseFloat(input.value);
  if (!Number.isFinite(val) || val <= 0) { input.classList.add("error"); return; }
  val = Math.floor(val);                         // Force integer — no paise
  input.value = val;
  input.classList.toggle("error", val < 1 || val > maxVal);
  input.classList.toggle("valid", val >= 1 && val <= maxVal);
}

function formatAccNo(input) {
  input.value = input.value.toUpperCase();       // Force uppercase for account numbers
}

/* ─── FILE UPLOAD ─────────────────────────────────────────────── */

function triggerFile(inputId) {
  document.getElementById(inputId).click();      // Trigger hidden file input
}

function handleFile(input, labelId) {
  const file = input.files[0];
  const box  = input.parentElement;
  if (!file) return;

  if (file.type !== "application/pdf") {         // Must be PDF
    showToast("Only PDF files are accepted.", "error");
    input.value = "";
    return;
  }
  if (file.size > 2 * 1024 * 1024) {            // Must be ≤ 2MB
    showToast("File too large. Maximum size is 2MB.", "error");
    input.value = "";
    return;
  }

  document.getElementById(labelId).textContent =
    `✓ ${file.name} (${(file.size / 1024).toFixed(1)} KB)`; // Show filename + size
  box.classList.add("uploaded");                 // Turn upload box green
}

/* ─── OTP BOXES ──────────────────────────────────────────────── */

function otpAdvance(input, index, prefix = "") {
  input.value = input.value.replace(/\D/g, ""); // Allow only digits
  if (input.value.length === 1 && index < 5) {
    const nextId = (prefix === "login" ? "lotp" : "otp") + (index + 1);
    const next   = document.getElementById(nextId);
    if (next) next.focus();                      // Move focus to next box
  }
}

function readOTPBoxes(prefix) {
  const ids = prefix === "login"
    ? ["lotp0","lotp1","lotp2","lotp3","lotp4","lotp5"]
    : ["otp0","otp1","otp2","otp3","otp4","otp5"];
  return ids.map(id => document.getElementById(id).value).join(""); // Combine all 6 digits
}

let otpCountdown = null;
function startOTPTimer() {
  let seconds = 30;
  document.getElementById("otp-countdown").textContent = seconds;
  document.getElementById("resend-btn").style.display  = "none"; // Hide resend button
  clearInterval(otpCountdown);
  otpCountdown = setInterval(() => {
    seconds--;
    document.getElementById("otp-countdown").textContent = seconds;
    if (seconds <= 0) {
      clearInterval(otpCountdown);
      document.getElementById("resend-btn").style.display = "inline"; // Show resend when timer ends
    }
  }, 1000);
}

/* ─── SIGNUP FLOW ─────────────────────────────────────────────── */

async function goStep2() {
  const name  = document.getElementById("su-name").value.trim();
  const age   = parseInt(document.getElementById("su-age").value);
  const email = document.getElementById("su-email").value.trim();
  const phone = document.getElementById("su-phone").value.trim();
  const pin   = document.getElementById("su-pin").value;

  if (!name || name.length < 2)              return showToast("Enter your full name (min 2 letters).", "error");
  if (!/^[a-zA-Z\s]+$/.test(name))          return showToast("Name must contain only letters.", "error");
  if (!Number.isInteger(age) || age < 1 || age > 120) return showToast("Enter a valid age (1–120).", "error");

  // Extra validation for minor accounts
  if (age < 18) {
    const gname  = document.getElementById("su-gname").value.trim();
    const gage   = parseInt(document.getElementById("su-gage").value);
    const rel    = document.getElementById("su-relation").value;
    const gphone = document.getElementById("su-gphone").value.trim();
    const gemail = document.getElementById("su-gemail").value.trim();
    const gdoc   = document.getElementById("guardian-doc").files[0];
    if (!gname)                                    return showToast("Guardian name is required.", "error");
    if (!Number.isInteger(gage) || gage < 18)      return showToast("Guardian must be 18 or older.", "error");
    if (!rel)                                      return showToast("Select guardian relationship.", "error");
    if (!/^\d{10}$/.test(gphone))                 return showToast("Guardian phone must be 10 digits.", "error");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(gemail)) return showToast("Enter a valid guardian email.", "error");
    if (!gdoc)                                     return showToast("Upload guardian ID PDF.", "error");
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return showToast("Enter a valid email address.", "error");
  if (!/^\d{10}$/.test(phone))                   return showToast("Phone must be exactly 10 digits.", "error");
  if (!/^\d{4}$/.test(pin))                      return showToast("PIN must be exactly 4 digits.", "error");

  document.getElementById("signup-step1").style.display = "none";
  document.getElementById("signup-step2").style.display = "block";
  document.getElementById("step1-dot").classList.add("done");
  document.getElementById("step2-dot").classList.add("active");
}

function goStep1() {
  document.getElementById("signup-step2").style.display = "none";
  document.getElementById("signup-step1").style.display = "block";
  document.getElementById("step2-dot").classList.remove("active");
}

async function goStep3() {
  if (!document.getElementById("aadhaar-doc").files[0])     return showToast("Upload Aadhaar PDF.", "error");
  if (!document.getElementById("pan-doc").files[0])         return showToast("Upload PAN Card PDF.", "error");
  if (!document.getElementById("address-doc").files[0])     return showToast("Upload Address Proof PDF.", "error");

  const phone = document.getElementById("su-phone").value.trim();
  try {
    const res = await api("/api/otp/send", "POST", { phone }); // Call backend to send OTP
    startOTPTimer();
    document.getElementById("otp-phone-display").textContent = "+91 " + phone;
    document.getElementById("signup-step2").style.display = "none";
    document.getElementById("signup-step3").style.display = "block";
    document.getElementById("step2-dot").classList.add("done");
    document.getElementById("step3-dot").classList.add("active");
    showToast(`OTP sent! Dev OTP: ${res.dev_otp}`, "info"); // Show OTP in dev mode
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function resendOTP() {
  const phone = document.getElementById("su-phone").value.trim();
  try {
    const res = await api("/api/otp/send", "POST", { phone });
    startOTPTimer();
    showToast(`OTP resent! Dev OTP: ${res.dev_otp}`, "info");
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function verifyAndCreate() {
  const enteredOTP = readOTPBoxes("");           // Collect OTP from 6 digit boxes
  if (enteredOTP.length < 6) return showToast("Enter the full 6-digit OTP.", "error");

  const age     = parseInt(document.getElementById("su-age").value);
  const isMinor = age < 18;

  // Build request payload matching backend SignupRequest model
  const payload = {
    name:  document.getElementById("su-name").value.trim(),
    age,
    email: document.getElementById("su-email").value.trim(),
    phone: document.getElementById("su-phone").value.trim(),
    pin:   parseInt(document.getElementById("su-pin").value),
    otp:   enteredOTP,
  };

  if (isMinor) {                                 // Add guardian fields for minor accounts
    payload.guardian_name     = document.getElementById("su-gname").value.trim();
    payload.guardian_age      = parseInt(document.getElementById("su-gage").value);
    payload.guardian_relation = document.getElementById("su-relation").value;
    payload.guardian_phone    = document.getElementById("su-gphone").value.trim();
    payload.guardian_email    = document.getElementById("su-gemail").value.trim();
  }

  try {
    const res = await api("/api/account/create", "POST", payload); // Create account

    // Upload documents after account creation
    const formData = new FormData();
    formData.append("acc_no",         res.accountNo);
    formData.append("pin",            payload.pin);
    formData.append("aadhaar",        document.getElementById("aadhaar-doc").files[0]);
    formData.append("pan",            document.getElementById("pan-doc").files[0]);
    formData.append("address_proof",  document.getElementById("address-doc").files[0]);
    if (isMinor && document.getElementById("guardian-doc").files[0]) {
      formData.append("guardian_doc", document.getElementById("guardian-doc").files[0]);
    }
    await apiForm("/api/docs/upload", formData);  // Upload all PDFs to backend

    // Auto-login after signup
    setSession(res.accountNo);
    localStorage.setItem("resan_name", payload.name);
    localStorage.setItem("resan_pin",  payload.pin);
    refreshAuthUI();
    closeModal();
    showPage("dashboard");
    await loadDashboard();
    showToast(`Welcome, ${payload.name}! Acct: ${res.accountNo}`, "success");

  } catch (err) {
    showToast(err.message, "error");
  }
}

/* ─── LOGIN FLOW ─────────────────────────────────────────────── */

async function initiateLogin() {
  const accNo = document.getElementById("login-acc").value.trim().toUpperCase();
  const pin   = parseInt(document.getElementById("login-pin").value);

  if (!accNo)     return showToast("Enter your account number.", "error");
  if (isNaN(pin)) return showToast("Enter your 4-digit PIN.", "error");

  try {
    const res = await api("/api/login/otp", "POST", { acc_no: accNo, pin }); // Verify credentials & send OTP
    localStorage.setItem("resan_pin", pin);       // Cache PIN for dashboard reload
    closeModal();
    setTimeout(() => showModal("otp-login"), 300); // Open OTP modal
    showToast(`OTP sent! Dev OTP: ${res.dev_otp}`, "info");
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function verifyLoginOTP() {
  const entered = readOTPBoxes("login");
  if (entered.length < 6) return showToast("Enter the full 6-digit OTP.", "error");

  const accNo = document.getElementById("login-acc").value.trim().toUpperCase();
  const pin   = parseInt(document.getElementById("login-pin").value);

  try {
    const res = await api("/api/login/verify", "POST", { acc_no: accNo, pin, otp: entered }); // Verify OTP
    setSession(res.accountNo);
    localStorage.setItem("resan_name", res.name);
    localStorage.setItem("resan_pin",  pin);
    refreshAuthUI();
    closeModal();
    showPage("dashboard");
    await loadDashboard();
    showToast(`Welcome back, ${res.name}!`, "success");
  } catch (err) {
    showToast(err.message, "error");
  }
}

/* ─── DASHBOARD ──────────────────────────────────────────────── */

async function loadDashboard() {
  const accNo = getSession();
  const pin   = parseInt(localStorage.getItem("resan_pin") || "0");
  if (!accNo || !pin) return;                    // Not logged in — skip

  try {
    const user = await api("/api/account/details", "POST", { acc_no: accNo, pin });

    document.getElementById("dash-balance").textContent =
      "₹" + user.balance.toLocaleString("en-IN", { minimumFractionDigits: 2 });
    document.getElementById("dash-accno").textContent  = user.accountNo;
    document.getElementById("dash-name").textContent   = user.name;
    document.getElementById("dash-age").textContent    = user.age;
    document.getElementById("dash-email").textContent  = user.email;
    document.getElementById("dash-type").textContent   = user.accountType;

    // Render transaction rows
    const list   = document.getElementById("txn-list");
    const myTxns = user.transactions || [];
    list.innerHTML = myTxns.length === 0
      ? `<p class="muted">No transactions yet.</p>`
      : myTxns.map(t => `
          <div class="txn-item">
            <div>
              <div class="txn-type">${t.type}</div>
              <div class="txn-date">${t.date}</div>
            </div>
            <div class="txn-amt ${t.type === "Deposit" ? "credit" : "debit"}">
              ${t.type === "Deposit" ? "+" : "−"}₹${t.amount.toLocaleString("en-IN")}
            </div>
          </div>
        `).join("");

  } catch (err) {
    showToast("Could not load dashboard: " + err.message, "error");
  }
}

/* ─── DEPOSIT ────────────────────────────────────────────────── */

async function handleDeposit() {
  const accNo  = document.getElementById("dep-acc").value.trim().toUpperCase();
  const pin    = parseInt(document.getElementById("dep-pin").value);
  const amount = parseInt(document.getElementById("dep-amount").value);

  if (!accNo)                                return showToast("Enter your account number.", "error");
  if (isNaN(pin))                            return showToast("Enter your 4-digit PIN.", "error");
  if (!Number.isFinite(amount) || amount < 1) return showToast("Enter a valid amount.", "error");

  try {
    const res = await api("/api/deposit", "POST", { acc_no: accNo, pin, amount });
    showToast(res.message, "success");
    ["dep-acc","dep-pin","dep-amount"].forEach(id => document.getElementById(id).value = "");
    if (getSession() === accNo) await loadDashboard(); // Refresh dashboard if own account
  } catch (err) {
    showToast(err.message, "error");
  }
}

/* ─── WITHDRAW ───────────────────────────────────────────────── */

async function handleWithdraw() {
  const accNo  = document.getElementById("with-acc").value.trim().toUpperCase();
  const pin    = parseInt(document.getElementById("with-pin").value);
  const amount = parseInt(document.getElementById("with-amount").value);

  if (!accNo)                                return showToast("Enter your account number.", "error");
  if (isNaN(pin))                            return showToast("Enter your 4-digit PIN.", "error");
  if (!Number.isFinite(amount) || amount < 1) return showToast("Enter a valid amount.", "error");

  try {
    const res = await api("/api/withdraw", "POST", { acc_no: accNo, pin, amount });
    showToast(res.message, "success");
    ["with-acc","with-pin","with-amount"].forEach(id => document.getElementById(id).value = "");
    if (getSession() === accNo) await loadDashboard();
  } catch (err) {
    showToast(err.message, "error");
  }
}

/* ─── ACCOUNT DETAILS ────────────────────────────────────────── */

async function handleDetails() {
  const accNo = document.getElementById("det-acc").value.trim().toUpperCase();
  const pin   = parseInt(document.getElementById("det-pin").value);
  if (!accNo || isNaN(pin)) return showToast("Enter account number and PIN.", "error");

  try {
    const user = await api("/api/account/details", "POST", { acc_no: accNo, pin });

    document.getElementById("details-result").style.display = "block";
    document.getElementById("det-balance").textContent =
      "₹" + user.balance.toLocaleString("en-IN", { minimumFractionDigits: 2 });
    document.getElementById("det-accno-chip").textContent = user.accountNo;

    let fields = [
      ["Name",         user.name],
      ["Age",          user.age],
      ["Email",        user.email],
      ["Phone",        "+91 " + user.phone],
      ["Account Type", user.accountType],
      ["Account No.",  user.accountNo],
      ["Docs Uploaded",user.docsUploaded ? "Yes ✓" : "No ✗"],
      ["Member Since", new Date(user.createdAt).toLocaleDateString("en-IN")],
    ];
    if (user.guardian) {                         // Add guardian fields for minors
      fields.push(
        ["Guardian Name",  user.guardian.name],
        ["Relationship",   user.guardian.relationship],
        ["Guardian Phone", "+91 " + user.guardian.phone],
        ["Guardian Email", user.guardian.email],
      );
    }

    document.getElementById("details-table").innerHTML = fields.map(([k, v]) =>
      `<div class="info-row"><span class="info-key">${k}</span><span class="info-val">${v}</span></div>`
    ).join("");

  } catch (err) {
    showToast(err.message, "error");
  }
}

/* ─── UPDATE ACCOUNT ─────────────────────────────────────────── */

async function handleUpdate() {
  const accNo    = document.getElementById("upd-acc").value.trim().toUpperCase();
  const pin      = parseInt(document.getElementById("upd-pin").value);
  const newName  = document.getElementById("upd-name").value.trim();
  const newEmail = document.getElementById("upd-email").value.trim();
  const newPinRaw = document.getElementById("upd-newpin").value;
  const newPin   = newPinRaw ? parseInt(newPinRaw) : null;

  if (!accNo || isNaN(pin)) return showToast("Enter account number and current PIN.", "error");
  if (newEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(newEmail))
    return showToast("New email format is invalid.", "error");

  try {
    const res = await api("/api/account/update", "PUT", {
      acc_no: accNo, pin,
      new_name:  newName  || null,               // null means "don't update this field"
      new_email: newEmail || null,
      new_pin:   newPin,
    });
    showToast(res.message, "success");
    ["upd-acc","upd-pin","upd-name","upd-email","upd-newpin"]
      .forEach(id => document.getElementById(id).value = "");
    if (newName && getSession() === accNo) {
      localStorage.setItem("resan_name", newName); // Update cached name
      refreshAuthUI();
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

/* ─── CLOSE ACCOUNT ──────────────────────────────────────────── */

async function handleClose() {
  const accNo   = document.getElementById("cls-acc").value.trim().toUpperCase();
  const pin     = parseInt(document.getElementById("cls-pin").value);
  const confirm = document.getElementById("cls-confirm").checked; // Must tick checkbox

  if (!accNo || isNaN(pin)) return showToast("Enter account number and PIN.", "error");
  if (!confirm)             return showToast("Please tick the confirmation checkbox.", "error");

  try {
    const res = await api("/api/account/close", "DELETE", { acc_no: accNo, pin });
    showToast(res.message, "success");
    if (getSession() === accNo) {                // Logout if closed own account
      clearSession();
      localStorage.removeItem("resan_name");
      localStorage.removeItem("resan_pin");
      refreshAuthUI();
      showPage("home");
    }
    ["cls-acc","cls-pin"].forEach(id => document.getElementById(id).value = "");
    document.getElementById("cls-confirm").checked = false;
  } catch (err) {
    showToast(err.message, "error");
  }
}

/* ─── HOME PAGE STATS ────────────────────────────────────────── */

async function loadStats() {
  try {
    const res = await api("/api/stats");          // Fetch aggregate stats from backend
    const totalEl   = document.getElementById("stat-total-accounts");
    const balanceEl = document.getElementById("stat-total-balance");
    if (totalEl)   totalEl.textContent   = res.total_accounts;
    if (balanceEl) balanceEl.textContent = "₹" + res.total_balance.toLocaleString("en-IN");
  } catch (_) { /* Non-critical — silently ignore */ }
}

/* ─── INIT ────────────────────────────────────────────────────── */

document.addEventListener("DOMContentLoaded", () => {
  refreshAuthUI();  // Check for existing session on page load
  loadStats();      // Load home page stats from backend

  // Close sidebar on outside click (mobile UX)
  document.addEventListener("click", (e) => {
    const sidebar   = document.getElementById("sidebar");
    const hamburger = document.querySelector(".hamburger");
    if (
      sidebar.classList.contains("open") &&
      !sidebar.contains(e.target) &&
      !hamburger.contains(e.target)
    ) {
      sidebar.classList.remove("open");
    }
  });
});
