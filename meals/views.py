import logging

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from file_upload.models import UploadedImage
from utils import from_image_url_to_image_relative_path, get_custom_pagination

from .models import Category, Dish, DishFlavor
from .serializers import CategorySerializer, DishSerializer

logger = logging.getLogger(__name__)


class CategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        _id = request.data.get("id", None)
        name = request.data.get("name", None)
        sort = request.data.get("sort", None)
        _type = request.data.get("type", None)

        if name is None or sort is None or _type is None:
            return Response(
                {"code": 0, "msg": "Please fill all the fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if _id and Category.objects.filter(id=_id).exists():
            return Response(
                {"code": 0, "msg": "Category id already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if _id:
                created_category = Category.objects.create(
                    id=_id,
                    name=name,
                    sort=sort,
                    type=_type,
                    create_user=request.user,
                    update_user=request.user,
                )
            else:
                created_category = Category.objects.create(
                    name=name,
                    sort=sort,
                    type=_type,
                    create_user=request.user,
                    update_user=request.user,
                )
        except Exception as e:
            return Response(
                {"code": 0, "msg": f"Failed to create category: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            data = CategorySerializer(created_category).data
            return Response(
                {
                    "code": 1,
                    "data": data,
                    "msg": "Category created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

    def put(self, request, *args, **kwargs):
        _id = request.data.get("id", None)
        name = request.data.get("name", None)
        sort = request.data.get("sort", None)
        _type = request.data.get("type", None)

        if _id is None or name is None or sort is None:
            return Response(
                {"code": 0, "msg": "Please fill all the fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query_category = Category.objects.filter(id=_id)

        if not query_category.exists():
            return Response(
                {"code": 0, "msg": "Category id does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category = query_category[0]
            category.name = name
            category.sort = sort
            category.type = _type if _type is not None else category.type
            category.update_user = request.user
            category.save()

        except Exception as e:
            return Response(
                {"code": 0, "msg": f"Failed to update category: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            data = CategorySerializer(category).data
            return Response(
                {
                    "code": 1,
                    "data": data,
                    "msg": "Category updated successfully",
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        _id = request.query_params.get("id", None)

        if not _id:
            return Response(
                {"code": 0, "msg": "Please provide the id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = Category.objects.get(id=_id)
        if not category.exists():
            return Response(
                {"code": 0, "msg": "Category id does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category.delete()
        except Exception as e:
            return Response(
                {"code": 0, "msg": f"Failed to delete category: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {
                    "code": 1,
                    "msg": "Category deleted successfully",
                },
                status=status.HTTP_200_OK,
            )


class QueryCategoryByTypeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        _type = request.query_params.get("type", None)

        if _type:
            categorys = Category.objects.filter(type=_type)
        else:
            categorys = Category.objects.all()

        return Response(
            {
                "code": 1,
                "data": CategorySerializer(categorys, many=True).data,
                "msg": "Get category data successfully.",
            },
        )


class ChangeCategoryStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        category_id = request.GET.get("id", None)
        category_status = self.kwargs.get("status", -1)

        if not category_id:
            return Response(
                {"code": 0, "msg": "Missing category id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if category_status not in (0, 1):
            return Response(
                {"code": 0, "msg": "Status code is NOT correct."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query_category = Category.objects.filter(id=category_id)

        if not query_category.exists():
            return Response(
                {"code": 0, "msg": "Category do Not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = query_category[0]
        msg = ""
        match (category.status, category_status):
            case (0, 0):
                msg = f"Category (id = {category_id}) was already BANNED."
            case (1, 1):
                msg = f"Category (id = {category_id}) was already ACTIVATED."
            case (0, 1):
                msg = f"Category (id = {category_id}) was was ACTIVATED."
            case (1, 0):
                msg = f"Category (id = {category_id}) was was LOCKED."

        category.status = category_status
        category.update_user = request.user
        category.save()

        return Response(
            {"code": 1, "data": CategorySerializer(category).data, "msg": msg},
            status=status.HTTP_200_OK,
        )


class PaginationCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        name = request.query_params.get("name", None)
        page_size = request.query_params.get("pageSize", None)
        _type = request.query_params.get("type", None)

        if not page_size:
            return Response(
                {"code": 0, "data": {}, "msg": "Please fill all the fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        paginator = get_custom_pagination(page_size)
        queryset = Category.objects.all()
        if name:
            queryset = queryset.filter(name__contains=name)
        if _type:
            queryset = queryset.filter(type=_type)

        result_page = paginator.paginate_queryset(queryset, request)
        return Response(
            {
                "code": 1,
                "msg": "Successfully fetched category",
                "data": {
                    "total": queryset.count(),
                    "records": CategorySerializer(result_page, many=True).data,
                },
            }
        )


class DishView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        category_id = request.data.get("categoryId", None)
        description = request.data.get("description", "")
        flavors = request.data.get("flavors", [])
        _id = request.data.get("id", None)
        image_url = request.data.get("image", None)
        name = request.data.get("name", None)
        price = request.data.get("price", None)
        _status = request.data.get("status", None)

        if not all([category_id, name, price, image_url]):
            return Response(
                {
                    "code": 0,
                    "msg": "Please fill all the required fields: categoryId, name, price, image",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        category = Category.objects.filter(id=category_id).first()
        if not category:
            return Response(
                {"code": 0, "msg": "Category does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if _id and Dish.objects.filter(id=_id).exists():
            return Response(
                {"code": 0, "msg": "Dish id already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if flavors and not all(
            [flavor.get("name") and flavor.get("value") for flavor in flavors]
        ):
            return Response(
                {
                    "code": 0,
                    "msg": "Please fill all the required fields for flavors: name, value",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_obj = UploadedImage.objects.filter(
            file=from_image_url_to_image_relative_path(image_url)
        ).first()
        if not image_obj:
            return Response(
                {"code": 0, "msg": "Image does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if _id:
                created_dish = Dish.objects.create(
                    id=_id,
                    category_id=category,
                    description=description,
                    image=image_obj,
                    name=name,
                    price=price,
                    create_user=request.user,
                    update_user=request.user,
                )
            else:
                created_dish = Dish.objects.create(
                    category_id=category,
                    description=description,
                    image=image_obj,
                    name=name,
                    price=price,
                    create_user=request.user,
                    update_user=request.user,
                )
            if _status:
                created_dish.status = _status
                created_dish.save()
            for flavor in flavors:
                DishFlavor.objects.create(
                    dish_id=created_dish,
                    name=flavor["name"],
                    value=flavor["value"],
                )
        except Exception as e:
            return Response(
                {"code": 0, "msg": f"Failed to create dish: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {
                    "code": 1,
                    "msg": "Dish created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

    def put(self, request, *args, **kwargs):
        category_id = request.data.get("categoryId", None)
        description = request.data.get("description", "")
        flavors = request.data.get("flavors", [])
        _id = request.data.get("id", None)
        image_url = request.data.get("image", None)
        name = request.data.get("name", None)
        price = request.data.get("price", None)
        _status = request.data.get("status", None)

        if not all([category_id, name, price, image_url, _id]):
            return Response(
                {
                    "code": 0,
                    "msg": "Please fill all the required fields: categoryId, name, price, image",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = Category.objects.filter(id=category_id).first()
        if not category:
            return Response(
                {"code": 0, "msg": "Category does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Dish.objects.filter(id=_id).exists():
            return Response(
                {"code": 0, "msg": "Dish id does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if flavors and not all(
            [flavor.get("name") and flavor.get("value") for flavor in flavors]
        ):
            return Response(
                {
                    "code": 0,
                    "msg": "Please fill all the required fields for flavors: name, value",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_obj = UploadedImage.objects.filter(
            file__exact=from_image_url_to_image_relative_path(image_url)
        ).first()
        if not image_obj:
            return Response(
                {"code": 0, "msg": "Image does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            dish = Dish.objects.get(id=_id)
            dish.category_id = category
            dish.description = description
            dish.image = image_obj
            dish.name = name
            dish.price = price
            dish.update_user = request.user
            dish.save()
            if _status:
                dish.status = _status
                dish.save()
            DishFlavor.objects.filter(dish_id=dish).delete()
            for flavor in flavors:
                DishFlavor.objects.create(
                    dish_id=dish,
                    name=flavor["name"],
                    value=flavor["value"],
                )
        except Exception as e:
            return Response(
                {"code": 0, "msg": f"Failed to update dish: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {
                    "code": 1,
                    "msg": "Dish updated successfully",
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        _ids = request.query_params.get("ids", None)
        ids_list = _ids.split(",") if _ids else []
        if not ids_list:
            return Response(
                {"code": 0, "msg": "Please provide the ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dishes = Dish.objects.filter(id__in=ids_list)
        if dishes.count() != len(ids_list):
            return Response(
                {"code": 0, "msg": "Some of the dish ids do not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            dishes.delete()
        except Exception as e:
            return Response(
                {"code": 0, "msg": f"Failed to delete dish: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {
                    "code": 1,
                    "msg": "Dish deleted successfully",
                },
                status=status.HTTP_200_OK,
            )


class QueryDishByIdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)

        if not _id:
            return Response(
                {"code": 0, "msg": "Please provide the id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dish = Dish.objects.filter(id=_id).first()
        if not dish:
            return Response(
                {"code": 0, "msg": "Dish id does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "code": 1,
                "data": DishSerializer(dish).data,
                "msg": "Get dish data successfully.",
            },
        )


class QueryDishByCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get("categoryId", None)

        if not category_id:
            return Response(
                {"code": 0, "msg": "Please provide the categoryId"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dishes = Dish.objects.filter(category_id=category_id)
        return Response(
            {
                "code": 1,
                "data": DishSerializer(dishes, many=True).data,
                "msg": "Get dish data successfully.",
            },
        )


class ChangeDishStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        dish_id = request.GET.get("id", None)
        dish_status = self.kwargs.get("status", -1)

        if not dish_id:
            return Response(
                {"code": 0, "msg": "Missing dish id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if dish_status not in (0, 1):
            return Response(
                {"code": 0, "msg": "Status code is NOT correct."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query_dish = Dish.objects.filter(id=dish_id)

        if not query_dish.exists():
            return Response(
                {"code": 0, "msg": "Dish do Not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dish = query_dish[0]
        msg = ""
        match (dish.status, dish_status):
            case (0, 0):
                msg = f"Dish (id = {dish_id}) was already BANNED."
            case (1, 1):
                msg = f"Dish (id = {dish_id}) was already ACTIVATED."
            case (0, 1):
                msg = f"Dish (id = {dish_id}) was was ACTIVATED."
            case (1, 0):
                msg = f"Dish (id = {dish_id}) was was LOCKED."

        dish.status = dish_status
        dish.update_user = request.user
        dish.save()

        return Response(
            {"code": 1, "data": DishSerializer(dish).data, "msg": msg},
            status=status.HTTP_200_OK,
        )


class PaginationDishView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name", None)
        page_size = request.query_params.get("pageSize", None)
        category_id = request.query_params.get("categoryId", None)
        _status = request.query_params.get("status", None)

        if not page_size:
            return Response(
                {"code": 0, "data": {}, "msg": "Please fill all the fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        paginator = get_custom_pagination(page_size)
        queryset = Dish.objects.all()
        if name:
            queryset = queryset.filter(name__contains=name)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if _status:
            queryset = queryset.filter(status=_status)

        result_page = paginator.paginate_queryset(queryset, request)
        return Response(
            {
                "code": 1,
                "msg": "Successfully fetched dish",
                "data": {
                    "total": queryset.count(),
                    "records": DishSerializer(result_page, many=True).data,
                },
            }
        )
