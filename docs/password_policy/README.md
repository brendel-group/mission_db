# Password Policy

Currently these rules are active:
1. The password has to be sufficiently different from certain attributes (username and email)
2. It has to be at least 8 characters long
3. It is checked against a list of common passwords and is not allowed to be in that list.
4. It can not be entirely numeric.

These rules are defined in `backend/backend/settings.py` in `AUTH_PASSWORD_VALIDATORS` more about available validators can be found [here](https://docs.djangoproject.com/en/5.1/topics/auth/passwords/#password-validation).