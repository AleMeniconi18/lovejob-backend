import json
import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework import generics
from rest_framework import status
from app.serializers import (
    ChangePasswordSerializer,
    ComunicazioneSerializer,
    ConsegnaSerializer,
    DipendentiSerializer,
    PresenzaSerializer,
    RoleSerializer,
    ZonaNuovaSerializer,
    ZonaSerializer,
)
from app.models import (
    ActionLogs,
    Comunicazione,
    Consegne,
    Filiale,
    Presenza,
    Responsabile,
    Role,
    User,
    UserProfile,
    Dipendente,
    Zona,
    ZonaNuova,
)
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.functions import Lower
from rest_framework.permissions import IsAuthenticated
import datetime
from dateutil.relativedelta import relativedelta
from django.core.files import File
from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from app.utils import parse_date
from ..permissions import IsResponsabile, IsResponsabileCons, IsSuper, IsUP


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getRole(request):
    """Restituisce ruoli dell'utente autenticato"""
    return Response(RoleSerializer(request.user.profile.roles.all(), many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsResponsabileCons | IsResponsabile)])
def getFiliale(request):
    """Restituisce ID filiale del responsabile autenticato"""
    resp = Responsabile.objects.get(utente=request.user.profile)
    return Response(resp.filiale.id)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def isUP(request):
    up_role = request.user.profile.roles.filter(id=Role.RoleType.UP).exists()
    return Response(data={"message": up_role})


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsUP | IsSuper)])
def getDipendentiPresenze(request):
    """Restituisce tutti i dipendenti"""
    lista = Dipendente.objects.all().order_by("cognome", "nome")
    serial = DipendentiSerializer(lista, many=True)
    return Response(serial.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated & IsUP])
def createOrUpdateDipendente(request):
    """
    Crea o aggiorna dipendente
    Body: nome, cognome, inizioVal (dd-mm-yyyy), fineVal (dd-mm-yyyy),
          filiale, mansione, cat, chiamata, id (opzionale, se presente aggiorna)
    """
    data = request.data

    inizioVal = datetime.datetime.strptime(data.get("inizioVal"), "%d-%m-%Y").date()
    fineVal = datetime.datetime.strptime(data.get("fineVal"), "%d-%m-%Y").date()

    try:
        obj, created = Dipendente.objects.update_or_create(
            id=data.get("id"),
            defaults={
                "nome": data.get("nome"),
                "cognome": data.get("cognome"),
                "inizio_val": inizioVal,
                "fine_val": fineVal,
                "filiale": Filiale.objects.get(id=data["filiale"]),
                "mansione": data.get("mansione"),
                "cat": data.get("cat").upper(),
                "chiamata": data.get("chiamata"),
            },
        )

        ActionLogs.objects.create(
            utente=UserProfile.objects.get(user=request.user.id),
            azione=(f"ha aggiunto/modificato il dipendente {data.get('cognome')}"),
            timestamp=datetime.datetime.now(),
        )
        return Response({"message": "ok", "id": obj.id}, status=status.HTTP_200_OK)

    except (KeyError, ValueError) as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsUP | IsSuper)])
def getReportPresenze(request):
    """Restituisce presenze del mese, filiale e categoria specificati"""
    _data = parse_date(request.GET.get("data"))
    filiale = request.GET.get("filiale", 0)
    cat = request.GET.get("cat", "A")
    mese = _data.month
    anno = _data.year

    lista_presenze = Presenza.objects.filter(
        dipendente__cat=cat, filiale=filiale, data__year=anno, data__month=mese
    )

    pres_serial = PresenzaSerializer(lista_presenze, many=True)

    dipendenti_id = (
        lista_presenze.order_by(Lower("dipendente__cognome"), Lower("dipendente__nome"))
        .values_list("dipendente_id", flat=True)
        .distinct()
    )

    return Response(
        {
            "presenze": pres_serial.data,
            "dipendenti": list(dipendenti_id),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsUP | IsSuper)])
def getReportConsegne(request):
    """Restituisce consegne del mese e filiale specificati"""
    _data = parse_date(request.GET.get("data"))

    filiale = request.GET.get("filiale", 0)
    mese = _data.month
    anno = _data.year

    lista = Consegne.objects.filter(filiale=filiale, data__year=anno, data__month=mese)

    serial = ConsegnaSerializer(lista, many=True)
    return Response(serial.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsUP | IsSuper)])
def getZoneUP(request):
    """Restituisce le zone della filiale specificata"""
    idFiliale = request.GET.get("filiale", 0)
    filiale = Filiale.objects.get(id=idFiliale)

    lista = ZonaNuova.objects.filter(filiale=filiale)
    serial = ZonaNuovaSerializer(lista, many=True)
    return Response(serial.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & IsResponsabile])
def getDipendentiResponsabile(request):
    """Restituisce i dipendenti della filiale del responsabile non ancora inseriti nelle presenze della data specificata"""
    _data = parse_date(request.GET.get("data"))

    cat_ = request.GET.get("cat", "M")

    resp = Responsabile.objects.get(utente=request.user.profile)

    # già inseriti
    esclusi = Presenza.objects.filter(
        data=_data,
        filiale=resp.filiale,
    ).values_list("dipendente_id", flat=True)

    # da inserire
    lista = Dipendente.objects.filter(
        filiale=resp.filiale, inizio_val__lte=_data, fine_val__gte=_data, cat=cat_
    ).exclude(id__in=esclusi)

    serial = DipendentiSerializer(lista, many=True)
    return Response(serial.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsResponsabile | IsResponsabileCons)])
def getAutistiResponsabileAll(request):
    """Restituisce tutti gli autisti della filiale del responsabile autenticato"""
    _data = parse_date(request.GET.get("data"))

    resp = Responsabile.objects.get(utente=request.user.profile)

    lista = Dipendente.objects.filter(
        filiale=resp.filiale, inizio_val__lte=_data, fine_val__gte=_data, cat="A"
    )
    serial = DipendentiSerializer(lista, many=True)
    return Response(serial.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsResponsabile | IsResponsabileCons)])
def getAutistiResponsabileCons(request):
    """Restituisce autisti senza consegne assegnate per la data specificata"""
    _data = parse_date(request.GET.get("data"))

    resp = Responsabile.objects.get(utente=request.user.profile)

    esclusi = Consegne.objects.filter(data=_data, filiale=resp.filiale).values_list(
        "dipendente_id", flat=True
    )
    lista = Dipendente.objects.filter(
        filiale=resp.filiale, inizio_val__lte=_data, fine_val__gte=_data, cat="A"
    ).exclude(id__in=esclusi)

    serial = DipendentiSerializer(lista, many=True)
    return Response(serial.data)


class PresenzeResponsabileView(APIView):
    permission_classes = [IsAuthenticated & IsResponsabile]

    def get(self, request):
        """
        Restituisce le presenze della filiale del responsabile

        Query params: data (yyyy-mm-dd), cat ('A'/'M')
        """
        _data = parse_date(request.GET.get("data"))
        cat_ = request.GET.get("cat", "")
        resp = Responsabile.objects.get(utente=request.user.profile)

        lista = (
            Presenza.objects.filter(
                data=_data, filiale=resp.filiale, dipendente__cat=cat_
            )
            .select_related("dipendente")
            .order_by("dipendente__cognome", "dipendente__nome")
        )

        serial = PresenzaSerializer(lista, many=True)
        return Response(serial.data)

    def post(self, request):
        """
        Salva o modifica le presenze della data specificata.

        Query params: data (yyyy-mm-dd)
        Body: { presenze: { dipendente_id: { presenza, zona, straordinari, ... } } }
        """
        resp = Responsabile.objects.get(utente=request.user.profile)
        _data = parse_date(request.GET.get("data"))

        data = request.data
        with transaction.atomic():
            for dip_id, pres in data.get("presenze").items():
                if pres.get("presenza") == "-":
                    Presenza.objects.filter(
                        dipendente_id=dip_id,
                        data=_data,
                        filiale=resp.filiale,
                    ).delete()
                    continue

                zona_id = 0
                if pres.get("zona") and isinstance(pres.get("zona"), dict):
                    zona_id = pres.get("zona").get("id", 0)

                _, created = Presenza.objects.update_or_create(
                    dipendente_id=dip_id,
                    data=_data,
                    filiale=resp.filiale,
                    defaults={
                        "zona": zona_id,
                        "presenza": pres.get("presenza"),
                        "straordinari": pres.get("straordinari", ""),
                        "macrozona": pres.get("macrozona", ""),
                        "servizi_straordinari": pres.get("serviziStraord", False),
                        "caricato": pres.get("caricato", False),
                        "esenzione": pres.get("esenzione", False),
                        "affiancamento": pres.get("affiancamento", False),
                        "annotazioni": pres.get("annotazioni", ""),
                    },
                )

        lista = Dipendente.objects.filter(filiale=resp.filiale)
        serial = DipendentiSerializer(lista, many=True)
        ActionLogs.objects.create(
            utente=request.user.profile,
            azione=(
                f"ha aggiunto le presenze del {_data}"
                if created
                else f"ha modificato la presenza del {_data} di {Dipendente.objects.get(id=dip_id).cognome}"
            ),
            timestamp=timezone.now(),
        )
        return Response(serial.data)


class ConsegneResponsabileView(APIView):
    permission_classes = [IsAuthenticated & IsResponsabileCons]

    def get(self, request):
        """
        Restituisce consegne della filiale del responsabile autenticato della data specificata
        Query params: data (yyyy-mm-dd)
        """
        _data = parse_date(request.GET.get("data"))
        resp = Responsabile.objects.get(utente=request.user.profile)

        lista = (
            Consegne.objects.filter(data=_data, filiale=resp.filiale)
            .select_related("dipendente")
            .order_by("dipendente__cognome", "dipendente__nome")
        )
        serial = ConsegnaSerializer(lista, many=True)
        return Response(serial.data)

    def post(self, request):
        """
        Salva o modifica le consegne della data specificata.

        Query params: data (yyyy-mm-dd)
        Body: { consegne: { dipendente_id: { ritiri, effettuate, assegnate } } }
        """
        resp = Responsabile.objects.get(utente=request.user.profile)

        _data = parse_date(request.GET.get("data"))

        data = request.data
        with transaction.atomic():
            for dip_id, cons in data.get("consegne").items():
                _, created = Consegne.objects.update_or_create(
                    dipendente_id=dip_id,
                    data=_data,
                    filiale=resp.filiale,
                    defaults={
                        "ritiri": cons.get("ritiri", 0),
                        "effettuate": cons.get("effettuate", 0),
                        "assegnate": cons.get("assegnate", 0),
                    },
                )

        lista = Dipendente.objects.filter(filiale=resp.filiale, cat="A")
        serial = DipendentiSerializer(lista, many=True)
        ActionLogs.objects.create(
            utente=request.user.profile,
            azione=(
                f"ha aggiunto le consegne del {_data}"
                if created
                else f"ha modificato le consegne del {_data} di {Dipendente.objects.get(id=dip_id).cognome}"
            ),
            timestamp=timezone.now(),
        )
        return Response(serial.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & IsSuper])
def getSuperConsegne(request):
    _data = parse_date(request.GET.get("data"))
    filiale_id = request.GET.get("filiale", 0)
    filiale = Filiale.objects.get(id=filiale_id)

    lista = Consegne.objects.filter(data=_data, filiale=filiale).order_by(
        "dipendente__cognome", "dipendente__nome"
    )

    serial = ConsegnaSerializer(lista, many=True)
    return Response(serial.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & IsSuper])
def getSuperPresenze(request):
    _data = parse_date(request.GET.get("data"))
    filiale_id = request.GET.get("filiale", 0)
    filiale = Filiale.objects.get(id=filiale_id)
    cat = request.GET.get("cat", "A")

    lista = Presenza.objects.filter(
        data=_data, filiale=filiale, dipendente__cat=cat
    ).order_by("dipendente__cognome", "dipendente__nome")

    serial = PresenzaSerializer(lista, many=True)
    return Response(serial.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & IsResponsabile])
def getZoneResponsabile(request):
    """Restituisce le zone della filiale del responsabile autenticato"""
    resp = Responsabile.objects.get(utente=request.user.profile)

    lista = ZonaNuova.objects.filter(filiale=resp.filiale)
    serial = ZonaNuovaSerializer(lista, many=True)

    return Response(serial.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated & (IsResponsabile | IsResponsabileCons)])
def getComunicazioni(request):
    """Restituisce comunicazioni alla filiale del responsabile autenticato"""
    resp = Responsabile.objects.get(utente=request.user.profile)
    lista = Comunicazione.objects.filter(
        filiale_id=resp.filiale_id,
    )
    serial = ComunicazioneSerializer(lista, many=True)
    return Response(serial.data)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": [],
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
