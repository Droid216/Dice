import datetime
import os
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView, ContextMixin
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from .models import Game, Profile, City
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserForm, CustomProfileUserForm, \
    AvatarChangeForm, ChangePasswordForm


class CityMixin(ContextMixin):
    template_name = None
    selected_city = City.objects.order_by('id').first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = City.objects.filter(close=False)
        context['selected_city'] = self.selected_city
        return context

    def dispatch(self, request, *args, **kwargs):
        selected_city_id = request.COOKIES.get('selected_city')
        if selected_city_id:
            self.selected_city = City.objects.get(pk=selected_city_id)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        selected_city_id = request.POST.get('city_id')
        if selected_city_id:
            self.selected_city = City.objects.get(pk=selected_city_id)
            response = self.render_to_response(self.get_context_data())
            response.set_cookie('selected_city', selected_city_id)
            return response
        return super().post(request, *args, **kwargs)


class RegisterLoginMixin(ContextMixin):
    template_name = None
    form_register = CustomUserCreationForm()
    form_login = CustomAuthenticationForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_register'] = self.form_register
        context['form_login'] = self.form_login
        if self.request.user.is_authenticated:
            try:
                profile = Profile.objects.get(user=self.request.user)
                context['profile'] = profile
            except Profile.DoesNotExist:
                pass
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        self.form_register = CustomUserCreationForm(request.POST)
        self.form_login = CustomAuthenticationForm(data=request.POST or None)
        if 'login-btn' in request.POST:
            if self.form_login.is_valid():
                username = self.form_login.cleaned_data['username']
                password = self.form_login.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return self.get(request, *args, **kwargs)
            return render(request, self.template_name, {**context,
                                                        'form_login': self.form_login,
                                                        'show_login': True})
        elif 'register-btn' in request.POST:
            if self.form_register.is_valid():
                user = self.form_register.save()
                Profile.objects.create(user=user)
                login(request, user)
                return self.get(request, *args, **kwargs)
            return render(request, self.template_name, {**context,
                                                        'form_register': self.form_register,
                                                        'show_login': True,
                                                        'show_register': True})
        return render(request, self.template_name, context)


class RecordsView(TemplateView, CityMixin, RegisterLoginMixin):
    template_name = 'record.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get('search_query', '').strip()
        search_fields = ['name__icontains', 'description__icontains', 'system__system__icontains',
                         'type_game__icontains', 'master__name__icontains', 'room__name__icontains',
                         'room__address__address__icontains']
        city_filter = Q(room__city__id__icontains=self.selected_city.id)
        search_filter = Q()
        for field in search_fields:
            search_filter |= Q(**{field: search_query})
        end_filter = city_filter & search_filter
        context['games'] = Game.objects.filter(end_filter)
        context['days'] = Game.objects.filter(
            end_filter,
            canceled=False,
            date__gte=datetime.date.today()).values('date').annotate(count_game=Count('name', distinct=True)).order_by()
        return context


class ProfileView(TemplateView, LoginRequiredMixin, CityMixin):
    template_name = 'profile.html'
    form_avatar = AvatarChangeForm
    form_change = CustomUserForm
    form_profile = CustomProfileUserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        context['profile'] = profile
        context['form_change'] = self.form_change(instance=self.request.user)
        context['form_profile'] = self.form_profile(instance=profile)

        avatars_list = []
        avatar_folder_path = os.path.join(settings.MEDIA_ROOT, settings.AVATAR_FOLDER)

        for filename in os.listdir(avatar_folder_path):
            if filename.endswith('.png'):
                avatar_url = os.path.join(settings.MEDIA_URL, settings.AVATAR_FOLDER, filename)
                avatars_list.append(avatar_url)
        context['avatars_list'] = avatars_list
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        profile = Profile.objects.get(user=request.user)
        if 'logout-btn' in request.POST:
            logout(request)
            return redirect('records')
        if 'avatars-save-btn' in request.POST:
            selected_avatar_url = unquote(request.POST.get('selected_avatar_url').split('uploads/')[-1])
            form = self.form_avatar(request.POST, request.FILES, instance=profile,
                                    initial={'avatars': selected_avatar_url})
            if form.is_valid():
                form.save()
                return redirect('profile')
        if 'profile-save-btn' in request.POST:
            form_change = self.form_change(request.POST, instance=self.request.user)
            form_profile = self.form_profile(request.POST, instance=profile)
            if form_change.is_valid() and form_profile.is_valid():
                form_change.save()
                form_profile.save()
                return redirect('profile')
            else:
                return render(request, self.template_name, {**context,
                                                            'form_change': form_change,
                                                            'form_profile': form_profile})
        return super().post(request, *args, **kwargs)


class ChangePasswordView(TemplateView, LoginRequiredMixin, CityMixin):
    template_name = 'change_password.html'
    form_class = ChangePasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        context['profile'] = profile
        context['form'] = self.form_class(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'change_password-btn' in request.POST:
            form = self.form_class(user=request.user, data=request.POST or None)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return redirect('profile')
            else:
                return render(request, self.template_name, {**context, 'form': form})
        return super().post(request, *args, **kwargs)
