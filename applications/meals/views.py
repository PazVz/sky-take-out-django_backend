import logging

from rest_framework import permissions
from rest_framework.views import APIView

from applications.exceptions import (
    KeyMissingException,
    StatusNotRightException,
)
from applications.file_upload.models import UploadedImage
from applications.utils import (
    from_image_url_to_image_relative_path,
    get_custom_pagination,
    standard_response,
)

from .models import Category, Dish, DishFlavor, Setmeal, SetmealDish
from .serializers import (
    CategoryCreationSerializer,
    CategoryRepresentationSerializer,
    CategoryUpdateSerializer,
    DishCreationSerializer,
    DishRepresentationSerializer,
    DishUpdateSerializer,
    SetmealCreationSerializer,
    SetmealRepresentationSerializer,
    SetmealUpdateSerializer,
)

logger = logging.getLogger(__name__)


class CategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CategoryCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        created_category = Category.objects.create(
            **validated_data, create_user=request.user, update_user=request.user
        )
        response_data = CategoryRepresentationSerializer(created_category).data
        return standard_response(True, "Category created successfully", response_data)

    def put(self, request, *args, **kwargs):
        serializer = CategoryUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        update_category = Category.objects.get(id=validated_data["id"])
        for key, value in validated_data.items():
            setattr(update_category, key, value)
        update_category.update_user = request.user
        update_category.save()
        response_data = CategoryRepresentationSerializer(update_category).data
        return standard_response(True, "Category updated successfully", response_data)

    def delete(self, request, *args, **kwargs):
        _id = request.query_params.get("id", None)

        if not _id:
            raise KeyMissingException(key_name="id", position="query params")

        category = Category.objects.get(id=_id)
        category.delete()
        return standard_response(True, "Category deleted successfully", {})


class QueryCategoryByTypeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        _type = request.query_params.get("type", None)

        categorys = Category.objects.all()
        if _type:
            categorys = Category.objects.filter(type=_type)

        return standard_response(
            True,
            "Category fetched successfully",
            CategoryRepresentationSerializer(categorys, many=True).data,
        )


class ChangeCategoryStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        category_id = request.GET.get("id", None)
        category_status = self.kwargs.get("status", -1)

        if not category_id:
            raise KeyMissingException(key_name="categoryId", position="request data")

        if category_status not in (0, 1):
            raise StatusNotRightException

        category = Category.objects.get(id=category_id)

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

        return standard_response(True, msg)


class PaginationCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        name = request.query_params.get("name", None)
        page_size = request.query_params.get("pageSize", None)
        _type = request.query_params.get("type", None)

        if not page_size:
            raise KeyMissingException(key_name="pageSize", position="request data")

        paginator = get_custom_pagination(page_size)
        queryset = Category.objects.all()
        if name:
            queryset = queryset.filter(name__contains=name)
        if _type:
            queryset = queryset.filter(type=_type)

        result_page = paginator.paginate_queryset(queryset, request)
        return standard_response(
            True,
            "Category fetched successfully",
            {
                "total": queryset.count(),
                "records": CategoryRepresentationSerializer(
                    result_page, many=True
                ).data,
            },
        )


class DishView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = DishCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        created_dish = Dish.objects.create(
            category_id=Category.objects.get(id=validated_data.get("category_id")),
            description=validated_data.get("description"),
            image=UploadedImage.objects.get(
                file=from_image_url_to_image_relative_path(validated_data.get("image"))
            ),
            name=validated_data.get("name"),
            price=validated_data.get("price"),
            create_user=request.user,
            update_user=request.user,
        )
        if _status := validated_data.get("status"):
            created_dish.status = _status
            created_dish.save()
        for flavor in validated_data.get("flavors"):
            DishFlavor.objects.create(
                dish_id=created_dish,
                name=flavor["name"],
                value=flavor["value"],
            )
        response_data = DishRepresentationSerializer(created_dish).data
        return standard_response(True, "Dish created successfully", response_data)

    def put(self, request, *args, **kwargs):
        serializer = DishUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        updated_dish = Dish.objects.get(id=validated_data["id"])

        updated_dish.category_id = Category.objects.get(
            id=validated_data.get("category_id")
        )
        updated_dish.description = validated_data.get("description")
        updated_dish.image = UploadedImage.objects.get(
            file=from_image_url_to_image_relative_path(validated_data.get("image"))
        )
        updated_dish.name = validated_data.get("name")
        updated_dish.price = validated_data.get("price")
        updated_dish.update_user = request.user
        updated_dish.save()
        DishFlavor.objects.filter(dish_id=updated_dish).delete()
        for flavor in validated_data["flavors"]:
            DishFlavor.objects.create(
                dish_id=updated_dish,
                name=flavor["name"],
                value=flavor["value"],
            )
        response_data = DishRepresentationSerializer(updated_dish).data
        return standard_response(True, "Dish updated successfully", response_data)

    def delete(self, request, *args, **kwargs):
        _ids = request.query_params.get("ids", None)
        ids_list = _ids.split(",") if _ids else []
        if not ids_list:
            raise KeyMissingException(key_name="ids", position="query params")
        dishes = Dish.objects.filter(id__in=ids_list)
        dishes.delete()
        return standard_response(True, "Dish deleted successfully")


class QueryDishByIdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)
        dish = Dish.objects.get(id=_id)
        return standard_response(
            True, "Get dish data successfully", DishRepresentationSerializer(dish).data
        )


class QueryDishByCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get("categoryId", None)

        if not category_id:
            raise KeyMissingException(key_name="categoryId", position="query params")
        dishes = Dish.objects.filter(category_id=category_id)
        return standard_response(
            True,
            "Get dish data successfully",
            DishRepresentationSerializer(dishes, many=True).data,
        )


class ChangeDishStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        dish_status = self.kwargs.get("status", -1)
        dish_id = request.GET.get("id", None)

        if not dish_id:
            raise KeyMissingException(key_name="id", position="query params")

        if dish_status not in (0, 1):
            raise StatusNotRightException

        dish = Dish.objects.get(id=dish_id)

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

        return standard_response(True, msg)


class PaginationDishView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name", None)
        page_size = request.query_params.get("pageSize", None)
        category_id = request.query_params.get("categoryId", None)
        _status = request.query_params.get("status", None)

        if not page_size:
            raise KeyMissingException(key_name="pageSize", position="query params")

        paginator = get_custom_pagination(page_size)
        queryset = Dish.objects.all()
        if name:
            queryset = queryset.filter(name__contains=name)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if _status:
            queryset = queryset.filter(status=_status)

        result_page = paginator.paginate_queryset(queryset, request)
        return standard_response(
            True,
            "Successfully fetched dish",
            {
                "total": queryset.count(),
                "records": DishRepresentationSerializer(result_page, many=True).data,
            },
        )


class SetMealView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SetmealCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        created_setmeal = Setmeal.objects.create(
            category_id=Category.objects.get(id=validated_data.get("category_id")),
            description=validated_data.get("description"),
            image=UploadedImage.objects.get(
                file=from_image_url_to_image_relative_path(validated_data.get("image"))
            ),
            name=validated_data.get("name"),
            price=validated_data.get("price"),
            create_user=request.user,
            update_user=request.user,
        )
        if _status := validated_data.get("status"):
            created_setmeal.status = _status
            created_setmeal.save()
        for setmeal_dish in validated_data["setmeal_dishes"]:
            SetmealDish.objects.create(
                setmeal_id=created_setmeal,
                dish_id=Dish.objects.get(id=setmeal_dish["dish_id"]),
                copies=setmeal_dish["copies"],
                name=setmeal_dish["name"],
                price=setmeal_dish["price"],
            )
        return standard_response(True, "Setmeal created successfully", {})

    def put(self, request, *args, **kwargs):
        serializer = SetmealUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        setmeal = Setmeal.objects.get(id=validated_data.get("id"))
        setmeal.category_id = Category.objects.get(id=validated_data.get("category_id"))
        setmeal.description = validated_data.get("description")
        setmeal.image = UploadedImage.objects.get(
            file=from_image_url_to_image_relative_path(validated_data.get("image"))
        )
        setmeal.name = validated_data.get("name")
        setmeal.price = validated_data.get("price")
        setmeal.update_user = request.user
        setmeal.save()
        SetmealDish.objects.filter(setmeal_id=setmeal).delete()
        for setmeal_dish in validated_data["setmeal_dishes"]:
            SetmealDish.objects.create(
                setmeal_id=setmeal,
                dish_id=Dish.objects.get(id=setmeal_dish["dish_id"]),
                copies=setmeal_dish["copies"],
                name=setmeal_dish["name"],
                price=setmeal_dish["price"],
            )
        return standard_response(True, "Setmeal updated successfully", {})

    def delete(self, request, *args, **kwargs):
        _ids = request.query_params.get("ids", None)
        ids_list = _ids.split(",") if _ids else []
        if not ids_list:
            raise KeyMissingException(key_name="ids", position="query params")

        setmeals = Setmeal.objects.filter(id__in=ids_list)
        setmeals.delete()
        return standard_response(True, "Setmeal deleted successfully", {})


class QuerySetmealByIdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        _id = self.kwargs.get("id", None)

        if not _id:
            raise KeyMissingException(key_name="id", position="query params")

        setmeal = Setmeal.objects.get(id=_id)

        return standard_response(
            True,
            "Get setmeal data successfully",
            SetmealRepresentationSerializer(setmeal).data,
        )


class QuerySetmealByCategoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get("categoryId", None)

        if not category_id:
            raise KeyMissingException(key_name="categoryId", position="query params")
        setmeals = Setmeal.objects.filter(category_id=category_id)
        return standard_response(
            True,
            "Get dish data successfully",
            SetmealRepresentationSerializer(setmeals, many=True).data,
        )


class PaginationSetmealView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name", None)
        page_size = request.query_params.get("pageSize", None)
        category_id = request.query_params.get("categoryId", None)
        _status = request.query_params.get("status", None)

        if not page_size:
            raise KeyMissingException(key_name="pageSize", position="query params")

        paginator = get_custom_pagination(page_size)
        queryset = Setmeal.objects.all()
        if name:
            queryset = queryset.filter(name__contains=name)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if _status:
            queryset = queryset.filter(status=_status)

        result_page = paginator.paginate_queryset(queryset, request)
        return standard_response(
            True,
            "Successfully fetched setmeal",
            {
                "total": queryset.count(),
                "records": SetmealRepresentationSerializer(result_page, many=True).data,
            },
        )


class ChangeSetmealStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        setmeal_id = request.GET.get("id", None)
        setmeal_status = self.kwargs.get("status", -1)

        if not setmeal_id:
            raise KeyMissingException(key_name="id", position="query params")

        if setmeal_status not in (0, 1):
            raise StatusNotRightException

        setmeal = Setmeal.objects.get(id=setmeal_id)

        msg = ""
        match (setmeal.status, setmeal_status):
            case (0, 0):
                msg = f"Dish (id = {setmeal_id}) was already BANNED."
            case (1, 1):
                msg = f"Dish (id = {setmeal_id}) was already ACTIVATED."
            case (0, 1):
                msg = f"Dish (id = {setmeal_id}) was was ACTIVATED."
            case (1, 0):
                msg = f"Dish (id = {setmeal_id}) was was LOCKED."

        setmeal.status = setmeal_status
        setmeal.update_user = request.user
        setmeal.save()

        return standard_response(True, msg)
