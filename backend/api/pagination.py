from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Отвечает за количество результатов в выдаче."""

    page_size = 6
    page_size_query_param = "limit"
