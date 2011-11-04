import settings as s

apache = """# Apache conf (/etc/apache2/apache2.conf)

#
# Basic server setup
#
ServerRoot "/etc/apache2"
PidFile ${APACHE_PID_FILE}
User ${APACHE_RUN_USER}
Group ${APACHE_RUN_GROUP}
ServerTokens ProductOnly
ServerAdmin %s
ServerName %s
# Standalone server.
Listen *:8000
NameVirtualHost %s_dev1_int:8000

#
# Worker MPM features
#

Timeout 60
StartServers 2
ServerLimit 4
MinSpareThreads 2
MaxSpareThreads 4
ThreadLimit 10
ThreadsPerChild 10
MaxClients 40
MaxRequestsPerChild 10000

#
# Modules
#

LoadModule mime_module /usr/lib/apache2/modules/mod_mime.so
LoadModule alias_module /usr/lib/apache2/modules/mod_alias.so
LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
LoadModule rewrite_module /usr/lib/apache2/modules/mod_rewrite.so

#
# Logging
#

ErrorLog /var/log/apache2/error.log
CustomLog /var/log/apache2/access.log combined

#
# Default HTTP features
#

AddDefaultCharset utf-8
DefaultType text/plain
TypesConfig /etc/mime.types

#
# virtualhost config
#

<VirtualHost %s_dev1_int:8000>
    ServerAdmin %s
    ServerName %s

    DocumentRoot "/home/web/%s/siteMedia"

    LogLevel warn
    LogFormat "%%h %%l %%u %%t \"%%r\" %%>s %%b \"%%{Referer}i\" \"%%{User-agent}i\"" combined
    ErrorLog /var/log/apache2/error.log
    CustomLog /var/log/apache2/access.log combined

    WSGIScriptAlias / /home/web/%s/apache/django.wsgi
</VirtualHost>
""" % (s.admin_email, s.server_name, s.prefix, s.prefix, s.admin_email, s.server_name, s.github_main_repo, s.github_main_repo)

nginx = """# Nginx conf (/etc/nginx/nginx.conf).

#
# Basic setup
#

user www-data;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;

#
# Event/worker setup.
#
# worker_processes controls the number of forked Nginx processes handling
# requests, general 1-2x the number of processors is a good choice.
# worker_connections controls the number of connections each process takes, so
# the total max connections is (worker_connections * worker_processes).
#
# Nginx can handle a *lot* more connections than an equivalent Apache, so the
# 400 total connections here isn't out of line for a small virtual machine.
#

worker_processes 2;
events {
    worker_connections 100;
}

#
# HTTP configuration
#

http {
    include /etc/nginx/mime.types;

    # HTTP upstream for load balancers.
    upstream %s {
        server %s_dev1_int:8000;
        # weight=2;
        # server 33.33.33.11:8000 weight=3;
        # fair;
    }

    server {
        listen 80;
        server_name %s.com;
        rewrite ^/(.*) http://www.%s.com/$1 permanent;
    }

    server {
        listen 80;
        server_name %s.com;
        rewrite ^/(.*) http://www.%s.com/$1 permanent;
    }

    server {
        listen 80;
        server_name www.%s.com;
        rewrite ^/(.*) http://www.%s.com/$1 permanent;
    }

    # The actual HTTP sever.
    server {
        listen 80;
  	
        server_name www.%s.com;

        # Don't proxy static files like robots.txt and favicon.ico.
        location ~ ^/(favicon.ico|robots.txt|sitemap.xml)$ {
            alias /home/web/%s/siteMedia/assets/$1;
        }

        # Serve media directly out of Nginx for performance
        location /site_media {
            alias /home/web/%s/siteMedia/;
        }

        # Proxy everything else to the backend
        location / {
            proxy_pass http://%s;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;      
            add_header X-Handled-By $upstream_addr;      
        }
    }
}
""" % (s.sitename, s.prefix, s.sitename, s.sitename, s.aliasname, s.sitename, s.aliasname, s.aliasname, s.sitename, s.github_main_repo, s.github_main_repo, s.sitename)

pg_hba = """# Postgres auth. file (/etc/postgresql/8.4/main/pg_hba.conf).

# Trust all connections from localhost
local all all trust

# Trust connections from known web servers.
# host all all 10.XX.XX.XX/32 trust
# host all all 33.33.33.11/32 trust

# If you'd prefer to use password authentication, you'll want something like:
#
# local all all md5
# host all all 10.X.X.X/32 md5
"""

postgresql = """
# PostgreSQL configuration file (/etc/postgresql/8.4/main/postgresql.conf)
#
# The OS-supplied postgresql.conf has every configuration directive known
# to man, and is actually worth reading through carefully. For simplicity,
# though, this is a stripped-down version with only the changes from the
# defaults included.

# Ubuntu puts some files in non-default locations:
data_directory = '/var/lib/postgresql/8.4/main'
hba_file = '/etc/postgresql/8.4/main/pg_hba.conf'
ident_file = '/etc/postgresql/8.4/main/pg_ident.conf'
external_pid_file = '/var/run/postgresql/8.4-main.pid'
unix_socket_directory = '/var/run/postgresql'

#
# Connections and authentication
#

# Listen only on the internal IP interface.
listen_addresses = '%s_dev1_int'
port = 5432

# We'll have pgpool holding up a maximum of 40 connections per server,
# so we need at least 80 connections. Add an additional 5 for superusers,
# monitoring, etc.
max_connections = 85

#
# WAL archiving
#
# Turn this on when it's time to replicate. It'll archive WAL files to
# /pg_standby, where they'll be picked up and moved to the standby server.
#

# archive_mode = on
# archive_command = 'rsync -qarv %%p /pg_archive/%%f > /dev/null'
# archive_timeout = 300 

#
# Logging
#

# Make sure to timestamp the logs.
log_line_prefix = '%%t '

#
# Locale
#
# I think most of the following isn't strictly required, but the OS puts it
# there and I'm not going to remove it without a good reason.
#

datestyle = 'iso, mdy'

# These settings are initialized by initdb, but they can be changed.
lc_messages = 'C'
lc_monetary = 'C'
lc_numeric = 'C'
lc_time = 'C'

# default configuration for text search
default_text_search_config = 'pg_catalog.english'
""" % s.prefix
