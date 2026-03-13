from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token as AuthToken
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinLengthValidator


class Token(AuthToken):
    key = models.CharField("Key", max_length=40, db_index=True, unique=True)
    user = models.ForeignKey(
        User,
        related_name="auth_token",
        on_delete=models.CASCADE,
        verbose_name="User",
    )


class Role(models.Model):

    class RoleType(models.IntegerChoices):
        DIPENDENTE = 1, "dipendente"
        RESPONSABILE = 2, "responsabile"
        SUPER = 3, "super"
        UP = 4, "up"
        RESPONSABILE_CONS = 5, "responsabile_cons"
        TEST = 6, "test"
        AMMINISTRAZIONE = 7, "amministrazione"

    id = models.PositiveSmallIntegerField(
        choices=RoleType.choices, default=RoleType.DIPENDENTE, primary_key=True
    )

    def __str__(self):
        return self.get_id_display()


@receiver(post_save, sender=User)
def create_userprofile(sender, instance, created, **kwargs):
    if created:
        profile, create = UserProfile.objects.get_or_create(user=instance)
        if create:
            role_default, _ = Role.objects.get_or_create(id=Role.RoleType.DIPENDENTE)
            profile.roles.add(role_default)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="utente", related_name="profile"
    )
    roles = models.ManyToManyField(Role)
    cf = models.CharField(
        unique=True,
        blank=True,
        null=True,  # solo perché è unique
        max_length=16,
        validators=[MinLengthValidator(16)],
    )

    def get_roles(self):
        return ", ".join([str(p) for p in self.roles.all()])

    get_roles.short_description = "ruoli"

    def __str__(self):
        return self.user.username


class Filiale(models.Model):
    nome = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Filiali"

    def __str__(self) -> str:
        return f"{self.nome}"


class Dipendente(models.Model):
    nome = models.CharField(max_length=200, blank=True)
    cognome = models.CharField(max_length=200)
    inizio_val = models.DateField()
    fine_val = models.DateField()
    filiale = models.ForeignKey(Filiale, on_delete=models.SET_NULL, null=True)
    mansione = models.CharField(max_length=200, blank=True)
    cat = models.CharField(max_length=1, default="A")
    chiamata = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Dipendenti"
        ordering = ("cognome",)

    def __str__(self) -> str:
        return f"{self.cognome}"


class Responsabile(models.Model):
    utente = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    filiale = models.ForeignKey(Filiale, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Responsabili"

    def __str__(self) -> str:
        return f"{self.utente.user.last_name} {self.utente.user.first_name}"


class Presenza(models.Model):

    class PresenzaType(models.TextChoices):
        SI = "si", "PRESENTE"
        MEZZA = "mez", "MEZZA GIORNATA"
        NO = "no", "NO"
        FERIE = "fer", "FERIE"
        MALATTIA = "mal", "MAL"
        INFORTUNIO = "inf", "INF"
        L104 = "104", "104"
        MATTINA = "mat", "MATTINA"
        INTERA = "int", "INTERA GIORNATA"
        PERM_SINDACALE = "sin", "PERMESSO SINDAC"

    dipendente = models.ForeignKey(
        Dipendente, on_delete=models.CASCADE, related_name="presenze"
    )
    data = models.DateField()
    presenza = models.CharField(
        max_length=3, choices=PresenzaType.choices, default=PresenzaType.SI
    )
    zona = models.PositiveIntegerField()
    macrozona = models.CharField(max_length=2, blank=True, default="")
    straordinari = models.CharField(max_length=50, blank=True, default="")
    caricato = models.BooleanField(default=False)
    servizi_straordinari = models.BooleanField(default=False)
    esenzione = models.BooleanField(default=False)
    affiancamento = models.BooleanField(default=False)
    annotazioni = models.CharField(max_length=300, blank=True, default="")
    filiale = models.ForeignKey(Filiale, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Presenze"
        unique_together = ["dipendente", "data"]

    def __str__(self) -> str:
        return f"{self.data} - {self.dipendente}"


class Consegne(models.Model):
    dipendente = models.ForeignKey(
        Dipendente, on_delete=models.CASCADE, related_name="consegne"
    )
    data = models.DateField()
    effettuate = models.PositiveIntegerField(default=0)
    assegnate = models.PositiveIntegerField(default=0)
    ritiri = models.PositiveIntegerField(default=0)
    filiale = models.ForeignKey(Filiale, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Consegne"
        unique_together = ["dipendente", "data"]

    def __str__(self) -> str:
        return f"{self.data} - {self.dipendente}"


class Zona(models.Model):
    comune = models.CharField(max_length=200)
    zona = models.CharField(max_length=200)
    filiale = models.ForeignKey(Filiale, on_delete=models.CASCADE)
    soglia = models.PositiveSmallIntegerField()
    valore = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.id} - {self.comune[0:15]}"

    class Meta:
        verbose_name_plural = "Zone"


class ZonaNuova(models.Model):
    numero = models.PositiveSmallIntegerField()
    comune = models.CharField(max_length=200, blank=True)
    zona = models.CharField(max_length=200)
    filiale = models.ForeignKey(Filiale, on_delete=models.CASCADE)
    soglia = models.PositiveSmallIntegerField()
    valore = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.numero} - {self.zona} - {self.filiale}"

    class Meta:
        verbose_name_plural = "ZoneNuove"


class ActionLogs(models.Model):
    utente = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="Utente",
    )
    azione = models.CharField(max_length=200)
    timestamp = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.utente}  {self.azione}"


class Comunicazione(models.Model):
    filiale = models.ForeignKey(Filiale, on_delete=models.CASCADE)
    testo = models.TextField()

    def __str__(self) -> str:
        return f"{self.filiale}"

    class Meta:
        verbose_name_plural = "Comunicazioni"
