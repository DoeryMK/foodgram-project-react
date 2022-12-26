from rest_framework.pagination import PageNumberPagination, _positive_int


class CustomPagination(PageNumberPagination):

    def get_page_size(self, request):
        page_size_query_param = request.query_params.get('limit')
        if page_size_query_param:
            try:
                return _positive_int(request.query_params.get('limit'),
                                     strict=True,
                                     cutoff=self.max_page_size)
            except (KeyError, ValueError):
                return self.page_size
