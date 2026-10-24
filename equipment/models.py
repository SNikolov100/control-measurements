from django.db import models, transaction
from django.utils.text import slugify
from core.model_mixins import TimestampMixin, AutoSlugMixin, TextNormalizationMixin
from django.utils.translation import gettext_lazy as translate
from django.core.validators import MinValueValidator

class EquipmentType(TextNormalizationMixin, TimestampMixin):
    strip_fields = ('name', 'short_name', 'description',)
    class IntervalUnit(models.TextChoices):
        DAYS = 'days', translate('Days')
        MONTHS = 'months', translate('Months')
        YEARS = 'years', translate('Years')

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=translate('Name'),
    )
    short_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=translate('Short name'),
    )
    specialty = models.ForeignKey(
        'core.Specialty',
        on_delete=models.PROTECT,
        related_name='equipment_types',
        verbose_name=translate("Specialty"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=translate('Description'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=translate('Active'),
    )
    default_interval_value = models.PositiveSmallIntegerField(
        default=12,
        validators=[MinValueValidator(1)],
        verbose_name=translate('Default interval value'),
    )
    default_interval_unit = models.CharField(
        max_length=10,
        choices=IntervalUnit.choices,
        default=IntervalUnit.MONTHS,
        verbose_name=translate('Default interval unit'),
    )
    default_inspection_duration = models.PositiveSmallIntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        verbose_name=translate('Default inspection duration in minutes'),
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = translate('Equipment type')
        verbose_name_plural = translate('Equipment types')


class Equipment(TextNormalizationMixin, AutoSlugMixin, TimestampMixin):
    strip_fields = ('model_name', 'serial_number', 'inventory_number', 'notes',)
    uppercase_fields = ('serial_number', 'inventory_number',)

    class Status(models.TextChoices):
        IN_SERVICE = 'in_service', translate('In service')
        WAITING_INSPECTION = 'waiting_inspection', translate('Waiting for inspection')
        UNDER_INSPECTION = 'under_inspection', translate('Under inspection')
        UNDER_REPAIR = 'under_repair', translate('Under repair')
        WAITING_REINSPECTION = 'waiting_reinspection', translate('Waiting for reinspection')
        TEMPORARILY_SUSPENDED = 'temporarily_suspended', translate('Temporarily suspended')
        DECOMMISSIONED = 'decommissioned', translate('Decommissioned')

    customer_site = models.ForeignKey(
        'customers.CustomerSite',
        on_delete=models.PROTECT,
        related_name='equipment_items',
        verbose_name=translate('Customer site'),
    )
    equipment_type = models.ForeignKey(
        'EquipmentType',
        on_delete=models.PROTECT,
        related_name='equipment_items',
        verbose_name=translate('Equipment type')
    )
    model_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=translate('Model name'),
    )
    serial_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=translate('Serial number'),
    )
    inventory_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=translate('Inventory number'),
    )
    is_active = models.BooleanField(
        default=True,
        editable=False,
        verbose_name=translate('Active'),
    )
    inspection_interval_value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=translate("Inspection interval value"),
    )
    inspection_interval_unit = models.CharField(
        max_length=10,
        choices=EquipmentType.IntervalUnit.choices,
        verbose_name=translate("Inspection interval unit"),
    )
    estimated_inspection_duration = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=translate("Estimated inspection duration in minutes"),
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.IN_SERVICE,
        verbose_name=translate("Status"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=translate("Notes"),
    )

    def save(self, *args, **kwargs):
        self.is_active = (self.status != self.Status.DECOMMISSIONED)
        update_fields = kwargs.get("update_fields")

        if update_fields is not None:
            kwargs["update_fields"] = (set(update_fields) | {"is_active"})
        super().save(*args, **kwargs)

    def build_slug(self):
        type_slug = slugify(self.equipment_type.short_name, allow_unicode=True,)
        serial_slug = slugify(self.serial_number, allow_unicode=True,)

        return f"{self.pk}-{type_slug}-{serial_slug}"

    def change_status(self, new_status, reason="", notes=""):
        valid_statuses = {status.value for status in self.Status}

        if new_status not in valid_statuses:
            raise ValueError("Invalid equipment status.")

        if self.pk is None:
            raise ValueError("Equipment must be saved before its status can be changed.")

        if new_status == self.status:
            return False

        previous_status = self.status

        with transaction.atomic():
            self.status = new_status
            self.save(update_fields={"status"})
            EquipmentStatusHistory.objects.create(
                equipment=self,
                previous_status=previous_status,
                new_status=new_status,
                reason=reason.strip(),
                notes=notes.strip(),
            )
        return True

    def __str__(self):
        return f"{self.equipment_type.short_name} - {self.serial_number}"

    class Meta:
        ordering = (
            'customer_site__customer__company_name',
            'customer_site__name',
            'equipment_type__name',
            'serial_number',
        )
        verbose_name = translate('Equipment')
        verbose_name_plural = translate('Equipment')

class EquipmentStatusHistory(models.Model):
    equipment = models.ForeignKey(
        'Equipment',
        on_delete=models.PROTECT,
        related_name='status_history',
        verbose_name=translate('Equipment'),
    )
    previous_status = models.CharField(
        max_length=30,
        choices=Equipment.Status.choices,
        blank=True,
        verbose_name=translate('Previous status'),
    )
    new_status = models.CharField(
        max_length=30,
        choices=Equipment.Status.choices,
        verbose_name=translate('New status'),
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=translate('Reason'),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=translate('Notes'),
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=translate('Changed at')
    )

    def __str__(self):
        if self.previous_status:
            return (f"{self.equipment}:"
                    f" {self.get_previous_status_display()}"
                    f" -> {self.get_new_status_display()}"
            )
        return f"{self.equipment}: {self.get_new_status_display()}"

    class Meta:
        ordering = ("-changed_at",)
        verbose_name = translate("Equipment status history")
        verbose_name_plural = translate("Equipment status histories")




