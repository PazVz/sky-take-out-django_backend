from django.urls import path

from .views import (
    CategoryView,
    ChangeCategoryStatusView,
    ChangeDishStatusView,
    DishView,
    PaginationCategoryView,
    PaginationDishView,
    QueryCategoryByTypeView,
    QueryDishByCategoryView,
    QueryDishByIdView,
)

urlpatterns = [
    path("category", CategoryView.as_view(), name="add_or_edit_or_delete_category"),
    path("category/page", PaginationCategoryView.as_view(), name="pagination_category"),
    path(
        "category/status/<int:status>",
        ChangeCategoryStatusView.as_view(),
        name="change_category_status",
    ),
    path(
        "category/list",
        QueryCategoryByTypeView.as_view(),
        name="query_category_by_type",
    ),
    path("dish", DishView.as_view(), name="add_or_edit_or_delete_dish"),
    path("dish/<int:id>", QueryDishByIdView.as_view(), name="query_dish_by_id"),
    path("dish/list", QueryDishByCategoryView.as_view(), name="query_dish_by_category"),
    path("dish/page", PaginationDishView.as_view(), name="pagination_dish"),
    path(
        "dish/status/<int:status>",
        ChangeDishStatusView.as_view(),
        name="change_dish_status",
    ),
]
