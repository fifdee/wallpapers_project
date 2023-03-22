from django.views import generic
from django.contrib.auth import authenticate, login
from django.conf import settings

from wallpapers.models import User


class CheckIfUserConverted(generic.View):
    def dispatch(self, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated and not self.request.session.get('temp_user_created', None):
            self.request.session['temp_user_created'] = 'created'

            username_part = settings.TEMP_USERNAME_PART
            password_part = settings.TEMP_PASSWORD_PART

            temp_users = User.objects.filter(username__contains=username_part)
            if temp_users.count() > 0:
                next_id = temp_users.last().id + 1
            else:
                next_id = 0

            username = f"{username_part}_{next_id}"
            password = f"{password_part}_{next_id}"

            user = User.objects.create_user(username=username, password=password)

            login(self.request, user, backend='allauth.account.auth_backends.AuthenticationBackend')

        if user.is_authenticated and user.temporary:
            try:
                temp_password_part = settings.TEMP_PASSWORD_PART
                id_part = user.username.split('_')[1]
                password = temp_password_part + '_' + id_part

                temporary = authenticate(self.request, username=user.username, password=password)
                if not temporary:
                    # default credentials don't work - new password was set
                    print('not temporary')
                    user.temporary = False
                    user.save()
            except IndexError:
                ...

        return super(CheckIfUserConverted, self).dispatch(*args, **kwargs)
