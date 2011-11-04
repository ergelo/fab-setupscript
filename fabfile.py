from fabric.api import *
from fabric.contrib.console import confirm
import settings as s
import configs as cf

env.hosts = []

def dev_setup():
    "setup dev server machine"
    
    root()
    update_apt()
    createuser()
    make_su(s.username)

    user()
    sudo("mkdir -p /home/web/")
    sudo("chown -R %s /home/web/" % s.username)

    sudo("apt-get --yes install git-core postgresql build-essential python-dev python-setuptools screen python-psycopg2 libpq-dev libjpeg-dev apache2 libapache2-mod-wsgi nginx sendmail") 

    setup_ssh()
    compile_hosts()

    sudo("easy_install pip")
    sudo("pip install django south beautifulsoup simplejson PIL oauth2 py-bcrypt django-piston django-model-utils django-debug-toolbar")

    github_egg('gabrielgrant','django-extensions')
    github_egg('saschwarz','minidetector')

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

#functions to change between connection users
def root():
    "to log in as root"
    local('ssh-add ~/.ssh/%s.pem' % s.pemkey_name)
    env.user = 'root'
    env.keyfilename = '~/.ssh/%s.pem' % s.pemkey_name

def user():
    "to login as user"
    env.user = s.username
    env.password = s.password
    env.keyfilename = ''

#debian management
def createuser():
    "add user and set password"
    run('adduser --disabled-password --gecos "" %s' % s.username)
    run('echo "%s:%s" | chpasswd' % (s.username, s.password))

def make_su(username):
    "make user a su"
    install('sudo')
    run('echo "%s  ALL=(ALL) ALL" >> /etc/sudoers' % s.username)
    run('chmod 440 /etc/sudoers')

#package installing functions
def update_apt():
    "update apt sources"
    run('apt-get update')

def install(package):
    "convenience function for installing a single package"
    run('apt-get install %s' % package)

def github_egg(user, project):
    run('git clone https://github.com/%s/%s.git' % (user, project))
    with cd('%s/' % project):
        sudo('python setup.py install')
    sudo('rm -rf %s' % project)

#networking
def setup_ssh():
    run('ssh-keygen -t dsa -N "" -f ~/.ssh/id_rsa')
    get('.ssh/id_rsa.pub', 'temp_rsa.pub')
    local('cat temp_rsa.pub')
    local('rm temp_rsa.pub')
    
    confirm('Copied key to GitHub?')

    run('git config --global user.name "%s"' % s.github_name)
    run('git config --global user.email "%s"' % s.github_email)

def compile_hosts():
    lines = []
    root()
    # for x in ['web', 'db']:
    #     for i, host in enumerate(env.roledefs[x]):
    #         with settings(host_string=host):
    internal = '.'.join(run('hostname').split('.')[0].split('-')[1:])
    external = '.'.join(env.host_string.split('.')[0].split('-')[1:])
    lines.append('%s %s_dev1_int' % (internal, prefix))
    lines.append('%s %s_dev1_ext' % (external, prefix))
    for l in lines:
        sudo('echo %s >> /etc/hosts' % l)

#webserver functions
def amazon_reload():
    "Reload Apache to pick up new code changes."
    user()
    sudo("invoke-rc.d apache2 reload")

def nginx_reload():
    "Reload nginx"
    user()
    sudo("invoke-rc.d nginx reload")

def nginx_test():
    local('echo "%s" > testnginx.conf' % cf.nginx)
