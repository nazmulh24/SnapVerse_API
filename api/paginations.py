from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class FollowPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class PostPagination(PageNumberPagination):
    page_size = 15  # 15 posts per page (good for social media)
    page_size_query_param = "page_size"
    max_page_size = 50  # Maximum 50 posts per page


class CommentPagination(PageNumberPagination):
    page_size = 20  # 20 comments per page
    page_size_query_param = "page_size"
    max_page_size = 50  # Maximum 50 comments per page
