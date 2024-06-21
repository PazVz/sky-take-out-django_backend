from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APIClient,
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from .views import (
    ChangeEmployeeStatusView,
    CustomLogoutView,
    EditPasswordView,
    EmployeeView,
    PaginationEmployeeView,
    QueryEmployeeByIDView,
)

# Create your tests here.


class CustomLoginViewTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_login",
            password="testpass123",
            name="test_login",
            phone="12345678901",
            sex="1",
            id_number="123456789012345678",
            status=1,
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
            sex="1",
            id_number="123456789012345678",
            status=1,
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
            sex="1",
            id_number="123456789012345678",
            status=1,
        )

        self.testuser_data = {
            "username": "employee_testuser",
            "password": "testpass123",
            "name": "employee_testuser",
            "phone": "12345678901",
            "sex": "1",
            "idNumber": "123456789012345678",
            "status": 1,
        }
        self.admin_user.is_staff = True
        self.factory = APIRequestFactory()
        self.url = reverse("add_or_edit_employee")
        self.view = EmployeeView.as_view()

    def test_create_employee_with_post_and_edit_it_wiht_put(self):
        # 测试通过 POST 添加用户
        request_post = self.factory.post(
            self.url, data=self.testuser_data, format="json"
        )
        force_authenticate(request_post, user=self.admin_user)
        response_post = self.view(request_post)
        self.assertEqual(response_post.status_code, status.HTTP_200_OK)
        response_post_json = str(response_post.data)
        self.assertIn("employee_testuser", response_post_json)

        # 获取刚刚添加的用户的 ID
        latest_user = get_user_model().objects.latest("id")
        _id = latest_user.id

        # 测试通过 POST 修改用户数据
        edit_testuser_data = dict(self.testuser_data)
        edit_testuser_data["username"] = "employee_testuser(edit)"
        edit_testuser_data["id"] = _id
        request_put = self.factory.put(self.url, data=edit_testuser_data, format="json")
        force_authenticate(request_put, user=self.admin_user)
        response_put = self.view(request_put)
        self.assertEqual(response_put.status_code, status.HTTP_200_OK)
        response_put_json = str(response_put.data)
        self.assertIn("employee_testuser(edit)", response_put_json)


class QueryEmployeeViewTest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_query",
            password="testpass123",
            name="test_query",
            phone="12345678901",
            sex="1",
            id_number="123456789012345678",
            status=1,
        )
        self.factory = APIRequestFactory()
        self.view = QueryEmployeeByIDView.as_view()
        self.url = reverse("query_employee", kwargs={"id": self.user.id})

    def test_query_employee(self):
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = self.view(request, id=self.user.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 1)
        self.assertIn("data", response.data)
        self.assertIn(
            str(self.user.id), str(response.data.get("data", {}).get("id", ""))
        )


class ChangeEmployeeStatusViewTest(APITestCase):

    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(
            username="admin_user",
            password="testpass123",
            name="admin_user",
            phone="12345678901",
            sex="1",
            id_number="123456789012345678",
            status=1,
        )
        self.user_status_1 = get_user_model().objects.create_user(
            username="test_change_status_1",
            password="testpass123",
            name="test_change_status_1",
            phone="12345678901",
            sex="1",
            id_number="123456789012345678",
            status=1,
        )
        self.user_status_0 = get_user_model().objects.create_user(
            username="test_change_status_0",
            password="testpass123",
            name="test_change_status_0",
            phone="12345678901",
            sex="1",
            id_number="123456789012345678",
            status=0,
        )
        self.admin_user.is_staff = True
        self.factory = APIRequestFactory()
        self.view = ChangeEmployeeStatusView.as_view()
        self.url_status_to_0 = reverse("change_employee_status", kwargs={"status": 0})

        self.url_status_to_1 = reverse("change_employee_status", kwargs={"status": 1})

    def test_status_0_to_1(self):
        request = self.factory.post(
            self.url_status_to_1 + f"?id={self.user_status_0.id}"
        )
        force_authenticate(request, self.admin_user)
        response = self.view(request, status=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("code", 0), 1)
        self.assertEqual(
            get_user_model().objects.filter(id=self.user_status_0.id)[0].status, 1
        )

    def test_status_0_to_0(self):
        request = self.factory.post(
            self.url_status_to_0 + f"?id={self.user_status_0.id}"
        )
        force_authenticate(request, self.admin_user)
        response = self.view(request, status=0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("code", 0), 1)
        self.assertEqual(
            get_user_model().objects.filter(id=self.user_status_0.id)[0].status, 0
        )

    def test_status_1_to_0(self):
        request = self.factory.post(
            self.url_status_to_0 + f"?id={self.user_status_1.id}"
        )
        force_authenticate(request, self.admin_user)
        response = self.view(request, status=0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("code", 0), 1)
        self.assertEqual(
            get_user_model().objects.filter(id=self.user_status_1.id)[0].status, 0
        )

    def test_status_1_to_1(self):
        request = self.factory.post(
            self.url_status_to_1 + f"?id={self.user_status_1.id}"
        )
        force_authenticate(request, self.admin_user)
        response = self.view(request, status=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("code", 0), 1)
        self.assertEqual(
            get_user_model().objects.filter(id=self.user_status_1.id)[0].status, 1
        )


class EditPasswordViewTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_edit_password",
            password="testpass123",
            name="test_edit_password",
            phone="12345678901",
            sex="1",
            id_number="123456789012345678",
            status=1,
        )
        self.factory = APIRequestFactory()
        self.view = EditPasswordView.as_view()
        self.url = reverse("edit_password")

    def test_edit_password_success(self):
        data = {
            "empId": self.user.id,
            "oldPassword": "testpass123",
            "newPassword": "newpass123",
        }
        request = self.factory.put(self.url, data, format="json")
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 1)

    def test_edit_password_fail(self):
        data = {
            "empId": self.user.id,
            "oldPassword": "wrongpass",
            "newPassword": "newpass123",
        }
        request = self.factory.put(self.url, data, format="json")
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], 0)


class PaginationEmployeeViewTests(APITestCase):

    def setUp(self):
        model = get_user_model()
        self.admin_user = model.objects.create_user(
            username="admin_user",
            password="testpass123",
            name="admin_user",
            phone="12345678901",
            sex="1",
            id_number="123456789012345678",
            status=1,
        )
        self.admin_user.is_staff = True
        for i in range(40):
            model.objects.create_user(
                username=f"test_Pagination_{i}",
                password="testpass123",
                name=f"test_Pagination_{i}",
                phone="12345678901",
                sex="1",
                id_number="123456789012345678",
                status=1,
            )
        self.factory = APIRequestFactory()
        self.view = PaginationEmployeeView.as_view()
        self.url = reverse("pagination_employee")

    def test_pagination(self):
        request = self.factory.get(self.url + "?page=1&pageSize=10")
        force_authenticate(request, user=self.admin_user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 1)
        self.assertEqual(response.data.get("data", {}).get("total", None), 41)
        self.assertEqual(len(response.data.get("data", {}).get("records", [])), 10)
