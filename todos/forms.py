import os

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Todo


class PrefilledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.render_value = True

        if not self.is_bound:
            self.fields['username'].initial = os.environ.get(
                'DJANGO_SUPERUSER_USERNAME',
                'admin',
            )
            self.fields['password'].initial = os.environ.get(
                'DJANGO_SUPERUSER_PASSWORD',
                '',
            )

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
