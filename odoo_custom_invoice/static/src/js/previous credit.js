odoo.define('odoo_custom_invoice.pos_previous_credit', function (require) {
    'use strict';

    const models = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');

    // ─────────────────────────────────────────────────────────────
    // Helper: check if a payment method is "Customer Account"
    // ─────────────────────────────────────────────────────────────
    function isCustomerAccountMethod(pm) {
        if (!pm) return false;
        const name = (pm.name || '').toLowerCase();
        const isCash = pm.is_cash_count === true;
        // Must NOT be cash AND name must contain customer/account/credit
        return !isCash && (
            name.includes('customer') ||
            name.includes('account') ||
            name.includes('credit') ||
            pm.receivable_account_id  // linked to customer receivable
        );
    }

    // ─────────────────────────────────────────────────────────────
    // 1) Extend Order model to store previous_credit
    // ─────────────────────────────────────────────────────────────
    const _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function () {
            _super_Order.initialize.apply(this, arguments);
            this.previous_credit = this.previous_credit || 0;
        },

        set_previous_credit: function (val) {
            this.previous_credit = Number(val) || 0;
            this.trigger('change', this);
        },

        export_for_printing: function () {
            const receipt = _super_Order.export_for_printing.apply(this, arguments);
            receipt.previous_credit = Number(this.previous_credit) || 0;
            return receipt;
        },

        export_as_JSON: function () {
            const json = _super_Order.export_as_JSON.apply(this, arguments);
            json.previous_credit = Number(this.previous_credit) || 0;
            return json;
        },

        init_from_JSON: function (json) {
            _super_Order.init_from_JSON.apply(this, arguments);
            this.previous_credit = Number(json.previous_credit) || 0;
        },
    });

    // ─────────────────────────────────────────────────────────────
    // 2) Override validateOrder in PaymentScreen
    //
    // FORMULA:
    //   Previous Credit = (all previous confirmed orders' CA payments)
    //                   + (current order's CA payment lines)
    //
    // Example - test1:
    //   Shop/0017: CA=700  → already confirmed → from backend RPC
    //   Shop/0019: CA=500  → current order     → from JS payment lines
    //   Total Previous Credit = 700 + 500 = 1200 ✓
    // ─────────────────────────────────────────────────────────────
    const PreviousCreditPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async validateOrder(isForceValidate) {
                const order = this.currentOrder;
                const partner = order.get_client();

                // Reset
                order.set_previous_credit(0);

                if (partner) {
                    const company_id = this.env.pos.company && this.env.pos.company.id;
                    const order_ref = order.name;

                    try {
                        // ── Step 1: Get previous CONFIRMED orders' Customer Account total ──
                        // Backend excludes current order (not yet saved)
                        const prev_orders_ca = await this.rpc({
                            model: 'account.move',
                            method: 'pos_get_previous_credit',
                            args: [partner.id, company_id, order_ref],
                        });

                        // ── Step 2: Get CURRENT order's Customer Account payment amount ──
                        const paymentLines = order.get_paymentlines();
                        let current_order_ca = 0;
                        for (const line of paymentLines) {
                            if (isCustomerAccountMethod(line.payment_method)) {
                                current_order_ca += line.get_amount();
                            }
                        }

                        // ── Step 3: Total = previous + current ──
                        const total_previous_credit = (Number(prev_orders_ca) || 0) + current_order_ca;
                        order.set_previous_credit(total_previous_credit);

                        console.log('[PreviousCredit] prev_orders_ca:', prev_orders_ca,
                            '| current_order_ca:', current_order_ca,
                            '| total:', total_previous_credit);

                    } catch (e) {
                        console.error('[PreviousCredit] Error:', e);
                        order.set_previous_credit(0);
                    }
                }

                return super.validateOrder(isForceValidate);
            }
        };

    Registries.Component.extend(PaymentScreen, PreviousCreditPaymentScreen);
});
