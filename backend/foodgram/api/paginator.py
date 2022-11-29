from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'limit'
    max_page_size = 3
    page_query_param = 'page'

