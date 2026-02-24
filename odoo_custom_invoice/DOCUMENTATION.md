# odoo_custom_invoice — Module Documentation

**Module Name:** `odoo_custom_invoice`  
**Version:** 15.0.1.0.29  
**Author:** AM Odoo Solutions  
**Last Updated:** 2026-02-24  
**Depends:** `account`, `point_of_sale`

---

## 📋 Table of Contents

1. [Module Overview](#module-overview)
2. [Module Structure](#module-structure)
3. [Complete Flow Diagram](#complete-flow-diagram)
4. [File-by-File Breakdown](#file-by-file-breakdown)
5. [Previous Credit — Core Logic](#previous-credit--core-logic)
6. [Report System](#report-system)
7. [Known Flow Issues & Status](#known-flow-issues--status)
8. [How to Install / Upgrade](#how-to-install--upgrade)

---

## Module Overview

یہ module دو مقاصد کے لیے بنایا گیا ہے:

1. **Custom Invoice Reports:** Accounting اور POS دونوں کے لیے custom PDF invoice جس میں Previous Credit دکھائی جائے۔
2. **Previous Credit Calculation:** ہر customer کے لیے Customer Account (credit) کے ذریعے کتنی رقم ابھی تک ادا نہیں ہوئی — اسے invoice پر display کرنا۔

---

## Module Structure

```
odoo_custom_invoice/
│
├── __manifest__.py              ← Module metadata, dependencies, assets
├── __init__.py                  ← Python imports + post_init_hook
│
├── models/
│   ├── __init__.py              ← Model imports
│   ├── account_move.py          ← ⭐ Previous Credit logic (CORE FILE)
│   ├── invoice_report_settings.py ← Report font/style settings model
│   ├── ir_actions_report.py     ← Report action overrides
│   └── pos_order.py             ← POS order extensions
│
├── views/
│   ├── account_move_views.xml   ← Invoice form view (PDF download button)
│   └── invoice_report_settings_views.xml ← Settings UI (font sizes, bold, etc.)
│
├── report/
│   ├── custom_invoice_reports.xml        ← Report action definitions (3 reports)
│   └── custom_invoice_report_templates.xml ← QWeb PDF templates (1553 lines)
│
├── static/src/
│   ├── js/
│   │   ├── previous credit.js   ← ⭐ POS Previous Credit JS (CORE FILE)
│   │   ├── payment_screen.js    ← Custom Invoice (POS) button handler
│   │   ├── pos_invoice.js       ← Override push_and_invoice_order → custom report
│   │   └── auto_invoice_print.js ← (disabled/commented out)
│   ├── xml/
│   │   └── payment_screen.xml   ← Adds "Custom Invoice (POS)" button to POS UI
│   └── scss/
│       └── report.scss          ← PDF report styling
│
├── security/
│   └── ir.model.access.csv      ← Access rights
│
└── data/
    └── report_data.xml          ← Default report settings data
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        POS FLOW                                      │
│                                                                     │
│  Customer selects items → Payment Screen                            │
│         │                                                           │
│         ▼                                                           │
│  [Customer Account Payment added: e.g. Rs. 500]                     │
│  [Cash Payment added: e.g. Rs. 2000]                                │
│         │                                                           │
│         ▼                                                           │
│  User clicks "VALIDATE" button                                      │
│         │                                                           │
│         ▼                                                           │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │  previous credit.js → validateOrder() override          │        │
│  │                                                         │        │
│  │  Step 1: Reset previous_credit = 0                      │        │
│  │                                                         │        │
│  │  Step 2: RPC call → account.move.pos_get_previous_credit│        │
│  │    args: [partner.id, company_id, order.name]           │        │
│  │    Returns: Sum of CA payments from PREVIOUS orders     │        │
│  │    (e.g., Shop/0017 had CA=700 → returns 700)           │        │
│  │                                                         │        │
│  │  Step 3: Read CURRENT order's CA lines from JS          │        │
│  │    (e.g., current order CA=500)                        │        │
│  │                                                         │        │
│  │  Step 4: Total = 700 + 500 = 1200                       │        │
│  │    order.set_previous_credit(1200)                      │        │
│  │                                                         │        │
│  │  Step 5: super.validateOrder() → saves order to backend │        │
│  └─────────────────────────────────────────────────────────┘        │
│         │                                                           │
│         ▼                                                           │
│  Backend creates pos.order + account.move (invoice)                 │
│         │                                                           │
│         ▼                                                           │
│  pos_invoice.js → push_and_invoice_order()                         │
│    Opens: action_custom_invoice_report_pos (custom PDF)             │
│         │                                                           │
│         ▼                                                           │
│  QWeb Template renders PDF                                          │
│    → calls o.previous_credit (computed field)                       │
│    → account_move.py _compute_previous_credit()                     │
│    → Finds all pos.orders for this customer                         │
│    → Sums ALL CA payments (incl. current order) = 1200             │
│    → Shows Previous Credit: 1200 on PDF ✅                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    ACCOUNTING INVOICE FLOW                           │
│                                                                     │
│  Accounting → Invoices → Open Invoice → Print                       │
│         │                                                           │
│         ▼                                                           │
│  _compute_previous_credit() called                                  │
│    → NOT a POS invoice → use accounting logic                       │
│    → Search other posted invoices with payment_state=not_paid/partial│
│    → Sum their amount_residual                                      │
│    → Show Previous Credit on PDF                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File-by-File Breakdown

---

### 1. `__manifest__.py`
**مقصد:** Module کی configuration

```python
'depends': ['account', 'point_of_sale']

'assets': {
    'point_of_sale.assets': [
        'payment_screen.js',    # Custom Invoice button
        'pos_invoice.js',       # Override invoice printing
        'previous credit.js',   # Previous Credit calculation
        'payment_screen.xml',   # UI button template
    ]
}
```

**Reports registered:**
- `action_custom_invoice_report_accounting` → Accounting invoice
- `action_custom_invoice_report_pos` → POS invoice
- `action_pos_invoice_a5` → A5 format report

---

### 2. `models/account_move.py` ⭐ CORE FILE

**Fields added:**

| Field | Type | Description |
|-------|------|-------------|
| `previous_credit` | `Monetary` (computed) | Customer Account total across all POS orders |
| `previous_credit_invoice_ids` | `Many2many` (computed) | Related invoices (for accounting flow) |

**Methods:**

#### `_is_customer_account_pm(pm)` — Static Helper
```
Payment Method کو identify کرتا ہے:
- name میں 'customer' یا 'account' یا 'credit' ہو
```

#### `_compute_previous_credit()` — PDF Rendering کے لیے
```
POS Invoice:
  → pos.order search by account_move=current invoice
  → ALL pos.orders for this partner (state=paid/done/invoiced)
  → Sum CA payments from all orders
  → previous_credit = total (incl. current order)

Accounting Invoice:
  → Search other invoices for same partner
  → payment_state in [not_paid, partial]
  → previous_credit = sum(amount_residual)
```

#### `pos_get_previous_credit(partner_id, company_id, current_order_ref)` — RPC
```
Called from JS BEFORE order is saved.
Returns: Sum of CA payments from PREVIOUS confirmed orders ONLY.
(Current order excluded — JS adds it separately)

Flow:
  1. Search pos.orders by partner_id, state=paid/done/invoiced
  2. Filter out current_order_ref (by pos_reference or name)
  3. Sum Customer Account payments
  4. Return float total
```

#### `action_download_invoice_pdf()` — PDF Download Button
```
Checks if invoice is from POS or Accounting:
  POS → action_custom_invoice_report_pos
  Accounting → action_custom_invoice_report_accounting
```

---

### 3. `static/src/js/previous credit.js` ⭐ CORE FILE

**Part A: Order Model Extension**

```javascript
models.Order.extend({
    initialize()          → previous_credit = 0 (default)
    set_previous_credit() → update value + trigger UI refresh
    export_for_printing() → include previous_credit in receipt data
    export_as_JSON()      → save to JSON (for backend sync)
    init_from_JSON()      → restore from JSON
})
```

**Part B: PaymentScreen Override**

```javascript
validateOrder(isForceValidate) {
    // Step 1: RPC → previous orders' CA total
    prev_orders_ca = await rpc('account.move', 'pos_get_previous_credit', ...)

    // Step 2: Current order's CA from JS payment lines
    current_order_ca = sum of CA payment lines

    // Step 3: Total
    order.set_previous_credit(prev_orders_ca + current_order_ca)

    // Step 4: Actually validate
    return super.validateOrder(isForceValidate)
}
```

**Helper Function:**
```javascript
isCustomerAccountMethod(pm) {
    // Returns true if:
    // - Not a cash payment (is_cash_count !== true)
    // - AND name contains 'customer' / 'account' / 'credit'
    // - OR has receivable_account_id
}
```

---

### 4. `static/src/js/payment_screen.js`

**مقصد:** "Custom Invoice (POS)" button کو handle کرنا

```javascript
printCustomInvoice() {
    // 1. Check customer selected
    // 2. If order not saved → validate first
    // 3. Call pos.order.action_print_custom_invoice
    // 4. Open PDF in new window
}
```

---

### 5. `static/src/js/pos_invoice.js`

**مقصد:** Default POS invoice کو custom invoice سے replace کرنا

```javascript
push_and_invoice_order(order) {
    // Override: instead of default account_invoices report
    // → open: odoo_custom_invoice.action_custom_invoice_report_pos
}
```

---

### 6. `static/src/xml/payment_screen.xml`

**مقصد:** POS Payment Screen پر "Custom Invoice (POS)" button add کرنا

```xml
<t t-inherit="point_of_sale.PaymentScreen">
    <!-- Add button before Validate -->
    <button class="custom-invoice-pos" t-on-click="printCustomInvoice">
        Custom Invoice (POS)
    </button>
</t>
```

---

### 7. `report/custom_invoice_report_templates.xml`

**3 QWeb Templates:**

| Template ID | Usage |
|-------------|-------|
| `custom_invoice_report_accounting` | Accounting invoices |
| `custom_invoice_report_pos` | POS invoices |
| `pos_invoice_a5` | A5 format |

**Previous Credit display in templates (POS):**
```xml
<!-- Lines 957-969 (POS) and 1444-1458 (Accounting) -->
<t t-if="o.previous_credit and o.previous_credit > 0">
    <tr>
        <td>Previous Credit</td>
        <td><span t-field="o.previous_credit" .../></td>
    </tr>
</t>
```

---

### 8. `views/invoice_report_settings_views.xml`

**مقصد:** Settings UI — font sizes, bold on/off for each field

**Settings جو control ہوتی ہیں:**
- Company name, address font size/bold
- Invoice number, date, due date font size/bold
- Table columns (description, quantity, price, taxes, amount)
- Total, Paid, Previous Credit, Amount Due font size/bold

---

## Previous Credit — Core Logic

### Formula

```
Previous Credit = 
    (Sum of Customer Account payments from ALL previous confirmed POS orders)
  + (Current POS order's Customer Account payment amount)

= All CA payments for this customer across ALL pos.orders
```

### Example

| Order | CA Payment | Cash | Status |
|-------|-----------|------|--------|
| Shop/0017 | 700 | 3000 | Confirmed |
| Shop/0018 | 0 | 1200 | Confirmed |
| Shop/0019 (current) | 500 | 2000 | Being validated |

**Previous Credit for Shop/0019:**
```
Backend RPC returns: 700 (from Shop/0017 only, Shop/0018 has no CA)
JS adds current order: 500
Total Previous Credit: 1200 ✅
```

### Customer Account Payment Identification

```python
# Python (account_move.py)
def _is_customer_account_pm(pm):
    name = pm.name.lower()
    return 'customer' in name or 'account' in name or 'credit' in name
```

```javascript
// JavaScript (previous credit.js)
function isCustomerAccountMethod(pm) {
    const name = (pm.name || '').toLowerCase();
    return !pm.is_cash_count && (
        name.includes('customer') ||
        name.includes('account') ||
        name.includes('credit') ||
        pm.receivable_account_id
    );
}
```

---

## Report System

### 3 Reports Available

| Report | ID | Format | Used For |
|--------|-----|--------|----------|
| Custom Invoice (Accounting) | `action_custom_invoice_report_accounting` | A4 PDF | Regular invoices |
| Custom Invoice (POS) | `action_custom_invoice_report_pos` | A4 PDF | POS orders |
| A5 Report | `action_pos_invoice_a5` | A5 PDF | Compact POS receipt |

### How PDF is Generated

```
1. User clicks Print/Download
2. action_download_invoice_pdf() checks: POS or Accounting invoice?
3. Calls appropriate ir.actions.report
4. QWeb renders template
5. o.previous_credit → _compute_previous_credit() called
6. PDF generated with correct Previous Credit value
```

---

## Known Flow Issues & Status

| Issue | Status | Fix Applied |
|-------|--------|-------------|
| Previous Credit showing 4900 instead of 1200 | ✅ Fixed | Sum CA payments, not amount_residual |
| RPC called after order save (timing) | ✅ Fixed | RPC before super(), JS adds current CA |
| Amount residual summed (all old invoices) | ✅ Fixed | pos.payment records used instead |
| Accounting invoice still uses residual sum | ✅ Correct | Different logic for non-POS (expected) |

---

## How to Install / Upgrade

### Fresh Install
```bash
python odoo-bin -c odoo.conf -i odoo_custom_invoice
```

### After Code Changes (Upgrade)
```bash
python odoo-bin -c odoo.conf -u odoo_custom_invoice --stop-after-init
```
Then restart Odoo server.

### Via Odoo UI
```
Settings → Technical → Modules → Search "Custom Invoice Reports" → Upgrade
```

### After JS Changes
```
1. Upgrade module
2. Clear browser cache: Ctrl + Shift + Delete
3. Reload POS: Close session → Reopen
```

---

## Checklist Before Testing

- [ ] Module upgraded after Python changes
- [ ] Browser cache cleared after JS changes
- [ ] POS Payment Method named: "Customer Account" (contains 'account' in name)
- [ ] Customer selected in POS before payment
- [ ] POS session properly closed for previous orders (state='paid'/'done')
- [ ] Check browser console for `[PreviousCredit]` debug logs

---

*Documentation generated: 2026-02-24 | Module Version: 15.0.1.0.29*
