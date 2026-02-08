from django.db import models

# Create your models here.

from django.contrib.auth.models import User


# -----------------------------
#  TIPOS DE INCIDENTE
# -----------------------------
class TipoIncidente(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


# -----------------------------
#  PERFIL DO UTILIZADOR
# -----------------------------
class UsersProfile(models.Model):
    TIPOS = [
        ('admin', 'Administrador'),
        ('utilizador', 'Utilizador')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_utilizador = models.CharField(max_length=20, choices=TIPOS, default='utilizador')

    def __str__(self):
        return f"{self.user.username} ({self.tipo_utilizador})"


# -----------------------------
#  INCIDENTES
# -----------------------------
class Incidente(models.Model):
    GRAVIDADES = [
        (1, 'Baixa'),
        (2, 'Média'),
        (3, 'Alta'),
    ]

    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    tipo = models.ForeignKey(TipoIncidente, on_delete=models.CASCADE)
    gravidade = models.IntegerField(choices=GRAVIDADES)
    latitude = models.FloatField()
    longitude = models.FloatField()
    data_ocorrencia = models.DateTimeField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} ({self.tipo.nome})"


# -----------------------------
#  AVISOS
# -----------------------------

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
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} ({self.gravidade}) {self.dataInicio:%Y-%m-%d %H:%M}"


# -----------------------------
#  NOTIFICAÇÕES
# -----------------------------
class Notificacao(models.Model):
    TIPOS = [
        ('Incidente', 'Incidente'),
        ('Aviso', 'Aviso'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    tipo = models.CharField(max_length=15, choices=TIPOS)
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} → {self.user.username}"


# -----------------------------
#  HISTÓRICO DE AÇÕES EM INCIDENTES
# -----------------------------
class HistoricoIncidentes(models.Model):
    ACOES = [
        ('Criado', 'Criado'),
        ('Atualizado', 'Atualizado'),
        ('Encerrado', 'Encerrado'),
    ]

    incidente = models.ForeignKey(Incidente, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=20, choices=ACOES)
    descricao = models.TextField()
    data_acao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.acao} | {self.incidente.titulo}"
