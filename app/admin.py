from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "get_roles")


class DipAdmin(admin.ModelAdmin):
    list_display = ("id", "cognome")
    search_fields = ["cognome"]
    list_filter = ["filiale"]


class RespAdmin(admin.ModelAdmin):
    list_display = ("utente", "filiale")


class PresAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ["data", "dipendente__cognome"]
    list_filter = ["filiale"]

    def full_name(self, obj):
        return "{} -> {}".format(obj.data, obj.dipendente.cognome)


class tokenAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created")


class logAdmin(admin.ModelAdmin):
    search_fields = ["azione"]


# Register your models here.
admin.site.unregister(Site)
admin.site.register(models.UserProfile, ProfileAdmin)
admin.register(models.UserProfile)
admin.site.register(models.Role)
admin.site.register(models.Filiale)
admin.site.register(models.Dipendente, DipAdmin)
admin.site.register(models.Responsabile, RespAdmin)
admin.site.register(models.Presenza, PresAdmin)
admin.site.register(models.Consegne)
admin.site.register(models.Zona)
admin.site.register(models.ZonaNuova)
admin.site.register(models.Comunicazione)
admin.site.register(models.Token, tokenAdmin)
admin.site.register(models.ActionLogs, logAdmin)
