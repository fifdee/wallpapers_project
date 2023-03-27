import django.forms
from django.forms import Form
from allauth.account.forms import ResetPasswordForm
from allauth.account.utils import filter_users_by_email


class UserConvertForm(ResetPasswordForm):
    def save(self, request, **kwargs):
        email = self.cleaned_data["email"]

        user = request.user
        if user.is_authenticated:
            user.email = email
            user.save()

        self.users = filter_users_by_email(email, is_active=True)

        if not self.users:
            self._send_unknown_account_mail(request, email)
        else:
            self._send_password_reset_mail(request, email, self.users, **kwargs)
        return email


class SearchForm(Form):
    query = django.forms.CharField(max_length=80, min_length=3, label='')