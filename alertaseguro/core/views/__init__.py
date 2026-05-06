from .pages import mainpage, sobre, tabela, doacoes, precaucoes, info, feedback
from .avisos import avisos
from .apis import api_incidentes, api_incidentesH, api_bombeiros, api_hospitais, api_aereas
from .ipma import rcm_hoje, rcm_amanha
from .auth import editar_perfil, login_view, registo_view, verify_email, delete_account, logout_view, perfil_view
from .admin import admin_reports
from .cron_import import cron_import
from .poi import bases_aereas, hospitais, bombeiros
from .error import error_400, error_403, error_404, error_500