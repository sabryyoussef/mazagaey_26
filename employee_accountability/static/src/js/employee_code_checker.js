/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

/**
 * Employee Code Checker Service
 * Checks if the current user needs to enter an employee code after login.
 * DISABLED: Auto-popup removed. Use systray badge instead.
 */
export const employeeCodeCheckerService = {
    dependencies: ["action", "notification"],
    
    start(env, { action, notification }) {
        // Service is registered but does nothing automatically
        // User can click the systray badge to identify themselves
        return {};
    },
};

registry.category("services").add("employee_code_checker", employeeCodeCheckerService);
