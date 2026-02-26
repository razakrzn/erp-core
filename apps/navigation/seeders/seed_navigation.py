from apps.navigation.models import Feature, Module

# Permissions (create/view/edit/delete) are created automatically via signal
# when each Module is created; see apps.navigation.services.permission_generator.

ERP_STRUCTURE = [
    {
        "feature_code": "core",
        "feature_name": "Core & Administration",
        "icon": "settings",
        "order": 1,
        "modules": [
            {"code": "user_management", "name": "User Management", "route": "/core/user-management", "icon": "users", "order": 1},
            {"code": "company_profile", "name": "Company Profile", "route": "/core/company-profile", "icon": "building", "order": 2},
            {"code": "branch_mgmt", "name": "Branch/Factory Management", "route": "/core/branch-management", "icon": "map-pin", "order": 3},
            {"code": "audit_logs", "name": "Audit Logs", "route": "/core/audit-logs", "icon": "activity", "order": 4},
            {"code": "backup", "name": "Backup & Restore", "route": "/core/backup", "icon": "database", "order": 5},
            {"code": "system_settings", "name": "System Settings", "route": "/core/system-settings", "icon": "sliders", "order": 6},
        ],
    },
    {
        "feature_code": "sales",
        "feature_name": "Sales & CRM",
        "icon": "trending-up",
        "order": 2,
        "modules": [
            {"code": "leads", "name": "Lead Management", "route": "/sales/leads", "icon": "users", "order": 1},
            {"code": "customers", "name": "Customer Database", "route": "/sales/customers", "icon": "user", "order": 2},
            {"code": "visits", "name": "Visit Management", "route": "/sales/visits", "icon": "calendar", "order": 3},
            {"code": "requirements", "name": "Requirement Gathering", "route": "/sales/requirements", "icon": "file-text", "order": 4},
            {"code": "competitors", "name": "Competitor Tracking", "route": "/sales/competitors", "icon": "target", "order": 5},
            {"code": "feedback", "name": "Customer Feedback", "route": "/sales/feedback", "icon": "message-circle", "order": 6},
        ],
    },
    {
        "feature_code": "project",
        "feature_name": "Project Management",
        "icon": "folder",
        "order": 3,
        "modules": [
            {"code": "projects", "name": "Project Creation", "route": "/project/projects", "icon": "folder", "order": 1},
            {"code": "workflow_stages", "name": "Workflow Stage Management", "route": "/project/workflow-stages", "icon": "git-merge", "order": 2},
            {"code": "tasks", "name": "Task Management", "route": "/project/tasks", "icon": "check-square", "order": 3},
            {"code": "gantt", "name": "Gantt Chart/Timeline", "route": "/project/gantt", "icon": "bar-chart-2", "order": 4},
            {"code": "documents", "name": "Document Management", "route": "/project/documents", "icon": "file", "order": 5},
            {"code": "meetings", "name": "Meeting Minutes", "route": "/project/meetings", "icon": "message-square", "order": 6},
            {"code": "change_orders", "name": "Change Order Management", "route": "/project/change-orders", "icon": "edit", "order": 7},
        ],
    },
    {
        "feature_code": "design",
        "feature_name": "Design & Engineering",
        "icon": "layout",
        "order": 4,
        "modules": [
            {"code": "concept_design", "name": "Concept Design", "route": "/design/concept", "icon": "layout", "order": 1},
            {"code": "cad_integration", "name": "CAD Integration", "route": "/design/cad", "icon": "monitor", "order": 2},
            {"code": "visualization", "name": "2D/3D Visualization", "route": "/design/visualization", "icon": "eye", "order": 3},
            {"code": "bom_generator", "name": "Bill of Materials Generator", "route": "/design/bom", "icon": "package", "order": 4},
            {"code": "technical_drawings", "name": "Technical Drawing Management", "route": "/design/drawings", "icon": "image", "order": 5},
            {"code": "site_measurement", "name": "Site Measurement Tool", "route": "/design/site-measurement", "icon": "ruler", "order": 6},
            {"code": "material_spec", "name": "Material Specification", "route": "/design/material-spec", "icon": "layers", "order": 7},
            {"code": "design_library", "name": "Design Library", "route": "/design/library", "icon": "book", "order": 8},
        ],
    },
    {
        "feature_code": "estimation",
        "feature_name": "Estimation & Quotation",
        "icon": "calculator",
        "order": 5,
        "modules": [
            {"code": "cost_calculator", "name": "Cost Calculator", "route": "/estimation/cost-calculator", "icon": "calculator", "order": 1},
            {"code": "rate_cards", "name": "Rate Card Management", "route": "/estimation/rate-cards", "icon": "credit-card", "order": 2},
            {"code": "bom_costing", "name": "BOM Costing", "route": "/estimation/bom-costing", "icon": "dollar-sign", "order": 3},
            {"code": "labor_estimation", "name": "Labor Estimation", "route": "/estimation/labor-estimation", "icon": "users", "order": 4},
            {"code": "quotations", "name": "Quotation Generator", "route": "/estimation/quotations", "icon": "file-text", "order": 5},
            {"code": "quote_approval", "name": "Quotation Approval Workflow", "route": "/estimation/quote-approval", "icon": "check-circle", "order": 6},
            {"code": "discounts", "name": "Discount Management", "route": "/estimation/discounts", "icon": "percent", "order": 7},
            {"code": "quote_comparison", "name": "Version Comparison", "route": "/estimation/quote-comparison", "icon": "copy", "order": 8},
            {"code": "quote_to_order", "name": "Quote-to-Order Conversion", "route": "/estimation/quote-to-order", "icon": "arrow-right", "order": 9},
        ],
    },
    {
        "feature_code": "procurement",
        "feature_name": "Procurement & Inventory",
        "icon": "shopping-cart",
        "order": 6,
        "modules": [
            {"code": "vendors", "name": "Vendor Management", "route": "/procurement/vendors", "icon": "truck", "order": 1},
            {"code": "purchase_requisitions", "name": "Purchase Requisition", "route": "/procurement/requisitions", "icon": "shopping-cart", "order": 2},
            {"code": "purchase_orders", "name": "Purchase Order Management", "route": "/procurement/purchase-orders", "icon": "file", "order": 3},
            {"code": "goods_receipt", "name": "Goods Receipt Note", "route": "/procurement/goods-receipt", "icon": "download", "order": 4},
            {"code": "inventory_dashboard", "name": "Inventory Dashboard", "route": "/procurement/inventory-dashboard", "icon": "pie-chart", "order": 5},
            {"code": "materials", "name": "Material Master", "route": "/procurement/materials", "icon": "cube", "order": 6},
            {"code": "stock_movements", "name": "Stock Movement", "route": "/procurement/stock-movements", "icon": "move", "order": 7},
            {"code": "low_stock_alerts", "name": "Low Stock Alerts", "route": "/procurement/low-stock", "icon": "alert-circle", "order": 8},
            {"code": "inventory_valuation", "name": "Inventory Valuation", "route": "/procurement/inventory-valuation", "icon": "dollar-sign", "order": 9},
            {"code": "warehouses", "name": "Warehouse Management", "route": "/procurement/warehouses", "icon": "home", "order": 10},
            {"code": "project_allocation", "name": "Project-wise Allocation", "route": "/procurement/project-allocation", "icon": "tag", "order": 11},
        ],
    },
    {
        "feature_code": "production",
        "feature_name": "Production & Manufacturing",
        "icon": "cpu",
        "order": 7,
        "modules": [
            {"code": "production_planning", "name": "Production Planning", "route": "/production/planning", "icon": "calendar", "order": 1},
            {"code": "production_orders", "name": "Production Order (Job Card)", "route": "/production/orders", "icon": "clipboard", "order": 2},
            {"code": "shop_floor", "name": "Shop Floor Control", "route": "/production/shop-floor", "icon": "activity", "order": 3},
            {"code": "bom_explosion", "name": "BOM Explosion", "route": "/production/bom-explosion", "icon": "share-2", "order": 4},
            {"code": "cutting_optimization", "name": "Cutting Optimization", "route": "/production/cutting", "icon": "scissors", "order": 5},
            {"code": "machine_integration", "name": "Machine Integration", "route": "/production/machine-integration", "icon": "cpu", "order": 6},
            {"code": "labor_tracking", "name": "Labor Tracking", "route": "/production/labor-tracking", "icon": "user-check", "order": 7},
            {"code": "wip_tracking", "name": "Work-in-Progress Tracking", "route": "/production/wip", "icon": "loader", "order": 8},
            {"code": "subcontracting", "name": "Subcontracting Management", "route": "/production/subcontracting", "icon": "external-link", "order": 9},
            {"code": "batch_tracking", "name": "Batch Tracking", "route": "/production/batch-tracking", "icon": "hash", "order": 10},
            {"code": "rework", "name": "Rejection & Rework Management", "route": "/production/rework", "icon": "rotate-cw", "order": 11},
        ],
    },
    {
        "feature_code": "quality",
        "feature_name": "Quality Control",
        "icon": "check-circle",
        "order": 8,
        "modules": [
            {"code": "incoming_qc", "name": "Incoming QC", "route": "/quality/incoming", "icon": "download-cloud", "order": 1},
            {"code": "inprocess_qc", "name": "In-process QC", "route": "/quality/inprocess", "icon": "activity", "order": 2},
            {"code": "final_qc", "name": "Final QC", "route": "/quality/final", "icon": "check-circle", "order": 3},
            {"code": "qc_checklists", "name": "QC Checklists", "route": "/quality/checklists", "icon": "list", "order": 4},
            {"code": "ncr", "name": "Non-Conformance Reports", "route": "/quality/ncr", "icon": "alert-triangle", "order": 5},
            {"code": "rework_auth", "name": "Rework Authorization", "route": "/quality/rework-auth", "icon": "edit", "order": 6},
            {"code": "quality_dashboard", "name": "Quality Dashboard", "route": "/quality/dashboard", "icon": "bar-chart", "order": 7},
        ],
    },
    {
        "feature_code": "logistics",
        "feature_name": "Logistics & Installation",
        "icon": "truck",
        "order": 9,
        "modules": [
            {"code": "dispatch_planning", "name": "Dispatch Planning", "route": "/logistics/dispatch-planning", "icon": "truck", "order": 1},
            {"code": "packing", "name": "Packing Management", "route": "/logistics/packing", "icon": "package", "order": 2},
            {"code": "delivery_challan", "name": "Delivery Challan", "route": "/logistics/delivery-challan", "icon": "file", "order": 3},
            {"code": "shipment_tracking", "name": "Shipment Tracking", "route": "/logistics/shipment-tracking", "icon": "map-pin", "order": 4},
            {"code": "installation_schedule", "name": "Installation Scheduling", "route": "/logistics/installation-schedule", "icon": "calendar", "order": 5},
            {"code": "installation_checklist", "name": "Installation Checklist", "route": "/logistics/installation-checklist", "icon": "check-square", "order": 6},
            {"code": "site_inventory", "name": "Site Inventory Management", "route": "/logistics/site-inventory", "icon": "archive", "order": 7},
            {"code": "handover", "name": "Handover Documentation", "route": "/logistics/handover", "icon": "file-plus", "order": 8},
            {"code": "customer_training", "name": "Customer Training", "route": "/logistics/customer-training", "icon": "users", "order": 9},
        ],
    },
    {
        "feature_code": "finance",
        "feature_name": "Finance & Accounting",
        "icon": "dollar-sign",
        "order": 10,
        "modules": [
            {"code": "accounts_receivable", "name": "Accounts Receivable", "route": "/finance/ar", "icon": "dollar-sign", "order": 1},
            {"code": "accounts_payable", "name": "Accounts Payable", "route": "/finance/ap", "icon": "credit-card", "order": 2},
            {"code": "budgeting", "name": "Budgeting", "route": "/finance/budgeting", "icon": "pie-chart", "order": 3},
            {"code": "cost_tracking", "name": "Cost Tracking", "route": "/finance/cost-tracking", "icon": "trending-up", "order": 4},
            {"code": "expenses", "name": "Expense Management", "route": "/finance/expenses", "icon": "file-text", "order": 5},
            {"code": "bank_integration", "name": "Bank Integration", "route": "/finance/bank-integration", "icon": "database", "order": 6},
            {"code": "tax", "name": "Tax Management", "route": "/finance/tax", "icon": "percent", "order": 7},
            {"code": "financial_reports", "name": "Financial Reports", "route": "/finance/reports", "icon": "bar-chart", "order": 8},
            {"code": "payment_collection", "name": "Payment Collection", "route": "/finance/payment-collection", "icon": "wallet", "order": 9},
            {"code": "retention", "name": "Retention Money Tracking", "route": "/finance/retention", "icon": "lock", "order": 10},
        ],
    },
    {
        "feature_code": "hr",
        "feature_name": "HR & Workforce",
        "icon": "users",
        "order": 11,
        "modules": [
            {"code": "employees", "name": "Employee Database", "route": "/hr/employees", "icon": "users", "order": 1},
            {"code": "attendance", "name": "Attendance Tracking", "route": "/hr/attendance", "icon": "clock", "order": 2},
            {"code": "payroll", "name": "Payroll Processing", "route": "/hr/payroll", "icon": "dollar-sign", "order": 3},
            {"code": "skill_matrix", "name": "Skill Matrix", "route": "/hr/skill-matrix", "icon": "grid", "order": 4},
            {"code": "work_allocation", "name": "Work Allocation", "route": "/hr/work-allocation", "icon": "user-check", "order": 5},
            {"code": "timesheets", "name": "Timesheet Management", "route": "/hr/timesheets", "icon": "calendar", "order": 6},
            {"code": "contractors", "name": "Contractor Management", "route": "/hr/contractors", "icon": "user-plus", "order": 7},
            {"code": "performance", "name": "Performance Management", "route": "/hr/performance", "icon": "star", "order": 8},
        ],
    },
    {
        "feature_code": "analytics",
        "feature_name": "Analytics & Reporting",
        "icon": "bar-chart-2",
        "order": 12,
        "modules": [
            {"code": "executive_dashboard", "name": "Executive Dashboard", "route": "/analytics/executive-dashboard", "icon": "monitor", "order": 1},
            {"code": "project_analytics", "name": "Project Analytics", "route": "/analytics/project-analytics", "icon": "folder", "order": 2},
            {"code": "financial_analytics", "name": "Financial Analytics", "route": "/analytics/financial-analytics", "icon": "dollar-sign", "order": 3},
            {"code": "inventory_analytics", "name": "Inventory Analytics", "route": "/analytics/inventory-analytics", "icon": "package", "order": 4},
            {"code": "production_analytics", "name": "Production Analytics", "route": "/analytics/production-analytics", "icon": "activity", "order": 5},
            {"code": "sales_analytics", "name": "Sales Analytics", "route": "/analytics/sales-analytics", "icon": "trending-up", "order": 6},
            {"code": "report_builder", "name": "Custom Report Builder", "route": "/analytics/report-builder", "icon": "file", "order": 7},
            {"code": "variance_analysis", "name": "Variance Analysis", "route": "/analytics/variance-analysis", "icon": "percent", "order": 8},
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