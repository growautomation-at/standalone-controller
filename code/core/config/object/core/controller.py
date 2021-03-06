# controller objects
#   holds controller specific config

from core.config.object.base import GaBase
from core.config.object.helper import set_attribute, overwrite_inherited_attribute


class GaControllerModel(GaBase):
    # hardcoded default values
    default_setting_dict = {
        'path_root': '/usr/sbin/ga', 'path_log': '/var/log/ga', 'path_backup': '/mnt/backup/ga',
        'sql_server': 'localhost', 'sql_port': 3306, 'sql_user': 'ga_admin', 'sql_secret': '4t/GdVV9Yd13IJqNbUC/cydeIU+aEO2kkyNIJ8+4Qd2pN2stAq/BrCT27RIgvwYk',
        'sql_database': 'ga', 'log_level': 2, 'debug': False, 'security': False, 'backup': True, 'timezone': 'MEZ', 'device_fail_count': 3,
        'device_fail_sleep': 3600, 'device_log': True,
    }
    setting_list = list(default_setting_dict.keys())

    def __init__(self):
        # inheritance from superclasses
        super().__init__(name='ga_controller_defaults', description='Growautomation controller default values', object_id=1)
        # vars from settings dict
        set_attribute(
            setting_dict=self.default_setting_dict,
            setting_list=self.setting_list,
            instance=self,
            obj=GaControllerModel
        )


class GaControllerDevice(GaBase):
    setting_list = [
        'path_root', 'path_log', 'path_backup', 'sql_server', 'sql_port', 'sql_user', 'sql_secret', 'sql_database', 'log_level', 'debug', 'security',
        'backup', 'timezone', 'device_fail_count', 'device_fail_sleep', 'device_log',
    ]

    def __init__(self, setting_dict: dict, parent_instance: GaControllerModel = None, **kwargs):
        # inheritance from superclasses
        super().__init__(**kwargs)
        # specific vars
        self.parent_instance = parent_instance
        self.setting_dict = setting_dict

        # vars from settings dict
        overwrite_inherited_attribute(
            child_setting_dict=self.setting_dict,
            setting_list=GaControllerModel.setting_list,
            child_instance=self,
            obj=GaControllerDevice
        )

        # more settings could be added - p.e.:
        # enabled, setuptype, install_timestamp, python_path, python_version, version, mnt_log_share, mnt_log_server, mnt_log_pwd,
        # mnt_log_type, -,,- with backup mount, mnt_log, backup time/interval, mnt_log_user, mnt_log_domain,
