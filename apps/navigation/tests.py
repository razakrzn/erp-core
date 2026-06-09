from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from api.v1.navigation.views import NavigationSeederAPIView
from apps.navigation.seeders.seed_navigation import run as run_navigation_seed
from apps.navigation.models import Permission

from .models import Feature, Module


class NavigationSeederAPIViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )

        self.feature_b = Feature.objects.create(
            feature_code="feature_b",
            feature_name="Feature B",
            icon="icon-b",
            order=2,
        )
        self.feature_a = Feature.objects.create(
            feature_code="feature_a",
            feature_name="Feature A",
            icon="icon-a",
            order=1,
        )

        Module.objects.create(
            feature=self.feature_a,
            module_code="module_a2",
            module_name="Module A2",
            route="/a/2",
            icon="icon-a2",
            order=2,
        )
        Module.objects.create(
            feature=self.feature_a,
            module_code="module_a1",
            module_name="Module A1",
            route="/a/1",
            icon="icon-a1",
            order=1,
        )

    def test_returns_seed_shaped_navigation_structure(self):
        request = self.factory.get("/api/v1/navigation/seeder/")
        force_authenticate(request, user=self.user)

        response = NavigationSeederAPIView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.data)
        structure = response.data["data"]["erp_structure"]

        self.assertEqual([item["feature_code"] for item in structure], ["feature_a", "feature_b"])
        self.assertEqual(structure[0]["modules"][0]["code"], "module_a1")
        self.assertEqual(structure[0]["modules"][1]["code"], "module_a2")
        self.assertEqual(
            [permission["permission_code"] for permission in structure[0]["modules"][0]["permissions"]],
            [
                "feature_a.module_a1.create",
                "feature_a.module_a1.delete",
                "feature_a.module_a1.edit",
                "feature_a.module_a1.view",
            ],
        )
        self.assertEqual(
            structure[0],
            {
                "feature_code": "feature_a",
                "feature_name": "Feature A",
                "icon": "icon-a",
                "order": 1,
                "modules": [
                    {
                        "code": "module_a1",
                        "name": "Module A1",
                        "route": "/a/1",
                        "icon": "icon-a1",
                        "order": 1,
                        "permissions": [
                            {
                                "id": structure[0]["modules"][0]["permissions"][0]["id"],
                                "module_name": "Module A1",
                                "permission_code": "feature_a.module_a1.create",
                                "permission_name": "Create Module A1",
                            },
                            {
                                "id": structure[0]["modules"][0]["permissions"][1]["id"],
                                "module_name": "Module A1",
                                "permission_code": "feature_a.module_a1.delete",
                                "permission_name": "Delete Module A1",
                            },
                            {
                                "id": structure[0]["modules"][0]["permissions"][2]["id"],
                                "module_name": "Module A1",
                                "permission_code": "feature_a.module_a1.edit",
                                "permission_name": "Edit Module A1",
                            },
                            {
                                "id": structure[0]["modules"][0]["permissions"][3]["id"],
                                "module_name": "Module A1",
                                "permission_code": "feature_a.module_a1.view",
                                "permission_name": "View Module A1",
                            },
                        ],
                    },
                    {
                        "code": "module_a2",
                        "name": "Module A2",
                        "route": "/a/2",
                        "icon": "icon-a2",
                        "order": 2,
                        "permissions": [
                            {
                                "id": structure[0]["modules"][1]["permissions"][0]["id"],
                                "module_name": "Module A2",
                                "permission_code": "feature_a.module_a2.create",
                                "permission_name": "Create Module A2",
                            },
                            {
                                "id": structure[0]["modules"][1]["permissions"][1]["id"],
                                "module_name": "Module A2",
                                "permission_code": "feature_a.module_a2.delete",
                                "permission_name": "Delete Module A2",
                            },
                            {
                                "id": structure[0]["modules"][1]["permissions"][2]["id"],
                                "module_name": "Module A2",
                                "permission_code": "feature_a.module_a2.edit",
                                "permission_name": "Edit Module A2",
                            },
                            {
                                "id": structure[0]["modules"][1]["permissions"][3]["id"],
                                "module_name": "Module A2",
                                "permission_code": "feature_a.module_a2.view",
                                "permission_name": "View Module A2",
                            },
                        ],
                    },
                ],
            },
        )


class NavigationSeederTests(TestCase):
    def test_run_creates_default_permissions_when_not_explicitly_provided(self):
        with patch(
            "apps.navigation.seeders.seed_navigation.ERP_STRUCTURE",
            [
                {
                    "feature_code": "demo",
                    "feature_name": "Demo",
                    "icon": "demo-icon",
                    "order": 1,
                    "modules": [
                        {
                            "code": "alpha",
                            "name": "Alpha",
                            "route": "/demo/alpha",
                            "icon": "alpha-icon",
                            "order": 1,
                        }
                    ],
                }
            ],
        ):
            run_navigation_seed()

        module = Module.objects.get(module_code="alpha")
        permission_codes = list(
            module.permissions.order_by("permission_code").values_list("permission_code", flat=True)
        )

        self.assertEqual(
            permission_codes,
            [
                "demo.alpha.create",
                "demo.alpha.delete",
                "demo.alpha.edit",
                "demo.alpha.view",
            ],
        )

    def test_run_uses_explicit_permissions_when_provided(self):
        with patch(
            "apps.navigation.seeders.seed_navigation.ERP_STRUCTURE",
            [
                {
                    "feature_code": "demo",
                    "feature_name": "Demo",
                    "icon": "demo-icon",
                    "order": 1,
                    "modules": [
                        {
                            "code": "alpha",
                            "name": "Alpha",
                            "route": "/demo/alpha",
                            "icon": "alpha-icon",
                            "order": 1,
                            "permissions": [
                                {
                                    "code": "demo.alpha.read",
                                    "name": "Read Alpha",
                                },
                                {
                                    "code": "demo.alpha.write",
                                    "name": "Write Alpha",
                                },
                            ],
                        }
                    ],
                }
            ],
        ):
            run_navigation_seed()

        module = Module.objects.get(module_code="alpha")
        permission_codes = list(
            module.permissions.order_by("permission_code").values_list("permission_code", flat=True)
        )

        self.assertEqual(permission_codes, ["demo.alpha.read", "demo.alpha.write"])
        self.assertFalse(Permission.objects.filter(permission_code="demo.alpha.create").exists())
