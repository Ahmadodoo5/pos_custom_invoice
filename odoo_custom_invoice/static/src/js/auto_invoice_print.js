/** @odoo-module **/

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

/**
 * Automatic Invoice Printing for POS Orders (Odoo 15 Compatible)
 * 
 * This patches the Order model to automatically print custom invoices
 * after order validation, but only if:
 * 1. A customer is selected
 * 2. The order is successfully validated and synced to backend
 * 3. An invoice (account.move) was created for the order
 */

patch(Order.prototype, {
    /**
     * Override the export_for_printing method to trigger invoice printing
     * This is called after order validation is complete
     */
    async export_for_printing() {
        const result = await super.export_for_printing(...arguments);
        
        // Check if auto print is enabled in settings
        const company = this.pos?.company;
        const autoPrintEnabled = company?.auto_print_invoice_pos || false;
        
        if (!autoPrintEnabled) {
            // Auto print is disabled, skip
            return result;
        }
        
        // Only attempt automatic invoice printing if:
        // - Auto print is enabled
        // - Order has a customer (required for invoices)
        // - Order has been synced to server (has positive id)
        if (this.get_client() && this.id && this.id > 0) {
            try {
                await this._printCustomInvoiceAuto();
            } catch (error) {
                // Log error but don't block the printing flow
                console.error('Auto invoice print failed:', error);
                // Optionally show notification (non-blocking)
                if (this.env?.services?.notification) {
                    this.env.services.notification.add(
                        this.env._t('Custom invoice could not be printed automatically. Use the Custom Invoice button.'),
                        { type: 'warning' }
                    );
                }
            }
        }
        
        return result;
    },

    /**
     * Print custom invoice automatically after order validation
     */
    async _printCustomInvoiceAuto() {
        const orderId = this.id;
        
        if (!orderId || orderId <= 0) {
            console.log('Order not synced yet, skipping auto invoice print');
            return;
        }

        try {
            // Small delay to ensure backend has finished processing
            await new Promise(resolve => setTimeout(resolve, 500));

            // Check if order has an invoice by reading from backend
            const orderData = await this.env.services.orm.call(
                'pos.order',
                'read',
                [[orderId], ['account_move']],
                { context: this.env.session.user_context }
            );

            if (!orderData || !orderData.length) {
                console.log('Order not found in backend');
                return;
            }

            let moveId = orderData[0].account_move;
            
            // Handle both formats: integer or [id, name]
            if (Array.isArray(moveId)) {
                moveId = moveId[0];
            }

            if (!moveId) {
                console.log('No invoice created for this order, skipping auto print');
                return;
            }

            // Call the Python method to get the report action
            const action = await this.env.services.orm.call(
                'pos.order',
                'action_print_custom_invoice',
                [[orderId]],
                { context: this.env.session.user_context }
            );

            if (action && action.url) {
                // Open invoice in new window/tab
                window.open(action.url, '_blank');
                console.log('Custom invoice printed automatically');
            }
        } catch (error) {
            console.error('Error in auto invoice print:', error);
            throw error;
        }
    },
});
