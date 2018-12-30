from datetime import datetime, timedelta, time

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from ngdb.utils import get_token
from .models import User, CameLog
from django.contrib.auth.hashers import (
    check_password
)


class CameLogForm(forms.ModelForm):
    class Meta:
        model = CameLog
        fields = ('title', 'info',)

    def get_commit_data(self):
        camelog = super(CameLogForm, self).save(commit=False)

        return camelog
