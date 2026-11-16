from django.core import signing
EMAIL_VERIFICATION_SALT = 'accounts.email-verification'
EMAIL_VERIFICATION_MAX_AGE = 60 * 60 * 24

def make_email_verification_token(user):
    data = {'user_id': user.pk, 'email': user.email}
    return signing.dumps(data, salt=EMAIL_VERIFICATION_SALT)

def read_email_verification_token(token):
    return signing.loads(token, salt=EMAIL_VERIFICATION_SALT, max_age=EMAIL_VERIFICATION_MAX_AGE)
