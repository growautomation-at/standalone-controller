from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from time import sleep

from ...user import authorized_to_read, authorized_to_write
from ...config.nav import nav_dict
from ...utils.helper import get_time_difference, develop_subprocess
from ..handlers import handler404

SHELL_SERVICE_STATUS = "/bin/systemctl is-active %s"
SHELL_SERVICE_ENABLED = "/bin/systemctl is-enabled %s"
SHELL_SERVICE_ACTIVE_TIMESTAMP = "/bin/systemctl show -p ActiveEnterTimestamp --value %s"
SHELL_SERVICE_INACTIVE_TIMESTAMP = "/bin/systemctl show -p InactiveEnterTimestamp --value %s"

# need to allow www-data to start/stop/restart/reload services


@user_passes_test(authorized_to_read, login_url='/denied/')
def ServiceView(request):
    service_name_options = {
        'Growautomation': 'ga.service',
        'Apache webserver': 'apache2.service'
    }

    service_status = None
    service_name = None
    service_value = None
    service_runtime = None
    service_status_time = None
    service_enabled = None

    # todo clean up and fix service time counter

    if 'service_name' in request.GET or 'service_name' in request.POST:
        if 'service_name' in request.GET:
            service_name = request.GET['service_name']
        else:
            service_name = request.POST['service_name']

        if service_name not in service_name_options:
            return handler404(request, msg="Service '%s' not manageable" % service_name)

        service_value = service_name_options[service_name]

        service_status = develop_subprocess(SHELL_SERVICE_STATUS % service_value, 'active')
        service_enabled = develop_subprocess(SHELL_SERVICE_ENABLED % service_value, 'enabled')

        if service_status == 'active':
            status_command = SHELL_SERVICE_ACTIVE_TIMESTAMP
        else:
            status_command = SHELL_SERVICE_INACTIVE_TIMESTAMP

        dev_time = str((datetime.now() - timedelta(minutes=5)).strftime('%a %Y-%m-%d %H:%M:%S')) + ' GMT'
        service_status_time = develop_subprocess(status_command % service_value, dev_time)

        if service_status_time is not None and service_status_time != '':
            service_runtime = get_time_difference(service_status_time.rsplit(' ', 1)[0], '%a %Y-%m-%d %H:%M:%S')

    if request.method == 'POST':
        if 'service_name' in request.POST:
            if service_runtime is not None and service_runtime > 60:
                service_action(request, service=service_value)
                sleep(1)

            return redirect("/system/service/?service_name=%s" % service_name.replace(' ', '+'))

    return render(request, 'system/service.html', context={
        'request': request, 'nav_dict': nav_dict, 'service_name': service_name, 'service_value': service_value, 'service_status': service_status,
        'service_name_options': service_name_options, 'service_status_time': service_status_time, 'service_enabled': service_enabled,
        'service_runtime': service_runtime,
    })


@user_passes_test(authorized_to_write, login_url='/denied/')
def service_action(request, service: str):
    # todo: log commands
    systemctl = 'sudo /bin/systemctl'
    if 'service_start' in request.POST:
        develop_subprocess("%s start %s" % (systemctl, service), 'ok')

    elif 'service_reload' in request.POST:
        develop_subprocess("%s reload %s" % (systemctl, service), 'ok')

    elif 'service_restart' in request.POST:
        develop_subprocess("%s restart %s" % (systemctl, service), 'ok')

    elif 'service_stop' in request.POST:
        develop_subprocess("%s stop %s" % (systemctl, service), 'ok')
