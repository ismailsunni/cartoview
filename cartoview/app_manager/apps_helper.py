import importlib
import os
import shutil
from subprocess import Popen
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.sites.models import Site
import json

current_folder, filename = os.path.split(os.path.abspath(__file__))


def app_url(app_name):
    app = str(app_name)
    return url(r'^' + app + '/', include('%s.urls' % app), name=app + '_base_url')


def import_app_rest(app_name):
    try:
        # print 'define %s rest api ....' % app_name
        module_ = importlib.import_module('%s.rest' % app_name)
    except ImportError:
        pass


def register_app_urls(app_name):
    from urls import urlpatterns
    urlpatterns.append(app_url(app_name))
    import_app_rest(app_name)
    # rest_api.register_app_urls(app_name)
    from django.contrib import admin
    admin.autodiscover()

    print 'app urls registerd.'


def get_apps_names():
    return [n for n in os.listdir(settings.APPS_DIR) if os.path.isdir(os.path.join(settings.APPS_DIR, n))]

def run_batch_file(path, params=None, cwd=current_folder):
    p = Popen(path)
    stdout, stderr = p.communicate()
    return stdout, stderr


def delete_installed_app(app):
    app_path = os.path.join(settings.APPS_DIR, app.name)
    shutil.rmtree(app_path)


def install_app(app_name):
    from django.conf import settings
    settings.INSTALLED_APPS += (app_name,)
    from django.db.models.loading import load_app
    load_app(app_name)
    from django.core.management import call_command
    call_command('syncdb', load_initial_data=False)
    call_command('collectstatic', interactive=False)
    try:
        print os.path.join(settings.APPS_DIR, app_name, 'fixtures')
        call_command('loaddata', os.path.join(settings.APPS_DIR, app_name, 'fixtures', 'initial_data.json'))
    except Exception:
        pass
    # from urls import register_app_urls
    register_app_urls(app_name)


def get_url(url_name):
    from django.core.urlresolvers import reverse
    try:
        return reverse(url_name)
    except:
        return None

def installed_apps():
    from .models import App
    apps = App.objects.filter(is_suspended=False).order_by('order')
    return apps


