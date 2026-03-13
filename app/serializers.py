from django.utils import timezone

from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from django.conf import settings
from rest_framework import serializers
from .models import (
    Comunicazione,
    Consegne,
    Presenza,
    Role,
    User,
    Dipendente,
    Zona,
    ZonaNuova,
    Token,
)


class NewLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = data.get("user")
        if user:
            # elimina token scaduti
            limite_scadenza = timezone.now() - settings.TOKEN_TTL
            Token.objects.filter(user=user, created__lt=limite_scadenza).delete()

        return data


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RoleSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source="get_id_display", read_only=True)

    class Meta:
        model = Role
        fields = ("id", "nome")


class DipendentiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dipendente
        fields = (
            "id",
            "nome",
            "cognome",
            "inizio_val",
            "fine_val",
            "filiale",
            "mansione",
            "cat",
            "chiamata",
        )


class PresenzaSerializer(serializers.ModelSerializer):
    cognome = serializers.ReadOnlyField(source="dipendente.cognome")
    nome = serializers.ReadOnlyField(source="dipendente.nome")
    dip = serializers.ReadOnlyField(source="dipendente_id")
    chiamata = serializers.ReadOnlyField(source="dipendente.chiamata")

    class Meta:
        model = Presenza
        fields = (
            "id",
            "dip",
            "cognome",
            "nome",
            "chiamata",
            "presenza",
            "zona",
            "macrozona",
            "caricato",
            "straordinari",
            "servizi_straordinari",
            "annotazioni",
            "esenzione",
            "affiancamento",
            "filiale",
            "data",
        )


class ConsegnaSerializer(serializers.ModelSerializer):
    cognome = serializers.ReadOnlyField(source="dipendente.cognome")
    nome = serializers.ReadOnlyField(source="dipendente.nome")
    dip = serializers.ReadOnlyField(source="dipendente.id")

    class Meta:
        model = Consegne
        fields = (
            "id",
            "dip",
            "cognome",
            "nome",
            "assegnate",
            "effettuate",
            "ritiri",
            "filiale",
            "data",
        )


class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = (
            "id",
            "zona",
            "comune",
            "filiale",
            "soglia",
            "valore",
        )


class ZonaNuovaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonaNuova
        fields = (
            "id",
            "numero",
            "zona",
            "comune",
            "filiale",
            "soglia",
            "valore",
        )


class ComunicazioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunicazione
        fields = (
            "filiale",
            "testo",
        )
