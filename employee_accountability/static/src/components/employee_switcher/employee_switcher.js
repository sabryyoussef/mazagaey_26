/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { _t } from "@web/core/l10n/translation";

/**
 * Employee Switcher Widget
 * 
 * Displays the current active employee in the navbar and allows switching
 * between employees linked to the current user (for shared department logins).
 */
export class EmployeeSwitcher extends Component {
    static template = "employee_accountability.EmployeeSwitcher";
    static components = { Dropdown, DropdownItem };
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.user = useService("user");
        this.dialog = useService("dialog");

        this.state = useState({
            activeEmployee: null,
            availableEmployees: [],
            isLoading: true,
            isSharedUser: false,
            showSwitcher: false,
        });

        onWillStart(async () => {
            await this.loadEmployeeData();
        });
    }

    /**
     * Load current active employee and available employees for this user
     */
    async loadEmployeeData() {
        try {
            this.state.isLoading = true;

            // Get current user's employee context
            const result = await this.orm.call(
                "res.users",
                "get_employee_switcher_data",
                [[this.user.userId]]
            );

            if (result) {
                this.state.activeEmployee = result.active_employee;
                this.state.availableEmployees = result.available_employees || [];
                this.state.isSharedUser = result.is_shared_user || false;
                this.state.showSwitcher = this.state.availableEmployees.length > 1;
            }
        } catch (error) {
            console.error("Failed to load employee data:", error);
            this.notification.add(
                _t("Failed to load employee information"),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Get display name for current employee
     */
    get activeEmployeeName() {
        if (this.state.isLoading) {
            return _t("Loading...");
        }
        if (this.state.activeEmployee) {
            return this.state.activeEmployee.name;
        }
        if (this.state.isSharedUser) {
            return _t("Select Employee");
        }
        return "";
    }

    /**
     * Check if we should show the widget
     */
    get shouldShow() {
        // Show if: loading, shared user, or has multiple employees
        return this.state.isLoading || this.state.isSharedUser || this.state.showSwitcher;
    }

    /**
     * Get CSS class for the widget based on state
     */
    get statusClass() {
        if (!this.state.activeEmployee && this.state.isSharedUser) {
            return "o_employee_switcher_warning";
        }
        return "";
    }

    /**
     * Handle employee selection from dropdown
     */
    async onEmployeeSelect(employeeId) {
        if (this.state.activeEmployee && this.state.activeEmployee.id === employeeId) {
            return; // Already selected
        }

        const employee = this.state.availableEmployees.find(e => e.id === employeeId);
        if (!employee) {
            return;
        }

        // Check if PIN is required
        if (employee.pin_required) {
            await this.openPinDialog(employee);
        } else {
            await this.switchEmployee(employee.id, null);
        }
    }

    /**
     * Open PIN verification dialog
     */
    async openPinDialog(employee) {
        // Open the PIN wizard as an action
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Verify PIN"),
            res_model: "employee.select.wizard",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_employee_id: employee.id,
                default_require_pin: true,
            },
        });

        // Reload after dialog closes
        await this.loadEmployeeData();
    }

    /**
     * Switch to a different employee
     */
    async switchEmployee(employeeId, pin) {
        try {
            const result = await this.orm.call(
                "res.users",
                "set_active_employee",
                [[this.user.userId], employeeId, pin]
            );

            if (result.success) {
                this.notification.add(
                    _t("Switched to %s", result.employee_name),
                    { type: "success" }
                );
                await this.loadEmployeeData();
            } else {
                this.notification.add(
                    result.message || _t("Failed to switch employee"),
                    { type: "warning" }
                );
            }
        } catch (error) {
            console.error("Failed to switch employee:", error);
            this.notification.add(
                _t("Error switching employee"),
                { type: "danger" }
            );
        }
    }

    /**
     * Open full employee selection wizard
     */
    async openSelectWizard() {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Select Employee"),
            res_model: "employee.select.wizard",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_require_pin: true,
            },
        });

        // Reload after dialog closes
        await this.loadEmployeeData();
    }
}

// Register the component in the systray registry
export const employeeSwitcherItem = {
    Component: EmployeeSwitcher,
    isDisplayed: (env) => true, // Always check, component decides visibility
};

registry.category("systray").add("employee_accountability.EmployeeSwitcher", employeeSwitcherItem, { sequence: 1 });
