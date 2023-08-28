from abc import ABC
import datetime

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin

from .models import City, Address, Systems, Master, Room, Game, Profile


class ArchiveGameFilter(admin.SimpleListFilter, ABC):
    title = "По дате"
    parameter_name = 'game'

    def lookups(self, request, model_admin):
        date = [
            ('year', 'Игры за год'),
            ('month', 'Игры за месяц'),
            ('week', 'Игры за неделю'),
            ('yesterday', 'Игры вчера'),
            ('planned', 'Запланированные'),
        ]
        return date

    def queryset(self, request, queryset):
        if self.value() == 'year':
            return queryset.filter(date__gte=datetime.date.today() - datetime.timedelta(weeks=52),
                                   date__lte=datetime.date.today() - datetime.timedelta(days=1))
        if self.value() == 'month':
            return queryset.filter(date__gte=datetime.date.today() - datetime.timedelta(days=31),
                                   date__lte=datetime.date.today() - datetime.timedelta(days=1))
        if self.value() == 'week':
            return queryset.filter(date__gte=datetime.date.today() - datetime.timedelta(weeks=1),
                                   date__lte=datetime.date.today() - datetime.timedelta(days=1))
        if self.value() == 'yesterday':
            return queryset.filter(date=datetime.date.today() - datetime.timedelta(days=1))
        if self.value() == 'planned':
            return queryset.filter(date__gte=datetime.date.today())
        else:
            return queryset


class MyAdminSite(AdminSite):

    def get_app_list(self, request, **kwargs):
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'])
        return app_list


class CityAdmin(admin.ModelAdmin):
    list_display = ("city", "get_close")
    search_fields = ["city", "close"]
    list_filter = ("close", )

    def get_close(self, obj):
        msg = "Есть филиал(ы)"
        if obj.close:
            msg = "Нет филиалов"
        return msg

    get_close.short_description = "Состояние"


class AddressAdmin(admin.ModelAdmin):
    list_display = ("get_full_address", "get_close")
    search_fields = ["address", "city__city"]
    list_filter = ("city__city", "close")

    def get_full_address(self, obj):
        return str(obj.city) + ", " + str(obj.address)

    def get_close(self, obj):
        msg = "Открыто"
        if obj.close:
            msg = "Закрыто"
        return msg

    get_full_address.short_description = "Адрес"
    get_close.short_description = "Состояние"


class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "get_full_address", "get_close")
    search_fields = ["name", "city__city", "address__address"]
    list_filter = ("city__city",  "address__address", "close")

    def get_full_address(self, obj):
        return str(obj.city) + ", " + str(obj.address)

    def get_close(self, obj):
        msg = "Открыто"
        if obj.close:
            msg = "Закрыто"
        return msg

    get_full_address.short_description = "Адрес"
    get_close.short_description = "Состояние"


class SystemsAdmin(admin.ModelAdmin):
    list_display = ("system", "difficulty_level")
    search_fields = ["system"]
    list_filter = ("difficulty_level", )
    list_editable = ("difficulty_level", )


class MasterAdmin(admin.ModelAdmin):
    list_display = ("get_fullname", "city", "get_job")
    search_fields = ["name", "last_name", "city__city"]
    list_filter = ("city__city", "on_holiday", "fired")

    def get_fullname(self, obj):
        return str(obj.name) + " " + str(obj.last_name)

    def get_job(self, obj):
        msg = "Работает"
        if obj.fired:
            msg = "Уволен"
        elif obj.on_holiday:
            msg = "Отдыхает"
        return msg

    get_fullname.short_description = "Имя"
    get_job.short_description = "Состояние"


class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "get_system_and_type", "date", "time", "room", "master", "price", "total_seats",
                    "filled_seats", "get_state")
    list_filter = (ArchiveGameFilter, "filled_seats", "type_game", "system", "room__name",
                   "room__city__city", "room__address__address", "canceled")
    list_editable = ("filled_seats", )
    search_fields = ["name", "room__name", "room__city__city", "room__address__address", "master__name",
                     "master__last_name", "date", "time", "type_game", "system__system"]

    def get_system_and_type(self, obj):
        return str(obj.system) + "(" + str(obj.type_game) + ")"

    def get_state(self, obj):
        msg = "Запланированна"
        if obj.canceled:
            msg = "Отменена"
        elif obj.date < datetime.date.today():
            msg = "Состоялась"
        return msg

    get_system_and_type.short_description = "Тип игры"
    get_state.short_description = "Состояние"


admin.site = MyAdminSite()
admin.site.register(Group, GroupAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Master, MasterAdmin)
admin.site.register(Systems, SystemsAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Profile)
