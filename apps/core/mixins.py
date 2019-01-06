from rest_framework import mixins


class CreateListRetrieveMixin(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              mixins.RetrieveModelMixin):
    pass
