from .views import presenze
from django.urls import path, include

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
    path("role/", presenze.getRole),
    path("isUP/", presenze.isUP),
    path("changePassword", presenze.ChangePasswordView.as_view()),
    path("filiale/", presenze.getFiliale),
    path("presenze/dipendenti/", presenze.getDipendentiPresenze),
    path("dipendenti/", presenze.createOrUpdateDipendente),
    path("presenze/report/", presenze.getReportPresenze),
    path("consegne/report/", presenze.getReportConsegne),
    path("presenze/zone/", presenze.getZoneUP),
    path("responsabile/presenze/dipendenti/", presenze.getDipendentiResponsabile),
    path("responsabile/presenze/autisti/", presenze.getAutistiResponsabileAll),
    path(
        "responsabile/presenze/autisti/consegne/", presenze.getAutistiResponsabileCons
    ),
    path("responsabile/presenze/", presenze.PresenzeResponsabileView.as_view()),
    path("responsabile/presenze/zone/", presenze.getZoneResponsabile),
    path("responsabile/consegne/", presenze.ConsegneResponsabileView.as_view()),
    path("responsabile/presenze/comunicazioni/", presenze.getComunicazioni),
    path("super/consegne/", presenze.getSuperConsegne),
    path("super/presenze/", presenze.getSuperPresenze),
]
