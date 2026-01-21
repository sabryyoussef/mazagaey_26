/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

/**
 * Employee Selection Field Widget
 * 
 * A reusable widget for selecting employees with department filtering.
 * Can be used in forms to select responsible/performing employee.
 */
export class EmployeeSelectionField extends Component {
    static template = "employee_accountability.EmployeeSelectionField";
    static props = {
        ...standardFieldProps,
        showDepartmentFilter: { type: Boolean, optional: true },
        filterByCurrentUser: { type: Boolean, optional: true },
        placeholder: { type: String, optional: true },
    };
    static defaultProps = {
        showDepartmentFilter: true,
        filterByCurrentUser: false,
        placeholder: "Select Employee...",
    };

    setup() {
        this.orm = useService("orm");
        this.user = useService("user");

        this.state = useState({
            employees: [],
            departments: [],
            selectedDepartmentId: null,
            searchQuery: "",
            isOpen: false,
            isLoading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.isLoading = true;

            // Build domain for employees
            let domain = [['active', '=', true]];
            
            if (this.props.filterByCurrentUser) {
                domain.push(['user_id', '=', this.user.userId]);
            }

            // Load employees
            const employees = await this.orm.searchRead(
                "hr.employee",
                domain,
                ["id", "name", "job_title", "department_id", "avatar_128", "user_id"],
                { order: "name asc" }
            );
            this.state.employees = employees;

            // Load departments
            const departments = await this.orm.searchRead(
                "hr.department",
                [['active', '=', true]],
                ["id", "name"],
                { order: "name asc" }
            );
            this.state.departments = departments;

        } catch (error) {
            console.error("Failed to load employee data:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    get filteredEmployees() {
        let employees = this.state.employees;

        // Filter by department
        if (this.state.selectedDepartmentId) {
            employees = employees.filter(
                e => e.department_id && e.department_id[0] === this.state.selectedDepartmentId
            );
        }

        // Filter by search query
        if (this.state.searchQuery) {
            const query = this.state.searchQuery.toLowerCase();
            employees = employees.filter(
                e => e.name.toLowerCase().includes(query) ||
                     (e.job_title && e.job_title.toLowerCase().includes(query))
            );
        }

        return employees;
    }

    get selectedEmployee() {
        const value = this.props.record.data[this.props.name];
        if (value) {
            return this.state.employees.find(e => e.id === value[0]) || null;
        }
        return null;
    }

    get displayValue() {
        const employee = this.selectedEmployee;
        if (employee) {
            return employee.name;
        }
        return this.props.placeholder;
    }

    onDepartmentChange(ev) {
        const value = ev.target.value;
        this.state.selectedDepartmentId = value ? parseInt(value) : null;
    }

    onSearchInput(ev) {
        this.state.searchQuery = ev.target.value;
    }

    onToggleDropdown() {
        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen) {
            this.state.searchQuery = "";
        }
    }

    onSelectEmployee(employee) {
        this.props.record.update({ [this.props.name]: [employee.id, employee.name] });
        this.state.isOpen = false;
    }

    onClear() {
        this.props.record.update({ [this.props.name]: false });
        this.state.isOpen = false;
    }
}

// Register the field widget
registry.category("fields").add("employee_selection", {
    component: EmployeeSelectionField,
    supportedTypes: ["many2one"],
    extractProps: ({ attrs }) => ({
        showDepartmentFilter: attrs.options?.show_department_filter !== false,
        filterByCurrentUser: attrs.options?.filter_by_current_user === true,
        placeholder: attrs.placeholder || "Select Employee...",
    }),
});
