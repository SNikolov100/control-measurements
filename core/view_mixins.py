from django.db.models import ProtectedError
from django.utils.translation import gettext_lazy as translate
from .base_forms import DeleteConfirmationForm

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
