import os
import sys

ApplicationDirectory = "current/site_health/"
ApplicationName = "site_health"
VirtualEnvDirectory = (
    "/var/www/vhosts/simonnouwens.nl/site-health.simonnouwens.nl/current/.venv"
)
VirtualEnv = os.path.join(os.getcwd(), VirtualEnvDirectory, "bin", "python")
if sys.executable != VirtualEnv:
    os.execl(VirtualEnv, VirtualEnv, *sys.argv)
sys.path.insert(0, os.path.join(os.getcwd(), ApplicationDirectory))
sys.path.insert(0, os.path.join(os.getcwd(), ApplicationDirectory, ApplicationName))
sys.path.insert(0, os.path.join(os.getcwd(), VirtualEnvDirectory, "bin"))
sys.path.insert(
    0, "/var/www/vhosts/simonnouwens.nl/site-health.simonnouwens.nl/current/"
)
os.chdir(os.path.join(os.getcwd(), ApplicationDirectory))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
