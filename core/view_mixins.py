from django.db.models import ProtectedError
from django.utils.translation import gettext_lazy as translate
from .base_forms import DeleteConfirmationForm
from django.db.models import Q

class SingleRecordFormViewMixin:
    model = None

    def get_record(self):
        return self.model.objects.first()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.get_record()
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

class ConfirmedDeleteMixin:
    form_class = DeleteConfirmationForm
    deletion_error_message = translate('This record cannot be deleted because it is currently in use.')

    def is_deletion_blocked(self):
        return False

    def get_deletion_error_message(self):
        return self.deletion_error_message

    def render_deletion_blocked(self, form):
        context = self.get_context_data(form=form)
        context["deletion_blocked"] = True
        context["deletion_error"] = self.get_deletion_error_message()
        return self.render_to_response(context)

    def form_valid(self, form):
        if self.is_deletion_blocked():
            return self.render_deletion_blocked(form)

        try:
            return super().form_valid(form)
        except ProtectedError:
            return self.render_deletion_blocked(form)

class PaginationMixin:
    default_page_size = 10
    page_size_choices = (5, 10, 15, 20, 25, 100)
    page_size_parameter = 'page_size'

    def get_paginate_by(self, queryset):
        requested_page_size = self.request.GET.get(self.page_size_parameter)

        try:
            page_size = int(requested_page_size)
        except (TypeError, ValueError):
            return self.default_page_size

        if page_size not in self.page_size_choices:
            return self.default_page_size

        return page_size

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_page_size = self.get_paginate_by(self.object_list)
        context['page_size_choices'] = self.page_size_choices
        context['current_page_size'] = current_page_size
        query_parameters = self.request.GET.copy()
        query_parameters.pop('page', None)
        context['pagination_query'] = query_parameters.urlencode()
        preserved_parameters = []

        for parameter_name, values in self.request.GET.lists():
            if parameter_name in {"page",self.page_size_parameter}:
                continue

            for value in values:
                preserved_parameters.append(
                    (parameter_name,value,)
                )

        context['pagination_preserved_parameters'] = preserved_parameters
        page_obj = context.get('page_obj')
        paginator = context.get('paginator')

        if page_obj is not None and paginator is not None:
            context['pagination_page_range'] = (paginator.get_elided_page_range(
                    page_obj.number,
                    on_each_side=1,
                    on_ends=1,
                )
            )

            context['pagination_ellipsis'] = paginator.ELLIPSIS

        return context

class SearchMixin:
    search_parameter = 'search'
    search_fields = ()
    search_distinct = False

    def get_search_query(self):
        return self.request.GET.get(self.search_parameter,'',).strip()

    def get_search_fields(self):
        return self.search_fields

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.get_search_query()

        if not search_query:
            return queryset

        search_condition = Q()

        for field_name in self.get_search_fields():
            search_condition |= Q(** {field_name: search_query,})

        queryset = queryset.filter(search_condition)

        if self.search_distinct:
            queryset = queryset.distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.get_search_query()
        context['search_parameter'] = (self.search_parameter)
        preserved_parameters = []

        for parameter_name, values in self.request.GET.lists():
            if parameter_name in {'page',self.search_parameter,}:
                continue

            for value in values:
                preserved_parameters.append(
                    (parameter_name,value,)
                )

        context['search_preserved_parameters'] = preserved_parameters

        return context