import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User

from dice_app.models import Profile


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(min_length=3, max_length=20,
                                 widget=forms.TextInput(attrs={'placeholder': 'Имя *',
                                                               'pattern': '^[\wа-яёА-ЯЁ]+$',
                                                               'title': 'Только буквы, цифры и символы подчеркивания (_)'}))
    username = forms.CharField(min_length=5, max_length=20,
                               widget=forms.TextInput(attrs={'placeholder': 'Логин *',
                                                             'pattern': '^(?!_)\w+(?<!_)$',
                                                             'title': 'Только латинские буквы, цифры и символ (_) внутри логина'}))
    password1 = forms.CharField(min_length=8, max_length=20,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Пароль *'}))
    password2 = forms.CharField(min_length=8, max_length=20,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Повтор пароля *'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email *',
                                                            'pattern': '[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$',
                                                            'title': 'Формат email (**@**.**)'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = 'register'

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[\wа-яёА-ЯЁ]+$', first_name):
            raise forms.ValidationError("Только буквы, цифры и символы подчеркивания (_).")
        return first_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^(?!_)[a-zA-Z\d_]+(?<!_)$', username):
            raise forms.ValidationError("Только латинские буквы, цифры и символ (_) внутри логина.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Формат email (**@**.**).")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email.lower()

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not re.match(r'^[a-zA-Z\d!@#$%^&*_]+$', password1):
            raise forms.ValidationError("Только латинские буквы, цифры и специальные символы (!@#$%^&*_).")
        return password1

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'username', 'password1', 'password2', 'email']


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(min_length=5, max_length=20,
                               widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    password = forms.CharField(min_length=8, max_length=20,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = 'login'


class GameSearchForm(forms.Form):
    search_query = forms.CharField(max_length=100,
                                   widget=forms.TextInput(attrs={'placeholder': 'Искать игру...'}))


class CustomUserForm(UserChangeForm):
    first_name = forms.CharField(label='Имя', min_length=3, max_length=20,
                                 widget=forms.TextInput(attrs={'pattern': '^[\wа-яёА-ЯЁ]+$',
                                                               'title': 'Только буквы, цифры и символы подчеркивания (_)'}))
    last_name = forms.CharField(label='Фамилия', min_length=3, max_length=20, required=False,
                                widget=forms.TextInput(attrs={'pattern': '^[\wа-яёА-ЯЁ]+$',
                                                              'title': 'Только буквы, цифры и символы подчеркивания (_)'}))
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'pattern': '[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$',
                                                            'title': 'Формат email (**@**.**)'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = 'profile'

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[\wа-яёА-ЯЁ]+$', first_name):
            raise forms.ValidationError("Только буквы, цифры и символы подчеркивания (_).")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) == 0:
            return last_name
        if not re.match(r'^[\wа-яёА-ЯЁ]+$', last_name):
            raise forms.ValidationError("Только буквы, цифры и символы подчеркивания (_).")
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        username = self.instance.username
        if not re.match(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Формат email '**@**.**'.")
        if User.objects.filter(username=username, email=email).exists():
            return email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CustomProfileUserForm(forms.ModelForm):
    male = forms.ChoiceField(label='Пол', required=False, choices=[('', ''), ('М', 'мужской'), ('Ж', 'женский')])
    birthday = forms.DateField(label='Дата рождения', required=False,
                               widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}))
    city = forms.CharField(label='Город', max_length=20, required=False,
                           widget=forms.TextInput(attrs={'pattern': '^[а-яА-Я]+$',
                                                         'title': 'Только буквы русского алфавита'}))
    phone = forms.CharField(label='Телефон', min_length=11, max_length=11, required=False,
                            widget=forms.TextInput(attrs={'pattern': '^\d+$',
                                                          'title': 'Только цифры'}))
    telegram = forms.CharField(label='Телеграм', max_length=32, required=False,
                               widget=forms.TextInput(attrs={'pattern': '^@[\w\d]+$',
                                                             'title': "Формат телеграм-username начиная с '@'"}))

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if city and not re.match(r'^[а-яА-Я]+$', city):
            raise forms.ValidationError("Только буквы русского алфавита.")
        return city

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\d+$', phone):
            raise forms.ValidationError("Только цифры.")
        return phone

    def clean_telegram(self):
        telegram = self.cleaned_data.get('telegram')
        if telegram and not re.match(r'^@[a-zA-z\d]+$', telegram):
            raise forms.ValidationError("Формат телеграм-username начиная с '@'.")
        return telegram

    class Meta:
        model = Profile
        fields = ['male', 'birthday', 'city', 'phone', 'telegram']


class AvatarChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatars']


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(min_length=8, max_length=20, label='Старый пароль', widget=forms.PasswordInput())
    new_password1 = forms.CharField(min_length=8, max_length=20, label='Новый пароль', widget=forms.PasswordInput())
    new_password2 = forms.CharField(min_length=8, max_length=20, label='Повтор пароля', widget=forms.PasswordInput())

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if not re.match(r'^[a-zA-Z\d!@#$%^&*_]+$', new_password1):
            raise forms.ValidationError("Только латинские буквы, цифры и специальные символы (!@#$%^&*_).")
        return new_password1
