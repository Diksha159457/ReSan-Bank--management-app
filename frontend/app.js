/* ── Config ─────────────────────────────────────────────────────────────── */
const API = '';   // Same origin — FastAPI serves this frontend

/* ── State ──────────────────────────────────────────────────────────────── */
let session = { accNo: null, name: null };

/* ── Theme ──────────────────────────────────────────────────────────────── */
const themeBtn   = document.getElementById('themeBtn');
const moonPath   = document.getElementById('moonPath');
const sunCircle  = document.getElementById('sunCircle');
const sunRays    = document.getElementById('sunRays');
const html       = document.documentElement;

function applyTheme(theme) {
  html.setAttribute('data-theme', theme);
  localStorage.setItem('rs-theme', theme);
  const isDark = theme === 'dark';
  moonPath.style.display  = isDark ? 'block' : 'none';
  sunCircle.style.display = isDark ? 'none'  : 'block';
  sunRays.style.display   = isDark ? 'none'  : 'block';
}

themeBtn.addEventListener('click', () => {
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  applyTheme(next);
});

// Init theme
applyTheme(localStorage.getItem('rs-theme') || 'dark');

/* ── Navigation ─────────────────────────────────────────────────────────── */
function goTo(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + page)?.classList.add('active');
  document.querySelector(`.nav-item[data-page="${page}"]`)?.classList.add('active');
  closeSidebar();
  window.scrollTo(0, 0);
}

document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => goTo(btn.dataset.page));
});

/* ── Sidebar (mobile) ───────────────────────────────────────────────────── */
const sidebar = document.getElementById('sidebar');
let overlay;

function toggleSidebar() {
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'overlay';
    overlay.onclick = closeSidebar;
    document.body.appendChild(overlay);
  }
  sidebar.classList.toggle('open');
  overlay.classList.toggle('show');
}
function closeSidebar() {
  sidebar.classList.remove('open');
  if (overlay) overlay.classList.remove('show');
}

/* ── Toast ──────────────────────────────────────────────────────────────── */
let toastTimer;
function showToast(msg, type = 'info') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast ' + type + ' show';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 3800);
}

/* ── Message helpers ────────────────────────────────────────────────────── */
function setMsg(id, text, type = 'info') {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text;
  el.className = 'msg ' + type;
}
function clearMsg(id) {
  const el = document.getElementById(id);
  if (el) { el.textContent = ''; el.className = 'msg'; }
}

/* ── API helper ─────────────────────────────────────────────────────────── */
async function apiCall(method, path, body = null, isForm = false) {
  const opts = { method, headers: {} };
  if (body) {
    if (isForm) {
      opts.body = body;
    } else {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
  }
  const res = await fetch(API + path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

/* ── OTP ─────────────────────────────────────────────────────────────────── */
async function sendOTP(prefix) {
  const phone = document.getElementById(prefix + '-phone').value.trim();
  if (!phone || phone.length !== 10) { setMsg(prefix + '-msg', 'Enter a valid 10-digit phone number.', 'error'); return; }
  try {
    const d = await apiCall('POST', '/api/otp/send', { phone });
    const hint = d.dev_otp ? ` (Dev OTP: ${d.dev_otp})` : ' Check your phone.';
    setMsg(prefix + '-msg', d.message + hint, 'info');
    showToast('OTP sent to ' + phone);
  } catch (e) { setMsg(prefix + '-msg', e.message, 'error'); }
}

/* ── REGISTER ────────────────────────────────────────────────────────────── */
document.getElementById('reg-age').addEventListener('input', function() {
  document.getElementById('guardianSection').style.display = +this.value < 18 ? 'block' : 'none';
});

async function registerAccount() {
  clearMsg('reg-msg');
  const name  = document.getElementById('reg-name').value.trim();
  const age   = +document.getElementById('reg-age').value;
  const email = document.getElementById('reg-email').value.trim();
  const phone = document.getElementById('reg-phone').value.trim();
  const pin   = +document.getElementById('reg-pin').value;
  const otp   = document.getElementById('reg-otp').value.trim();

  if (!name || !age || !email || !phone || !pin || !otp) {
    setMsg('reg-msg', 'Please fill all required fields.', 'error'); return;
  }

  const payload = { name, age, email, phone, pin: pin, otp };
  if (age < 18) {
    payload.guardian_name     = document.getElementById('g-name').value.trim();
    payload.guardian_age      = +document.getElementById('g-age').value;
    payload.guardian_relation = document.getElementById('g-relation').value.trim();
    payload.guardian_phone    = document.getElementById('g-phone').value.trim();
    payload.guardian_email    = document.getElementById('g-email').value.trim();
  }

  try {
    const d = await apiCall('POST', '/api/account/create', payload);
    setMsg('reg-msg', `✅ Account created! Your Account No: ${d.accountNo}`, 'success');
    showToast('Welcome, ' + d.name + '!', 'success');
    loadStats();
  } catch (e) { setMsg('reg-msg', e.message, 'error'); }
}

/* ── LOGIN ───────────────────────────────────────────────────────────────── */
async function loginSendOTP() {
  clearMsg('login-msg');
  const acc_no = document.getElementById('login-acc').value.trim().toUpperCase();
  const pin    = +document.getElementById('login-pin').value;
  if (!acc_no || !pin) { setMsg('login-msg', 'Enter account number and PIN.', 'error'); return; }

  try {
    const d = await apiCall('POST', '/api/login/otp', { acc_no, pin });
    const hint = d.dev_otp ? ` (Dev OTP: ${d.dev_otp})` : ' Check your registered phone.';
    setMsg('login-msg', d.message + hint, 'info');
    document.getElementById('loginOTPArea').style.display = 'block';
    document.getElementById('loginSendOTPBtn').style.display = 'none';
  } catch (e) { setMsg('login-msg', e.message, 'error'); }
}

async function verifyLoginOTP() {
  clearMsg('login-msg');
  const acc_no = document.getElementById('login-acc').value.trim().toUpperCase();
  const pin    = +document.getElementById('login-pin').value;
  const otp    = document.getElementById('login-otp').value.trim();
  try {
    const d = await apiCall('POST', '/api/login/verify', { acc_no, pin, otp });
    session = { accNo: d.accountNo, name: d.name };
    updateSession();
    setMsg('login-msg', `✅ Welcome back, ${d.name}!`, 'success');
    showToast('Logged in as ' + d.name, 'success');
    document.getElementById('loginOTPArea').style.display = 'none';
    document.getElementById('loginSendOTPBtn').style.display = 'block';
    // Pre-fill dashboard
    document.getElementById('dash-acc').value = d.accountNo;
    document.getElementById('dep-acc').value  = d.accountNo;
    document.getElementById('with-acc').value = d.accountNo;
    document.getElementById('tr-from').value  = d.accountNo;
    document.getElementById('tx-acc').value   = d.accountNo;
    document.getElementById('upd-acc').value  = d.accountNo;
    setTimeout(() => goTo('dashboard'), 1200);
  } catch (e) { setMsg('login-msg', e.message, 'error'); }
}

function updateSession() {
  const si = document.getElementById('sessionInfo');
  const lb = document.getElementById('logoutBtn');
  if (session.accNo) {
    si.style.display = 'flex';
    lb.style.display = 'block';
    document.getElementById('sessionName').textContent = session.name;
    document.getElementById('sessionAcc').textContent  = session.accNo;
  } else {
    si.style.display = 'none';
    lb.style.display = 'none';
  }
}

function logout() {
  session = { accNo: null, name: null };
  updateSession();
  goTo('home');
  showToast('Signed out successfully.');
}

/* ── DASHBOARD ───────────────────────────────────────────────────────────── */
async function loadDashboard() {
  clearMsg('dash-msg');
  const acc_no = document.getElementById('dash-acc').value.trim().toUpperCase();
  const pin    = +document.getElementById('dash-pin').value;
  if (!acc_no || !pin) { setMsg('dash-msg', 'Enter account number and PIN.', 'error'); return; }

  try {
    const d = await apiCall('POST', '/api/account/details', { acc_no, pin });
    document.getElementById('dashLoginCard').style.display = 'none';
    document.getElementById('dashContent').style.display = 'block';

    document.getElementById('dash-balance').textContent = fmt(d.balance);
    document.getElementById('dash-type').textContent    = d.accountType;
    document.getElementById('dash-accno').textContent   = d.accountNo;
    document.getElementById('dash-name').textContent    = d.name;
    document.getElementById('dash-email').textContent   = d.email;
    document.getElementById('dash-age').textContent     = d.age + ' years';
    document.getElementById('dash-since').textContent   = new Date(d.createdAt).toLocaleDateString('en-IN', { year:'numeric', month:'long', day:'numeric' });
    document.getElementById('dash-docs').textContent    = d.docsUploaded ? '✅ Verified' : '❌ Pending';

    // Recent transactions
    const recent = (d.transactions || []).slice(0, 5);
    const rc = document.getElementById('dashRecent');
    if (recent.length) {
      rc.innerHTML = `<h3>Recent Transactions</h3>` + recent.map(renderTx).join('');
    } else {
      rc.innerHTML = `<h3>Recent Transactions</h3><div class="tx-empty">No transactions yet.</div>`;
    }
  } catch (e) {
    setMsg('dash-msg', e.message, 'error');
  }
}

/* ── DEPOSIT ─────────────────────────────────────────────────────────────── */
async function doDeposit() {
  clearMsg('dep-msg');
  const acc_no = document.getElementById('dep-acc').value.trim().toUpperCase();
  const pin    = +document.getElementById('dep-pin').value;
  const amount = +document.getElementById('dep-amt').value;
  if (!acc_no || !pin || !amount) { setMsg('dep-msg', 'Fill all fields.', 'error'); return; }
  try {
    const d = await apiCall('POST', '/api/deposit', { acc_no, pin, amount });
    setMsg('dep-msg', `${d.message} New balance: ${fmt(d.new_balance)}`, 'success');
    showToast(d.message, 'success');
    document.getElementById('dep-amt').value = '';
  } catch (e) { setMsg('dep-msg', e.message, 'error'); }
}

/* ── WITHDRAW ────────────────────────────────────────────────────────────── */
async function doWithdraw() {
  clearMsg('with-msg');
  const acc_no = document.getElementById('with-acc').value.trim().toUpperCase();
  const pin    = +document.getElementById('with-pin').value;
  const amount = +document.getElementById('with-amt').value;
  if (!acc_no || !pin || !amount) { setMsg('with-msg', 'Fill all fields.', 'error'); return; }
  try {
    const d = await apiCall('POST', '/api/withdraw', { acc_no, pin, amount });
    setMsg('with-msg', `${d.message} New balance: ${fmt(d.new_balance)}`, 'success');
    showToast(d.message, 'success');
    document.getElementById('with-amt').value = '';
  } catch (e) { setMsg('with-msg', e.message, 'error'); }
}

/* ── TRANSFER ────────────────────────────────────────────────────────────── */
async function doTransfer() {
  clearMsg('tr-msg');
  const from_acc = document.getElementById('tr-from').value.trim().toUpperCase();
  const pin      = +document.getElementById('tr-pin').value;
  const to_acc   = document.getElementById('tr-to').value.trim().toUpperCase();
  const amount   = +document.getElementById('tr-amt').value;
  if (!from_acc || !pin || !to_acc || !amount) { setMsg('tr-msg', 'Fill all fields.', 'error'); return; }
  try {
    const d = await apiCall('POST', '/api/transfer', { from_acc, pin, to_acc, amount });
    setMsg('tr-msg', `${d.message} New balance: ${fmt(d.new_balance)}`, 'success');
    showToast(d.message, 'success');
    document.getElementById('tr-amt').value = '';
  } catch (e) { setMsg('tr-msg', e.message, 'error'); }
}

/* ── TRANSACTIONS ────────────────────────────────────────────────────────── */
async function loadTransactions() {
  clearMsg('tx-msg');
  const acc_no = document.getElementById('tx-acc').value.trim().toUpperCase();
  const pin    = +document.getElementById('tx-pin').value;
  if (!acc_no || !pin) { setMsg('tx-msg', 'Enter account number and PIN.', 'error'); return; }
  try {
    const d = await apiCall('GET', `/api/transactions/${acc_no}?pin=${pin}`);
    document.getElementById('txLoginCard').style.display = 'none';
    document.getElementById('txContent').style.display   = 'block';
    document.getElementById('tx-balance').textContent    = fmt(d.balance);

    const txl = document.getElementById('txList');
    if (!d.transactions || d.transactions.length === 0) {
      txl.innerHTML = '<div class="tx-empty">No transactions found.</div>';
    } else {
      txl.innerHTML = d.transactions.map(renderTx).join('');
    }
  } catch (e) { setMsg('tx-msg', e.message, 'error'); }
}

function renderTx(tx) {
  const type = tx.type || '';
  let cls = 'debit', icon = '↑', amtCls = 'debit';
  if (type === 'Credit' || type === 'Deposit' || type === 'Transfer In') {
    cls = 'credit'; icon = '↓'; amtCls = type === 'Transfer In' ? 'transfer-in' : 'credit';
  } else if (type === 'Transfer Out') {
    cls = 'transfer'; icon = '⇄'; amtCls = 'transfer-out';
  }
  const sign = (amtCls === 'credit' || amtCls === 'transfer-in') ? '+' : '-';
  return `
    <div class="tx-item">
      <div class="tx-left">
        <div class="tx-dot ${cls}">${icon}</div>
        <div>
          <div class="tx-type">${type}</div>
          <div class="tx-date">${tx.date || ''}</div>
        </div>
      </div>
      <div class="tx-amount ${amtCls}">${sign}${fmt(tx.amount)}</div>
    </div>`;
}

/* ── UPLOAD ──────────────────────────────────────────────────────────────── */
async function uploadDocs() {
  clearMsg('up-msg');
  const acc_no = document.getElementById('up-acc').value.trim().toUpperCase();
  const pin    = document.getElementById('up-pin').value;
  const aadhaar = document.getElementById('up-aadhaar').files[0];
  const pan     = document.getElementById('up-pan').files[0];
  const address = document.getElementById('up-address').files[0];
  const guardian= document.getElementById('up-guardian').files[0];

  if (!acc_no || !pin || !aadhaar || !pan || !address) {
    setMsg('up-msg', 'Account number, PIN, and all 3 documents are required.', 'error'); return;
  }

  const fd = new FormData();
  fd.append('acc_no', acc_no);
  fd.append('pin', pin);
  fd.append('aadhaar', aadhaar);
  fd.append('pan', pan);
  fd.append('address_proof', address);
  if (guardian) fd.append('guardian_doc', guardian);

  try {
    const d = await apiCall('POST', '/api/docs/upload', fd, true);
    setMsg('up-msg', d.message, 'success');
    showToast('Documents uploaded!', 'success');
  } catch (e) { setMsg('up-msg', e.message, 'error'); }
}

/* ── UPDATE ──────────────────────────────────────────────────────────────── */
async function updateAccount() {
  clearMsg('upd-msg');
  const acc_no    = document.getElementById('upd-acc').value.trim().toUpperCase();
  const pin       = +document.getElementById('upd-pin').value;
  const new_name  = document.getElementById('upd-name').value.trim() || null;
  const new_email = document.getElementById('upd-email').value.trim() || null;
  const np        = document.getElementById('upd-newpin').value;
  const new_pin   = np ? +np : null;
  if (!acc_no || !pin) { setMsg('upd-msg', 'Account number and current PIN are required.', 'error'); return; }
  if (!new_name && !new_email && !new_pin) { setMsg('upd-msg', 'Enter at least one field to update.', 'error'); return; }
  try {
    const d = await apiCall('PUT', '/api/account/update', { acc_no, pin, new_name, new_email, new_pin });
    setMsg('upd-msg', d.message, 'success');
    showToast('Profile updated!', 'success');
  } catch (e) { setMsg('upd-msg', e.message, 'error'); }
}

/* ── CLOSE ───────────────────────────────────────────────────────────────── */
async function closeAccount() {
  clearMsg('cls-msg');
  const acc_no  = document.getElementById('cls-acc').value.trim().toUpperCase();
  const pin     = +document.getElementById('cls-pin').value;
  const confirm = document.getElementById('cls-confirm').value.trim();
  if (confirm !== 'DELETE') { setMsg('cls-msg', 'Type DELETE exactly to confirm.', 'error'); return; }
  if (!acc_no || !pin) { setMsg('cls-msg', 'Enter account number and PIN.', 'error'); return; }
  try {
    const d = await apiCall('DELETE', '/api/account/close', { acc_no, pin });
    setMsg('cls-msg', d.message, 'success');
    showToast('Account closed.', 'info');
    if (session.accNo === acc_no) logout();
    loadStats();
  } catch (e) { setMsg('cls-msg', e.message, 'error'); }
}

/* ── Helpers ─────────────────────────────────────────────────────────────── */
function fmt(n) {
  return '₹' + Number(n || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function setAmount(id, val) {
  document.getElementById(id).value = val;
}

/* ── Stats ───────────────────────────────────────────────────────────────── */
async function loadStats() {
  try {
    const d = await apiCall('GET', '/api/stats');
    document.getElementById('stat-accounts').textContent = d.total_accounts;
    document.getElementById('stat-balance').textContent  = fmt(d.total_balance);
    document.getElementById('stat-savings').textContent  = d.savings_accounts ?? '—';
    document.getElementById('stat-minor').textContent    = d.minor_accounts ?? '—';
  } catch (_) {}
}

/* ── Init ────────────────────────────────────────────────────────────────── */
loadStats();
