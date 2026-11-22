from accounts.models import AppUser, Person
from .forms import EmployeeRequestReviewForm
from .models import Employee, EmployeeRequest
from django.utils.translation import gettext_lazy as translate
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from .models import EmployeeHistory
from .choices import EmployeeRequestAction, PersonNameSource, PersonPhoneSource
from functools import partial
from .emails import send_employee_request_result_email
from django.core.files.uploadedfile import UploadedFile


def ensure_employee_request(user):
    if user.registration_status != AppUser.RegistrationStatus.APPROVED:
        raise ValueError(translate('User account is not approved.'))

    person = user.person
    if person is None or not person.is_profile_complete:
        raise ValueError(translate('The user profile is incomplete.'))

    if Employee.objects.filter(user=user).exists():
        return None, False

    employee_request, created = EmployeeRequest.objects.get_or_create(
        user=user,
        status=EmployeeRequest.Status.PENDING,
    )

    return employee_request, created


@transaction.atomic
def review_employee_request(*,
    request_id: int,
    reviewer,
    action: str,
    role: Group | None = None,
    employee=None,
    note: str = '',
    confirm_name_difference: bool = False,
    name_source: str | None = None,
    phone_source: str | None = None):

    if not reviewer.is_authenticated or not reviewer.is_superuser:
        raise PermissionDenied

    if action not in EmployeeRequestAction.values:
        raise ValidationError(translate('Invalid action.'))

    note = note.strip()
    if action == EmployeeRequestAction.REJECT and not note:
        raise ValidationError(translate('Rejection reason is required.'))

    group = None
    if action != EmployeeRequestAction.REJECT:
        if not isinstance(role, Group) or role.pk is None:
            raise ValidationError(translate('Select a valid permission group.'))
        group = Group.objects.filter(pk=role.pk).first()
        if group is None:
            raise ValidationError(translate('The selected group no longer exists.'))

    if action == EmployeeRequestAction.LINK and employee is None:
        raise ValidationError(translate('Select an employee.'))

    new_status = EmployeeRequest.Status.REJECTED if action == EmployeeRequestAction.REJECT else EmployeeRequest.Status.APPROVED
    updated = (EmployeeRequest.objects
        .filter(pk=request_id, status=EmployeeRequest.Status.PENDING)
        .update(status=new_status, reviewed_by=reviewer, reviewed_at=timezone.now(), review_note=note,)
    )
    if updated != 1:
        raise ValidationError(translate('This request has already been processed.'))

    employee_request = EmployeeRequest.objects.select_related('user', 'user__person').get(pk=request_id)
    if action == EmployeeRequestAction.REJECT:
        transaction.on_commit(
            partial(send_employee_request_result_email, employee_request.user.email, employee_request.status),
            robust=True,
        )
        return employee_request

    user = AppUser.objects.select_for_update().get(pk=employee_request.user_id)
    if user.registration_status != user.RegistrationStatus.APPROVED:
        raise ValidationError(translate('User account is not approved.'))

    if user.is_superuser:
        raise ValidationError(translate('Cannot link a superuser account.'))

    person = user.person
    if person is None or not person.is_profile_complete:
        raise ValidationError(translate('The user profile is incomplete.'))

    if Employee.objects.filter(user=user).exists():
        raise ValidationError(translate('This user already has an employee record.'))

    history_details = []
    if action == EmployeeRequestAction.CREATE:
        employee = Employee.objects.create(person=person, user=user)
        event_type = EmployeeHistory.EventType.CREATED

    else:
        employee = (Employee.objects
            .select_for_update()
            .filter(pk=employee.pk, user__isnull=True, is_active=True)
            .first()
        )

        if employee is None:
            raise ValidationError(translate('The selected employee is no longer available.'))

        if employee.person_id is None:
            raise ValidationError(translate('The selected employee has no personal record.'))

        person_ids = (person.pk, employee.person_id)
        locked_persons = {obj.pk: obj for obj in Person.objects.select_for_update().filter(pk__in=person_ids).order_by('pk')}

        if len(locked_persons) != 2:
            raise ValidationError(translate('Both personal records must exist and be different.'))

        person = locked_persons[person.pk]
        employee_person = locked_persons[employee.person_id]
        if not person.is_profile_complete:
            raise ValidationError(translate('The user personal profile is no longer complete.'))

        if AppUser.objects.filter(person_id=employee_person.pk).exists():
            raise ValidationError(translate('The selected employee personal record is already linked to a user account.'))

        account_email = person.email.strip().lower()
        employee_email = employee_person.email.strip().lower()
        if user.email.strip().lower() != account_email:
            raise ValidationError( translate('The account email does not match the personal record email.'))

        if not employee_email or employee_email != account_email:
            raise ValidationError(translate("The employee's email must match the account email. Check the employee's personal record before linking."))

        account_name = person.get_full_name()
        employee_name = employee_person.get_full_name()
        normalized_account_name = ' '.join(account_name.split()).casefold()
        normalized_employee_name = ' '.join(employee_name.split()).casefold()
        names_differ = normalized_account_name != normalized_employee_name
        phone_differs = bool(employee_person.phone and person.phone and employee_person.phone.strip() != person.phone.strip())
        link_errors = []
        if names_differ:
            if not confirm_name_difference:
                link_errors.append(
                    ValidationError(
                        translate(
                            'The employee name (%(employee_name)s) differs '
                            'from the account name (%(account_name)s). '
                            'Confirm that both records belong to the same person.'
                        ),
                        params={'employee_name': employee_name, 'account_name': account_name},
                        code='name_mismatch',
                    )
                )
            elif name_source not in PersonNameSource.values:
                link_errors.append(ValidationError(translate('Choose which names to keep.'), code='name_source_required'))

        if phone_differs and phone_source not in PersonPhoneSource.values:
            link_errors.append(ValidationError(
                translate('The employee and account phone numbers differ. Choose which phone number to keep.'),
                code='phone_source_required'
                )
            )

        if link_errors:
            raise ValidationError(link_errors)

        if names_differ and name_source == PersonNameSource.ACCOUNT:
            chosen_names = (person.first_name, person.middle_name, person.last_name)
        else:
            chosen_names = (employee_person.first_name, employee_person.middle_name, employee_person.last_name)

        personal_fields = ('date_of_birth', 'address', 'photo')
        conflicting_fields = []

        for field in personal_fields:
            employee_value = getattr(employee_person, field)
            account_value = getattr(person, field)

            if employee_value and account_value and str(employee_value).strip() != str(account_value).strip():
                conflicting_fields.append(field)

        if conflicting_fields:
            raise ValidationError(
                translate('Conflicting personal data: %(fields)s. Resolve the differences before linking the account.'),
                params={'fields': ', '.join(conflicting_fields)},
                code='personal_data_conflict',
            )

        merged_personal_data = {}
        for field in personal_fields:
            employee_value = getattr(employee_person, field)
            account_value = getattr(person, field)

            if not employee_value and account_value:
                merged_personal_data[field] = account_value

        if phone_differs:
            if phone_source == PersonPhoneSource.ACCOUNT:
                merged_personal_data['phone'] = person.phone
            history_details.append(f'Phone difference resolved. Selected phone source: "{phone_source}".')

        elif not employee_person.phone and person.phone:
            merged_personal_data['phone'] = person.phone

        employee_person.first_name, employee_person.middle_name, employee_person.last_name = chosen_names
        for field, value in merged_personal_data.items():
            setattr(employee_person, field, value)

        if person.pk == employee_person.pk:
            raise ValidationError(translate('The account and employee already share the same person.'))

        if not person.login_email_reserved:
            raise ValidationError(translate('The account email is not reserved.'))

        if employee_person.login_email_reserved:
            raise ValidationError(translate('The employee email is already reserved.'))

        person.login_email_reserved = False
        person.save(update_fields=['login_email_reserved'])
        employee_person.login_email_reserved = True
        employee_person.save(update_fields=['login_email_reserved'])
        user.person = employee_person
        user.save(update_fields=['person'])
        fields_to_update = ['first_name', 'middle_name', 'last_name', *merged_personal_data.keys()]
        employee_person.save(update_fields=fields_to_update)

        if names_differ:
            history_details.append(f'Name difference confirmed: employee "{employee_name}", account "{account_name}". Selected name source: "{name_source}".')

        employee.person = employee_person
        updates = {
            'user': user,
            'slug': employee.build_slug(),
            'updated_at': timezone.now(),
        }
        updated_employee = (Employee.objects
            .filter(pk=employee.pk, person_id=employee_person.pk, user__isnull=True, is_active=True)
            .update(**updates)
        )
        if updated_employee != 1:
            raise ValidationError(translate('The employee record changed during review. Reload the page and check the details again.'))

        if AppUser.objects.filter(person_id=person.pk).exists() or Employee.objects.filter(person_id=person.pk).exists():
            raise ValidationError(translate('The temporary personal record is still in use.'))

        person.delete()
        employee.refresh_from_db()
        event_type = EmployeeHistory.EventType.UPDATED

    history_description = f'Account linked to {user.username} by {reviewer.username} via request #{request_id}.'
    if history_details:
        history_description += ' ' + ' '.join(history_details)

    EmployeeHistory.objects.create(employee=employee, event_type=event_type, description=history_description)
    user.groups.set([group])
    EmployeeRequest.objects.filter(pk=request_id,).update(employee=employee)
    employee_request.employee = employee
    transaction.on_commit(
        partial(send_employee_request_result_email, employee_request.user.email, employee_request.status),
        robust=True,
    )

    return employee_request


@transaction.atomic
def reconsider_employee_request(*, request_id: int, reviewer, note: str):
    if not reviewer.is_authenticated or not reviewer.is_superuser:
        raise PermissionDenied

    note = note.strip()
    if not note:
        raise ValidationError(translate('Reconsideration reason is required.'))

    old_request = (
        EmployeeRequest.objects
        .select_for_update()
        .select_related('user')
        .filter(pk=request_id, status=EmployeeRequest.Status.REJECTED)
        .first()
    )
    if old_request is None:
        raise ValidationError(translate('The request is not rejected or does not exist.'))

    if EmployeeRequest.objects.filter(reconsidered_from=old_request).exists():
        raise ValidationError(translate('This request has already been reconsidered.'))

    user = old_request.user
    if not user.is_active or user.is_superuser or user.registration_status != user.RegistrationStatus.APPROVED or not user.email_verified:
        raise ValidationError(translate('The user account is not eligible for reconsideration.'))

    person = user.person
    if person is None or not person.is_profile_complete:
        raise ValidationError(translate('The user profile is incomplete.'))

    if Employee.objects.filter(user=user).exists():
        raise ValidationError(translate('This user already has an employee record.'))

    if EmployeeRequest.objects.filter(user=user, status=EmployeeRequest.Status.PENDING).exists():
        raise ValidationError(translate('The user already has a pending request.'))

    new_request = EmployeeRequest.objects.create(
        user=user,
        status=EmployeeRequest.Status.PENDING,
        reconsidered_from=old_request,
        reconsidered_by=reviewer,
        reconsideration_note=note,
    )

    return new_request


@transaction.atomic
def create_employee_from_form(form):
    uploaded_photo = form.cleaned_data['photo']
    person = Person.objects.create(
        first_name=form.cleaned_data['first_name'],
        middle_name=form.cleaned_data['middle_name'],
        last_name=form.cleaned_data['last_name'],
        email=form.cleaned_data['email'],
        phone=form.cleaned_data['phone'],
        photo=uploaded_photo,
        login_email_reserved=False,
    )
    employee = form.save(commit=False)
    employee.person = person
    employee.save()
    form.save_m2m()
    return employee


def delete_unused_person_photo(photo_name: str):
    if not photo_name:
        return

    is_used = Person.objects.filter(photo=photo_name).exists()
    if is_used:
        return

    storage = Person._meta.get_field('photo').storage
    storage.delete(photo_name)



@transaction.atomic
def update_employee_from_form(form):
    employee = Employee.objects.select_for_update().get(pk=form.instance.pk)

    if employee.person_id is None:
        raise ValidationError(translate('The employee has no linked personal record.'))

    person = Person.objects.select_for_update().get(pk=employee.person_id)
    old_photo_name = person.photo.name if person.photo else None
    new_email = form.cleaned_data['email'].strip().lower()
    current_email = person.email.strip().lower()
    has_account = AppUser.objects.filter(person_id=person.pk).exists()
    if has_account != person.login_email_reserved:
        raise ValidationError(translate('The personal record has an inconsistent email reservation state.'))

    if has_account and (new_email != current_email):
        raise ValidationError(translate('This employee has a linked user account. The email address cannot be changed from this form.'))

    new_names = {
        'first_name': form.cleaned_data['first_name'],
        'middle_name': form.cleaned_data['middle_name'],
        'last_name': form.cleaned_data['last_name'],
    }
    new_personal_data = {**new_names, 'phone': form.cleaned_data['phone'], 'email': new_email}
    new_photo = form.cleaned_data['photo']
    for field, value in new_personal_data.items():
        setattr(person, field, value)

    if new_photo is False:
        person.photo = None
    elif isinstance(new_photo, UploadedFile):
        person.photo = new_photo

    fields_to_update = list(new_personal_data.keys())
    if new_photo is False or isinstance(new_photo, UploadedFile):
        fields_to_update.append('photo')

    person.save(update_fields=fields_to_update)
    employee.person = person
    Employee.objects.filter(pk=employee.pk).update(
        position=form.cleaned_data['position'],
        notes=form.cleaned_data['notes'],
        updated_at=timezone.now(),
        slug=employee.build_slug(),
    )
    employee.specialties.set(form.cleaned_data['specialties'])
    employee.refresh_from_db()
    new_photo_name = person.photo.name if person.photo else None

    if old_photo_name and old_photo_name != new_photo_name:
        transaction.on_commit(
            partial(delete_unused_person_photo, old_photo_name),
            robust=True,
        )

    return employee