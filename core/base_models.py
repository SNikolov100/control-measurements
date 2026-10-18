from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as translate


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=translate("Created at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=translate("Updated at"),
    )

    class Meta:
        abstract = True


class SingleRecordMixin(models.Model):
    def clean(self):
        super().clean()
        model_class = type(self)

        if model_class.objects.exclude(pk=self.pk).exists():
            raise ValidationError(translate("Only one record of this type is allowed."))

    class Meta:
        abstract = True