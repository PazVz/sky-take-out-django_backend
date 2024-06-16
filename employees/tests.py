from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APIClient,
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from .views import CustomLogoutView, EmployeeView

# Create your tests here.


class CustomLoginViewTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_login",
            password="testpass123",
            name="test_login",
            phone="12345678901",
            sex="F",
            id_number="123456789012345678",
            status="N",
        )
        self.client = APIClient()
        self.url = reverse("employee_login")

    def test_login_success(self):
        data = {
            "username": "test_login",
            "password": "testpass123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 1)
        response_userdata = response.data.get("data", {})
        self.assertEqual(response_userdata.get("name", None), "test_login")
        self.assertEqual(response_userdata.get("username", None), "test_login")
        self.assertIn("token", response_userdata.keys())

    def test_login_fail(self):
        data = {
            "username": "test",
            "password": "wrongpass",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 0)
        self.assertEqual(response.data.get("msg", ""), "Login failed")


class CustomLogoutViewTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_logout",
            password="testpass123",
            name="test_logout",
            phone="12345678901",
            sex="F",
            id_number="123456789012345678",
            status="N",
        )
        self.factory = APIRequestFactory()
        self.view = CustomLogoutView.as_view()
        self.logout_url = reverse("employee_logout")

    def test_logout_auth(self):
        request = self.factory.post(self.logout_url)
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 1)
        self.assertEqual(response.data["msg"], "Successfully Logout")

    def test_logout_unauth(self):
        request = self.factory.post(self.logout_url)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmployeeViewTests(APITestCase):

    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(
            username="admin_user",
            password="testpass123",
            name="admin_user",
            phone="12345678901",
            sex="F",
            id_number="123456789012345678",
            status="N",
        )

        self.testuser_data = {
            "username": "employee_testuser",
            "password": "testpass123",
            "name": "employee_testuser",
            "phone": "12345678901",
            "sex": "F",
            "idNumber": "123456789012345678",
            "status": "N",
        }
        self.admin_user.is_staff = True
        self.factory = APIRequestFactory()
        self.url = reverse("add_or_edit_employee")
        self.view = EmployeeView.as_view()

    def test_create_employee_with_put_and_edit_it_wiht_post(self):
        # 测试通过 PUT 添加用户
        request_put = self.factory.put(self.url, data=self.testuser_data, format="json")
        force_authenticate(request_put, user=self.admin_user)
        response_put = self.view(request_put)
        self.assertEqual(response_put.status_code, status.HTTP_200_OK)
        response_put_json = str(response_put.data)
        self.assertIn("employee_testuser", response_put_json)

        # 获取刚刚添加的用户的 ID
        latest_user = get_user_model().objects.latest("id")
        _id = latest_user.id

        # 测试通过 POST 修改用户数据
        edit_testuser_data = dict(self.testuser_data)
        edit_testuser_data["username"] = "employee_testuser(edit)"
        edit_testuser_data["id"] = _id
        request_post = self.factory.post(self.url, data=edit_testuser_data, format="json")
        force_authenticate(request_post, user=self.admin_user)
        response_post = self.view(request_post)
        self.assertEqual(response_post.status_code, status.HTTP_200_OK)
        response_post_json = str(response_post.data)
        self.assertIn("employee_testuser(edit)", response_post_json)