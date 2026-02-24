/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async printCustomInvoice() {
        const order = this.env.pos.get_order();
        if (!order) {
            return;
        }

        // Check if customer is selected
        if (!order.get_client()) {
            this.env.services.notification.add(
                this.env._t('Please select a customer to print invoice'),
                { type: 'warning' }
            );
            return;
        }

        try {
            let orderId = order.id;
            
            // If order is not saved yet, validate it first
            if (!orderId || orderId < 0) {
                // Validate order to create invoice
                await this._validateOrder();
                // Wait for order to be saved
                await new Promise(resolve => setTimeout(resolve, 1000));
                orderId = order.id;
            }
            
            if (orderId && orderId > 0) {
                // Call Python method to print custom invoice
                const action = await this.env.services.orm.call(
                    'pos.order',
                    'action_print_custom_invoice',
                    [[orderId]]
                );
                
                if (action) {
                    // Open report in new window
                    if (action.url) {
                        window.open(action.url, '_blank');
                    } else if (action.type === 'ir.actions.report') {
                        // Generate PDF and open
                        const report = await this.env.services.orm.call(
                            'ir.actions.report',
                            'render_qweb_pdf',
                            [action.id],
                            [action.res_ids]
                        );
                        
                        if (report) {
                            const blob = new Blob([report], { type: 'application/pdf' });
                            const url = URL.createObjectURL(blob);
                            window.open(url, '_blank');
                        }
                    }
                }
            } else {
                this.env.services.notification.add(
                    this.env._t('Please validate the order first to create invoice'),
                    { type: 'warning' }
                );
            }
        } catch (error) {
            console.error('Error printing custom invoice:', error);
            this.env.services.notification.add(
                this.env._t('Error printing invoice: ') + (error.message || error),
                { type: 'danger' }
            );
        }
    },
});

