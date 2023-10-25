from rest_framework.pagination import PageNumberPagination

PAGE_LIMIT = 6


class CustomPagination(PageNumberPagination):
    """Отвечает за количество результатов в выдаче."""

    page_size = PAGE_LIMIT
    page_size_query_param = "limit"
