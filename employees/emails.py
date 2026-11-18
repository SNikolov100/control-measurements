from django.conf import settings
from django.core.mail import send_mail
from .choices import EmployeeRequestStatus


def send_employee_request_result_email(email, status):
    if status == EmployeeRequestStatus.APPROVED:
        subject = 'Employee access approved - Control Measurements'
        message = (
            'Hello,\n\n'
            'Your employee access request has been approved.\n'
            'You can now access Control Measurements.\n'
        )

    elif status == EmployeeRequestStatus.REJECTED:
        subject = 'Employee access request - Control Measurements'
        message = (
            'Hello,\n\n'
            'Your employee access request has been rejected.\n'
            'Please contact the administrator if you have questions.\n'
        )

    else:
        raise ValueError('Invalid employee request status.')

    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
