username = ""
password = ""

github_name = ""
github_username = ""
github_email = ""

github_main_repo = ""
github_conf_repo = ""

settings_module = ""
pemkey_name = ""

prefix = ""

admin_email = ""
server_name = ""

sitename = ""
aliasname = ""

db_name = ""

hosts = []

single_machine_setup = True

dev_packages = [
                "git-core",
                "postgresql",
                "build-essential",
                "python-dev",
                "python-setuptools",
                "screen",
                "python-psycopg2",
                "libpq-dev",
                "libjpeg-dev",
                "apache2",
                "libapache2-mod-wsgi",
                "nginx",
                "sendmail",
                "vim",
            ]

dev_modules = [
                "django",
                "south",
                "beautifulsoup",
                "simplejson",
                "PIL",
                "oauth2",
                "py-bcrypt",
                "django-piston",
                "django-model-utils",
                "django-debug-toolbar",
            ]

dev_github_eggs = [
                {
                    'user': 'gabrielgrant',
                    'project': 'django-extensions'
                },
                {
                    'user': 'saschwarz',
                    'project':'minidetector'
                }
            ]
