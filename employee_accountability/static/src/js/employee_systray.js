/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

/**
 * Systray widget showing the current employee name
 * Appears next to the notification icon
 */
export class EmployeeSystray extends Component {
    static template = "employee_accountability.EmployeeSystray";
    static props = {};
    
    setup() {
        this.actionService = useService("action");
        this.state = useState({
            employeeName: null,
            isSharedUser: false,
            loading: true,
        });
        
        onWillStart(async () => {
            await this.loadEmployeeStatus();
        });
    }
    
    async loadEmployeeStatus() {
        try {
            const result = await rpc("/employee_accountability/check_session", {});
            this.state.isSharedUser = result.is_shared_user || false;
            if (result.active_employee) {
                this.state.employeeName = result.active_employee.name;
            } else {
                this.state.employeeName = null;
            }
        } catch (e) {
            // Silently fail
            console.log("Employee systray: failed to load status", e);
            this.state.isSharedUser = false;
        }
        this.state.loading = false;
    }
    
    async onClickSwitch() {
        try {
            const wizardAction = await rpc("/employee_accountability/wizard_action", {});
            this.actionService.doAction(wizardAction);
        } catch (e) {
            console.log("Failed to open wizard", e);
        }
    }
}

// Register in systray category
registry.category("systray").add("employee_accountability.EmployeeSystray", {
    Component: EmployeeSystray,
}, { sequence: 100 });
