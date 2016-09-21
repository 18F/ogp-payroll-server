# ogp-payroll-server
Back-end for the OGP Payroll prototype

## Running locally

Install Django, then

    cd server
    export SECRET_KEY=whatever-you-want
    export DJANGO_SETTINGS_MODULE=server.settings.dev
    createdb payroll
    python manage.py migrate

Next, gather XML files of WDOL data, and load
them into the database:

    python manage.py parse_xmldump <path to XML file>

To run the server:

    python manage.py runserver
