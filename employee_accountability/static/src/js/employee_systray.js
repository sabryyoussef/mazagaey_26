/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";

export class EmployeeSystray extends Component {
    static template = "employee_accountability.EmployeeSystray";
    static props = {};

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            currentEmployee: null,
            currentCode: null,
            loading: false,
        });
        onMounted(() => {
            // Delay loading to ensure services are ready
            setTimeout(() => {
                this.loadCurrentEmployee();
            }, 100);
        });
    }

    async loadCurrentEmployee() {
        try {
            // Check if user service is available
            if (!user || !user.userId) {
                return;
            }
            
            this.state.loading = true;
            const session = await this.orm.searchRead(
                "employee.session.context",
                [["user_id", "=", user.userId], ["state", "=", "active"]],
                ["employee_id", "employee_code"],
                { limit: 1 }
            );

            if (session && session.length > 0) {
                const employeeData = session[0].employee_id;
                this.state.currentEmployee = Array.isArray(employeeData) ? employeeData[1] : employeeData;
                this.state.currentCode = session[0].employee_code;
            } else {
                this.state.currentEmployee = null;
                this.state.currentCode = null;
            }
        } catch (error) {
            // Silently fail - component will just show "No Code"
            this.state.currentEmployee = null;
            this.state.currentCode = null;
        } finally {
            this.state.loading = false;
        }
    }

    async openEmployeeCodeWizard() {
        try {
            await this.action.doAction({
                name: "Employee Code Authentication",
                res_model: "employee.code.wizard",
                views: [[false, "form"]],
                target: "new",
                type: "ir.actions.act_window",
            });
            // Reload after wizard closes
            await this.loadCurrentEmployee();
        } catch (error) {
            console.error("Error opening employee code wizard:", error);
        }
    }
}

export const employeeSystrayItem = {
    Component: EmployeeSystray,
};

registry.category("systray").add("employee_accountability.employee_systray", employeeSystrayItem, { sequence: 100 });
