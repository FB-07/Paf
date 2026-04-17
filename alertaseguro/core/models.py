from django.db import models
from django.contrib.auth.models import AbstractUser, User

class UsersProfile(models.Model):
    TIPOS = [
        ("admin", "Administrador"),
        ("utilizador", "Utilizador"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_utilizador = models.CharField(max_length=20, choices=TIPOS, default="utilizador")

    class Meta:
        verbose_name = "Perfil de Utilizador"
        verbose_name_plural = "Perfis de Utilizador"

    def __str__(self):
        return f"{self.user.username} ({self.tipo_utilizador})"

class IncidenteAPI(models.Model):
    api_id = models.CharField(max_length=200, unique=True, db_index=True)
    dico = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    created_at_api = models.DateTimeField(blank=True, null=True)
    updated_at_api = models.DateTimeField(blank=True, null=True)

    means_aerial = models.PositiveIntegerField(default=0)
    means_aquatic = models.PositiveIntegerField(default=0)
    means_man = models.PositiveIntegerField(default=0)
    means_terrain = models.PositiveIntegerField(default=0)

    district = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    county = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    parish = models.CharField(max_length=200, blank=True, null=True)
    location_name = models.CharField(max_length=200, blank=True, null=True)
    region = models.CharField(max_length=200, blank=True, null=True)
    subregion = models.CharField(max_length=200, blank=True, null=True)

    coords_ok = models.BooleanField(default=False, db_index=True)
    latitude = models.FloatField(blank=True, null=True, db_index=True)
    longitude = models.FloatField(blank=True, null=True, db_index=True)

    is_fire = models.BooleanField(default=False)
    is_accident = models.BooleanField(default=False)
    is_meteo = models.BooleanField(default=False)

    status_code = models.CharField(max_length=20, blank=True, null=True)
    status_color = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    natureza_code = models.CharField(max_length=20, blank=True, null=True)
    natureza = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    kml = models.TextField(blank=True, null=True)
    significant = models.BooleanField(default=False)

    active = models.BooleanField(default=True, db_index=True)

    icnf_altitude = models.IntegerField(default=0)
    icnf_fogacho = models.BooleanField(default=False)
    icnf_fonte_alerta = models.CharField(max_length=200, blank=True, null=True)

    burned_area = models.CharField(max_length=50, blank=True, null=True)
    burned_area_agricultural = models.CharField(max_length=50, blank=True, null=True)
    burned_area_bush = models.CharField(max_length=50, blank=True, null=True)
    burned_area_forest = models.CharField(max_length=50, blank=True, null=True)
    fire_duration = models.IntegerField(default=0)
    burned_area_created_at = models.CharField(max_length=50, blank=True, null=True)
    burned_area_updated_at = models.CharField(max_length=50, blank=True, null=True)

    fetched_at = models.DateTimeField(auto_now=True)
    raw = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Incidente (API)"
        verbose_name_plural = "Incidentes (API)"

    def __str__(self):
        base = self.natureza or self.category or "Incidente"
        loc = self.location_name or self.county or ""
        return f"{self.api_id} - {base}{(' - ' + loc) if loc else ''}"


class Weather(models.Model):
    incidente = models.OneToOneField(IncidenteAPI, on_delete=models.CASCADE, related_name="weather")

    station = models.CharField(max_length=100, blank=True, null=True)
    distance_km = models.FloatField(blank=True, null=True)

    temperature_c = models.FloatField(blank=True, null=True)
    temperature_min_c = models.FloatField(blank=True, null=True)
    temperature_max_c = models.FloatField(blank=True, null=True)

    humidity_percent = models.IntegerField(blank=True, null=True)
    wind_kmh = models.FloatField(blank=True, null=True)
    precipitation_mmh = models.FloatField(blank=True, null=True)
    pressure_hpa = models.IntegerField(blank=True, null=True)

    description = models.CharField(max_length=100, blank=True, null=True)

    wind_degree = models.IntegerField(blank=True, null=True)
    wind_cardinal = models.CharField(max_length=5, blank=True, null=True)

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tempo"
        verbose_name_plural = "Tempo"

    def __str__(self):
        return f"Weather for {self.incidente.api_id}"


class NearbyFireStation(models.Model):
    incidente = models.ForeignKey(IncidenteAPI, on_delete=models.CASCADE, related_name="nearby_fire_stations")
    name = models.CharField(max_length=200)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    distance = models.CharField(max_length=50, blank=True, null=True)
    logo = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Bombeiros Próximos"
        verbose_name_plural = "Bombeiros Próximos"

    def __str__(self):
        return f"{self.name} ({self.distance or '-'})"


class NearbyEmergency(models.Model):
    incidente = models.ForeignKey(IncidenteAPI, on_delete=models.CASCADE, related_name="nearby_emergencies")
    name = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    distance = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Emergência Próxima"
        verbose_name_plural = "Emergências Próximas"

    def __str__(self):
        return f"{self.name} ({self.distance or '-'})"


class NearbyAirbase(models.Model):
    incidente = models.ForeignKey(IncidenteAPI, on_delete=models.CASCADE, related_name="nearby_airbases")
    name = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    distance = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Base Aérea Próxima"
        verbose_name_plural = "Bases Aéreas Próximas"

    def __str__(self):
        return f"{self.name} ({self.distance or '-'})"


class Hospital(models.Model):
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    standbyTimesUrl = models.URLField(blank=True, null=True)
    shareStandbyTimes = models.CharField(max_length=10, blank=True, null=True)
    hasCTH = models.CharField(max_length=10, blank=True, null=True)
    hasSIGLIC = models.CharField(max_length=10, blank=True, null=True)
    hasEmergency = models.BooleanField(default=False)
    website = models.URLField(blank=True, null=True)
    pilot = models.CharField(max_length=10, blank=True, null=True)
    raw = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitais"

    def __str__(self):
        return self.name


class Bombero(models.Model):
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    logo = models.URLField(blank=True, null=True)
    foundation_date = models.DateField(blank=True, null=True)
    code_cb = models.CharField(max_length=20, blank=True, null=True)
    raw = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Bombeiro / Departamento"
        verbose_name_plural = "Bombeiros / Departamentos"

    def __str__(self):
        return self.name


class AirResource(models.Model):
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    decir = models.CharField(max_length=50, blank=True, null=True)
    raw = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Recurso Aéreo"
        verbose_name_plural = "Recursos Aéreos"

    def __str__(self):
        return self.name


class Aviso(models.Model):
    GRAVIDADE_CHOICES = [
        ("green", "Verde"),
        ("yellow", "Amarelo"),
        ("orange", "Laranja"),
        ("red", "Vermelho"),
    ]
    api_id = models.CharField(max_length=120, unique=True)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    gravidade = models.CharField(max_length=10, choices=GRAVIDADE_CHOICES, default="green")
    dataInicio = models.DateTimeField()
    dataFim = models.DateTimeField()
    idAreaAviso = models.CharField(max_length=10, blank=True)
    AreaNome = models.CharField(max_length=100, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"

    def __str__(self):
        return f"{self.titulo} ({self.gravidade}) {self.dataInicio:%Y-%m-%d %H:%M}"

class Feedback(models.Model):
    TIPOS = [
        ("", "---------"),
        ("sugestao", "Sugestão"),
        ("bug", "Bug"),
        ("outro", "Outro"),
    ]

    PAGINAS = [
        ("home", "Página Inicial"),
        ("doacoes", "Doações"),
        ("perfil", "Perfil"),
        ("informacao", "Informação"),
        ("avisos", "Avisos"),
        ("precaucoes", "Precauções"),
        ("tabela", "Tabela de Incidentes"),
        ("login", "Login"),
        ("registo", "Registo"),
        ("sobre", "Sobre"),
        ("editar_perfil", "Editar Perfil"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()

    pagina = models.CharField(
        max_length=50,
        choices=PAGINAS,
        null=True,
        blank=True
    )

    #imagem = models.ImageField(upload_to="FeedbackForm_images/", null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    resolvido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tipo} | ({self.pagina}) - {self.titulo}"

class Notificacao(models.Model):
    TIPOS = [
        ("IncidenteAPI", "Incidente (API)"),
        ("Aviso", "Aviso"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    tipo = models.CharField(max_length=15, choices=TIPOS)
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"{self.titulo} → {self.user.username}"