from django.views.generic import TemplateView


class APILandingView(TemplateView):
    template_name = "api/v1/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "api_name": "ERP Core API",
                "api_version": "v1",
                "endpoint_groups": [
                    {
                        "path": "/api/v1/auth/",
                        "methods": ["POST"],
                        "description": "JWT login and token refresh flows for authenticated clients.",
                    },
                    {
                        "path": "/api/v1/users/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "User account records, profile data, and tenant-aware access.",
                    },
                    {
                        "path": "/api/v1/companies/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "Company master data, branding, registration, and contact details.",
                    },
                    {
                        "path": "/api/v1/navigation/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "Modules, features, permissions, and sidebar composition.",
                    },
                    {
                        "path": "/api/v1/inventory/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "Products, vendors, purchase requisitions, and purchase orders.",
                    },
                    {
                        "path": "/api/v1/crm/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "Customers, enquiries, quote lifecycle signals, and sales context.",
                    },
                    {
                        "path": "/api/v1/hrm/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "Employee, department, attendance, payroll, and leave resources.",
                    },
                    {
                        "path": "/api/v1/assessment/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "BOQs, templates, quotes, terms, finishes, and quote items.",
                    },
                    {
                        "path": "/api/v1/production/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "Manufacturing jobs, cutting plans, and optimization workflows.",
                    },
                    {
                        "path": "/api/v1/settings/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "Shared configuration endpoints such as terms and conditions.",
                    },
                    {
                        "path": "/api/v1/access-control/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "API access rules and policy evaluation utilities.",
                    },
                    {
                        "path": "/api/v1/roles/",
                        "methods": ["GET", "POST", "PUT", "DELETE"],
                        "description": "RBAC roles, permissions, user role assignment, and hierarchy.",
                    },
                ],
                "quick_links": [
                    {"label": "Swagger", "href": "/api/docs/"},
                    {"label": "Redoc", "href": "/api/redoc/"},
                    {"label": "Admin", "href": "/admin/"},
                    {"label": "Schema", "href": "/api/schema/"},
                ],
            }
        )
        context["total_endpoint_groups"] = len(context["endpoint_groups"])
        return context
