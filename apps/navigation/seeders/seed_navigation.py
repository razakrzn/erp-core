from apps.navigation.models import Feature, Module

# Permissions (create/view/edit/delete) are created automatically via signal
# when each Module is created; see apps.navigation.services.permission_generator.

ERP_STRUCTURE = [
    {
        "feature_code": "sales",
        "feature_name": "Sales & CRM",
        "icon": "trending-up",
        "order": 1,
        "modules": [
            {"code": "leads", "name": "Lead Management", "route": "/sales/leads", "icon": "users", "order": 1},
            {"code": "customers", "name": "Customer Database", "route": "/sales/customers", "icon": "user", "order": 2},
            {"code": "enquiry", "name": "Enquiry", "route": "/sales/enquiry", "icon": "user", "order": 3},
        ],
    },
    {
        "feature_code": "estimation",
        "feature_name": "Assessment",
        "icon": "clipboard-text",
        "order": 2,
        "modules": [
            {"code": "boq", "name": "BOQ", "route": "/estimation/boq/", "icon": "list", "order": 1},
            {"code": "quotations", "name": "Quotations", "route": "/estimation/quotations", "icon": "file-pencil", "order": 2},
            {"code": "quatation_template", "name": "Templates Items", "route": "/estimation/template/", "icon": "template", "order": 3},
            {"code": "quote_to_order", "name": "Quote-to-Order Conversion", "route": "/estimation/quote-to-order", "icon": "arrow-right", "order": 4},
        ],
    },
    {
        "feature_code": "project",
        "feature_name": "Projects",
        "icon": "folder",
        "order": 3,
        "modules": [
            {"code": "all_projects", "name": "All Projects", "route": "/project/project-creation/", "icon": "folder", "order": 1},
            {"code": "project_overview", "name": "Project Overview", "route": "/project/project-overview", "icon": "chart-bar", "order": 2},
            {"code": "tasks", "name": "Task Management", "route": "/project/tasks", "icon": "check-square", "order": 3},
            {"code": "gantt", "name": "Gantt Chart/Timeline", "route": "/project/gantt", "icon": "bar-chart-2", "order": 4},
            {"code": "documents", "name": "Document Management", "route": "/project/documents", "icon": "file", "order": 5},
            {"code": "rework_auth", "name": "Rework Authorization", "route": "/project/rework-auth", "icon": "edit", "order": 6},
        ],
    },
    {
        "feature_code": "design",
        "feature_name": "Engineering",
        "icon": "layout",
        "order": 4,
        "modules": [
            {"code": "site_measurement", "name": "Site Measurement Tool", "route": "/design/site-measurement", "icon": "ruler", "order": 1},
            {"code": "material_spec", "name": "Material Specification", "route": "/design/material-spec", "icon": "layers", "order": 2},
        ],
    },
    {
        "feature_code": "procurement",
        "feature_name": "Inventory",
        "icon": "shopping-cart",
        "order": 5,
        "modules": [
            {"code": "vendors", "name": "Vendor Management", "route": "/procurement/vendors", "icon": "truck", "order": 1},
            {"code": "purchase_requisitions", "name": "Purchase Requisition", "route": "/procurement/requisitions", "icon": "shopping-cart", "order": 2},
            {"code": "purchase_orders", "name": "Purchase Order Management", "route": "/procurement/purchase-orders", "icon": "file", "order": 3},
            {"code": "goods_receipt", "name": "Goods Receipt Note", "route": "/procurement/goods-receipt", "icon": "download", "order": 4},
            {"code": "inventory_dashboard", "name": "Inventory Dashboard", "route": "/procurement/inventory-dashboard", "icon": "pie-chart", "order": 5},
            {"code": "material_settings", "name": "Material Settings", "route": "/inventory/material-settings/", "icon": "settings-2", "order": 6},
            {"code": "materials", "name": "Material Master", "route": "/procurement/materials", "icon": "cube", "order": 7},
            {"code": "stock_movements", "name": "Stock Movement", "route": "/procurement/stock-movements", "icon": "move", "order": 8},
            {"code": "inventory_checklist", "name": "Checklist Inventory", "route": "/inventory/inventory-checklist/", "icon": "list-check", "order": 9},
            {"code": "low_stock_alerts", "name": "Low Stock Alerts", "route": "/procurement/low-stock", "icon": "alert-circle", "order": 10},
            {"code": "inventory_valuation", "name": "Inventory Valuation", "route": "/procurement/inventory-valuation", "icon": "dollar-sign", "order": 11},
            {"code": "warehouses", "name": "Warehouse Management", "route": "/procurement/warehouses", "icon": "home", "order": 12},
            {"code": "project_allocation", "name": "Project-wise Allocation", "route": "/procurement/project-allocation", "icon": "tag", "order": 13},
        ],
    },
    {
        "feature_code": "production",
        "feature_name": "Production",
        "icon": "cpu",
        "order": 6,
        "modules": [
            {"code": "cutting_optimization", "name": "Cutting Optimization", "route": "/production/cutting", "icon": "scissors", "order": 1},
            {"code": "production_orders", "name": "Production Order (Job Card)", "route": "/production/orders", "icon": "clipboard", "order": 2},
            {"code": "work_stages", "name": "Work Stages", "route": "/production/work-stages", "icon": "activity", "order": 3},
            {"code": "labor_tracking", "name": "Labor Tracking", "route": "/production/labor-tracking", "icon": "user-check", "order": 4},
            {"code": "production_task", "name": "Tasks", "route": "/production/tasks", "icon": "check-square", "order": 5},
            {"code": "production_checklist", "name": "Checklist Production", "route": "/production/checklist/", "icon": "list-check", "order": 6},
            {"code": "rework", "name": "Rejection & Rework Management", "route": "/production/rework", "icon": "rotate-cw", "order": 7},
        ],
    },
    {
        "feature_code": "quality",
        "feature_name": "Quality Control",
        "icon": "list-check",
        "order": 7,
        "modules": [
            {"code": "quality_dashboard", "name": "Quality Dashboard", "route": "/quality/dashboard", "icon": "bar-chart", "order": 1},
            {"code": "final_qc", "name": "Check QC", "route": "/quality/final", "icon": "zoom-check", "order": 2},
            {"code": "ncr", "name": "Non-Conformance Reports", "route": "/quality/ncr", "icon": "alert-triangle", "order": 3},
            {"code": "qc_checklists", "name": "QC Checklists", "route": "/quality/checklists", "icon": "list", "order": 4},
        ],
    },
    {
        "feature_code": "logistics",
        "feature_name": "Logistics",
        "icon": "truck",
        "order": 8,
        "modules": [
            {"code": "packing", "name": "Packing Management", "route": "/logistics/packing", "icon": "package", "order": 1},
            {"code": "dispatch_planning", "name": "Dispatch Planning", "route": "/logistics/dispatch-planning", "icon": "truck", "order": 2},
            {"code": "delivery_challan", "name": "Delivery Challan", "route": "/logistics/delivery-challan", "icon": "file", "order": 3},
            {"code": "shipment_tracking", "name": "Shipment Tracking", "route": "/logistics/shipment-tracking", "icon": "map-pin", "order": 4},
        ],
    },
    {
        "feature_code": "installation",
        "feature_name": "Installation",
        "icon": "arrow-down-to-arc",
        "order": 9,
        "modules": [
            {"code": "installation_schedule", "name": "Installation Scheduling", "route": "/installation/installation-schedule", "icon": "calendar", "order": 1},
            {"code": "intsallation-labor-tracking", "name": "Labor Tracking", "route": "/installation/intsallation-labor-tracking/", "icon": "user-check", "order": 2},
            {"code": "site_inventory", "name": "Site Inventory Management", "route": "/installation/site-inventory", "icon": "archive", "order": 3},
            {"code": "installation_checklist", "name": "Installation Checklist", "route": "/installation/installation-checklist", "icon": "check-square", "order": 4},
            {"code": "installation_task", "name": "Tasks", "route": "/installation/tasks/", "icon": "check-square", "order": 5},
            {"code": "installation_rework", "name": "Rework Installation", "route": "/installation/rework/", "icon": "rotate-cw", "order": 6},
            {"code": "handover", "name": "Handover Documentation", "route": "/installation/handover", "icon": "file-plus", "order": 7},
        ],
    },
    {
        "feature_code": "hr",
        "feature_name": "HRM",
        "icon": "users",
        "order": 10,
        "modules": [
            {"code": "roles", "name": "Roles", "route": "/hr/roles/", "icon": "circles", "order": 1},
            {"code": "department", "name": "Department", "route": "/hrm/department/", "icon": "window", "order": 2},
            {"code": "designation", "name": "Designation", "route": "/hr/designation/", "icon": "buildings", "order": 3},
            {"code": "employees", "name": "Employee Database", "route": "/hr/employees", "icon": "users", "order": 4},
            {"code": "attendance", "name": "Attendance Tracking", "route": "/hr/attendance", "icon": "clock", "order": 5},
            {"code": "payroll", "name": "Payroll Processing", "route": "/hr/payroll", "icon": "dollar-sign", "order": 6},
            {"code": "performance", "name": "Performance Management", "route": "/hr/performance", "icon": "star", "order": 7},
        ],
    },
    {
        "feature_code": "vehicle-management",
        "feature_name": "Vehicles",
        "icon": "truck",
        "order": 11,
        "modules": [
            {"code": "vehicle_database", "name": "Vehicle Database", "route": "/vehicle/vehicle-database/", "icon": "car-garage", "order": 1},
            {"code": "trip_log", "name": "Trip Log", "route": "/vehicle/trip-log/", "icon": "arrows-up-down", "order": 2},
            {"code": "vehicle_mainatanance", "name": "Vehicle Maintenance", "route": "/vehicle/vehicle-maintanance/", "icon": "settings-cog", "order": 3},
            {"code": "schedule&alerts", "name": "Schedule & Alerts", "route": "/vehicle/schedule&alerts/", "icon": "calendar-pause", "order": 4},
        ],
    },
    {
        "feature_code": "analytics",
        "feature_name": "Analytics",
        "icon": "bar-chart-2",
        "order": 12,
        "modules": [
            {"code": "executive_dashboard", "name": "Executive Dashboard", "route": "/analytics/executive-dashboard", "icon": "monitor", "order": 1},
            {"code": "project_analytics", "name": "Project Analytics", "route": "/analytics/project-analytics", "icon": "folder", "order": 2},
            {"code": "financial_analytics", "name": "Financial Analytics", "route": "/analytics/financial-analytics", "icon": "dollar-sign", "order": 3},
            {"code": "inventory_analytics", "name": "Inventory Analytics", "route": "/analytics/inventory-analytics", "icon": "package", "order": 4},
            {"code": "sales_analytics", "name": "Sales Analytics", "route": "/analytics/sales-analytics", "icon": "trending-up", "order": 5},
        ],
    },
    {
        "feature_code": "core",
        "feature_name": "Core & Administration",
        "icon": "settings",
        "order": 13,
        "modules": [
            {"code": "user_management", "name": "User Management", "route": "/core/user-management", "icon": "users", "order": 1},
            {"code": "company_profile", "name": "Company Profile", "route": "/core/company-profile", "icon": "building", "order": 2},
            {"code": "branch_mgmt", "name": "Branch/Factory Management", "route": "/core/branch-management", "icon": "map-pin", "order": 3},
            {"code": "audit_logs", "name": "Audit Logs", "route": "/core/audit-logs", "icon": "activity", "order": 4},
            {"code": "backup", "name": "Backup & Restore", "route": "/core/backup", "icon": "database", "order": 5},
            {"code": "system_settings", "name": "System Settings", "route": "/core/system-settings", "icon": "sliders", "order": 6},
            {"code": "features", "name": "Features", "route": "/core/features", "icon": "building", "order": 7},
            {"code": "modules", "name": "Modules", "route": "/core/modules", "icon": "sliders", "order": 8},
        ],
    },
]



def run():
    for feature_data in ERP_STRUCTURE:
        feature, created = Feature.objects.get_or_create(
            feature_code=feature_data["feature_code"],
            defaults={
                "feature_name": feature_data["feature_name"],
                "icon": feature_data["icon"],
                "order": feature_data["order"],
            }
        )
        if not created:
            # Update existing feature if needed
            feature.feature_name = feature_data["feature_name"]
            feature.icon = feature_data["icon"]
            feature.order = feature_data["order"]
            feature.save()

        for module_data in feature_data["modules"]:
            Module.objects.get_or_create(
                module_code=module_data["code"],
                defaults={
                    "module_name": module_data["name"],
                    "feature": feature,
                    "route": module_data["route"],
                    "icon": module_data["icon"],
                    "order": module_data["order"],
                }
            )
            # Default permissions (create/view/edit/delete) are created by
            # post_save signal in apps.navigation.signals.
