from apps.navigation.models import Feature, Module

# Permissions (create/view/edit/delete) are created automatically via signal
# when each Module is created; see apps.navigation.services.permission_generator.

ERP_STRUCTURE = [
    {
        "feature_code": "hrm",
        "feature_name": "HRM",
        "icon": "users",
        "modules": [
            {"code": "employees", "name": "Employees", "route": "/hrm/employees", "icon": "user"},
            {"code": "attendance", "name": "Attendance", "route": "/hrm/attendance", "icon": "clock"},
            {"code": "payroll", "name": "Payroll", "route": "/hrm/payroll", "icon": "wallet"},
            {"code": "leave", "name": "Leave", "route": "/hrm/leave", "icon": "calendar"},
            {"code": "recruitment", "name": "Recruitment", "route": "/hrm/recruitment", "icon": "user-plus"},
        ],
    },
    {
        "feature_code": "finance",
        "feature_name": "Finance",
        "icon": "dollar-sign",
        "modules": [
            {"code": "general_ledger", "name": "General Ledger", "route": "/finance/gl", "icon": "book"},
            {"code": "accounts_payable", "name": "Accounts Payable", "route": "/finance/ap", "icon": "credit-card"},
            {"code": "accounts_receivable", "name": "Accounts Receivable", "route": "/finance/ar", "icon": "receipt"},
            {"code": "expenses", "name": "Expenses", "route": "/finance/expenses", "icon": "file-text"},
        ],
    },
    {
        "feature_code": "crm",
        "feature_name": "CRM",
        "icon": "users",
        "modules": [
            {"code": "leads", "name": "Leads", "route": "/crm/leads", "icon": "target"},
            {"code": "customers", "name": "Customers", "route": "/crm/customers", "icon": "user"},
            {"code": "activities", "name": "Activities", "route": "/crm/activities", "icon": "check-circle"},
        ],
    },
    {
        "feature_code": "sales",
        "feature_name": "Sales",
        "icon": "shopping-cart",
        "modules": [
            {"code": "quotations", "name": "Quotations", "route": "/sales/quotations", "icon": "file"},
            {"code": "sales_orders", "name": "Sales Orders", "route": "/sales/orders", "icon": "shopping-bag"},
            {"code": "invoices", "name": "Invoices", "route": "/sales/invoices", "icon": "file-text"},
        ],
    },
    {
        "feature_code": "procurement",
        "feature_name": "Procurement",
        "icon": "truck",
        "modules": [
            {"code": "vendors", "name": "Vendors", "route": "/procurement/vendors", "icon": "users"},
            {"code": "purchase_requests", "name": "Purchase Requests", "route": "/procurement/requests", "icon": "file-plus"},
            {"code": "purchase_orders", "name": "Purchase Orders", "route": "/procurement/orders", "icon": "shopping-cart"},
        ],
    },
    {
        "feature_code": "inventory",
        "feature_name": "Inventory",
        "icon": "box",
        "modules": [
            {"code": "stock", "name": "Stock", "route": "/inventory/stock", "icon": "archive"},
            {"code": "warehouse", "name": "Warehouse", "route": "/inventory/warehouse", "icon": "home"},
            {"code": "transfers", "name": "Stock Transfers", "route": "/inventory/transfers", "icon": "repeat"},
        ],
    },
    {
        "feature_code": "manufacturing",
        "feature_name": "Manufacturing",
        "icon": "tool",
        "modules": [
            {"code": "bom", "name": "Bill of Materials", "route": "/mrp/bom", "icon": "list"},
            {"code": "work_orders", "name": "Work Orders", "route": "/mrp/work-orders", "icon": "settings"},
            {"code": "production", "name": "Production", "route": "/mrp/production", "icon": "cpu"},
        ],
    },
    {
        "feature_code": "quality",
        "feature_name": "Quality Control",
        "icon": "check-square",
        "modules": [
            {"code": "inspections", "name": "Inspections", "route": "/quality/inspections", "icon": "search"},
            {"code": "defects", "name": "Defects", "route": "/quality/defects", "icon": "alert-triangle"},
        ],
    },
    {
        "feature_code": "assets",
        "feature_name": "Assets",
        "icon": "briefcase",
        "modules": [
            {"code": "asset_list", "name": "Asset List", "route": "/assets/list", "icon": "box"},
            {"code": "maintenance", "name": "Maintenance", "route": "/assets/maintenance", "icon": "tool"},
        ],
    },
    {
        "feature_code": "logistics",
        "feature_name": "Logistics",
        "icon": "truck",
        "modules": [
            {"code": "shipments", "name": "Shipments", "route": "/logistics/shipments", "icon": "send"},
            {"code": "deliveries", "name": "Deliveries", "route": "/logistics/deliveries", "icon": "map"},
        ],
    },
    {
        "feature_code": "reports",
        "feature_name": "Reports",
        "icon": "bar-chart",
        "modules": [
            {"code": "financial_reports", "name": "Financial Reports", "route": "/reports/finance", "icon": "pie-chart"},
            {"code": "hr_reports", "name": "HR Reports", "route": "/reports/hr", "icon": "users"},
            {"code": "sales_reports", "name": "Sales Reports", "route": "/reports/sales", "icon": "trending-up"},
        ],
    },
    {
        "feature_code": "administration",
        "feature_name": "Administration",
        "icon": "shield",
        "modules": [
            {"code": "roles", "name": "Roles", "route": "/admin/roles", "icon": "lock"},
            {"code": "designation", "name": "Designation", "route": "/admin/designation", "icon": "user-tag"},
            {"code": "department", "name": "Department", "route": "/admin/department", "icon": "building"},
        ],
    },
    {
        "feature_code": "superuser",
        "feature_name": "Superuser",
        "icon": "cog",
        "modules": [
            {"code": "features", "name": "Features", "route": "/superuser/features", "icon": "cog"},
            {"code": "modules", "name": "Modules", "route": "/superuser/modules", "icon": "cog"},
            {"code": "permissions", "name": "Permissions", "route": "/superuser/permissions", "icon": "cog"},
            {"code": "companies", "name": "Companies", "route": "/superuser/companies", "icon": "building"},
            {"code": "users", "name": "Users", "route": "/superuser/users", "icon": "user"},
        ],
    },
]


def run():
    for feature_data in ERP_STRUCTURE:

        feature = Feature.objects.create(
            feature_code=feature_data["feature_code"],
            feature_name=feature_data["feature_name"],
            icon=feature_data["icon"]
        )

        for module_data in feature_data["modules"]:

            Module.objects.create(
                module_code=module_data["code"],
                module_name=module_data["name"],
                feature=feature,
                route=module_data["route"],
                icon=module_data["icon"],
            )
            # Default permissions (create/view/edit/delete) are created by
            # post_save signal in apps.navigation.signals.
