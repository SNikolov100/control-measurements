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