import datetime

import pytz
from django.utils import timezone


def custom_create_token(token_model, user, serializer):
    token = token_model.objects.create(user=user)
    utc_now = timezone.now()
    utc_now = utc_now.replace(tzinfo=pytz.utc)
    token.created = utc_now
    token.save()
    return token


def parse_date(date_str):
    """Converte data in formato Y-m-d, ritorna oggi se non valida."""
    try:
        clean = date_str.split(" ")[0]
        return datetime.datetime.strptime(clean, "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return timezone.now().date()
