import settings as s

from fab_helpers import *

env.hosts = s.hosts

def main():
    """
    checks the settings and calls the appropriate setup functions
    """

    if s.single_machine_setup:
        dev_setup()
    else:
        db_setup()
        dev_setup()

#################################
#                               #
#       setup functions         #
#                               #
#################################

def dev_setup():
    "setup dev server machine"
    
    root()
    update_apt()

    user_routine()

    apt_setup()
    pip_setup()

    setup_ssh()
    compile_hosts()

    github_egg_setup()

    with cd("/home/web/"):
        run("git clone git@github.com:%s/%s.git" % (s.github_name, s.github_main_repo))
        run("git clone git@github.com:%s/%s.git" % (s.github_name, s.github_conf_repo))
    with cd("/etc/apache2"):
        sudo("rm -rf apache2.conf conf.d/ httpd.conf magic mods-* sites-* ports.conf")
        sudo("cp /home/web/%s/apache2.conf ." % s.github_conf_repo)
    with cd('/etc/nginx/'):
        sudo('rm -rf conf.d/ fastcgi_params koi-* nginx.conf sites-* win-utf')
        sudo('cp /home/web/%s/nginx.conf .' % s.github_conf_repo)
        sudo('/etc/init.d/nginx start')
    amazon_reload()
    nginx_reload()

    sudo('invoke-rc.d postgresql stop')
    with cd('/etc/postgresql/8.4/main/'):
        sudo('mv postgresql.conf postgresql.conf.orig')
        sudo('mv pg_hba.conf pg_hba.conf.orig')
        sudo("cp /home/web/%s/postgresql.conf ." % s.github_conf_repo)
        sudo("cp /home/web/%s/pg_hba.conf ." % s.github_conf_repo)
    sudo('invoke-rc.d postgresql start')

    sudo('createuser %s -s -d -r' % s.username, user='postgres')
    user('createdb -O %s %s' % (s.username, s.username))

    sudo('echo "export DJANGO_SETTINGS_MODULE=server_settings" >> /etc/profile')
    sudo('echo "export PYTHONPATH=/home/web/%s" >> /etc/profile' % s.github_main_repo)
    sudo('source /etc/profile')

    with cd('/home/web/%s/' % s.github_main_repo):
        run('export DJANGO_SETTINGS_MODULE=%s' % s.settings_module)
        run('export PYTHONPATH=.')
        run('django-admin.py syncdb')
        run('django-admin.py migrate')
        run('ln -s /usr/local/lib/python2.6/dist-packages/django/contrib/admin/media/ siteMedia/admin-media')

