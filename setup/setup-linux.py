#!/usr/bin/python3
# This file is part of Growautomation
#     Copyright (C) 2020  René Pascal Rath
#
#     Growautomation is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#     E-Mail: rene.rath@growautomation.at
#     Web: https://git.growautomation.at

########################################################################################################################

from os import popen as os_popen
from os import path as os_path
from os import system as os_system
from os import getuid as os_getuid
from os import listdir as os_listdir
from datetime import datetime
from getpass import getpass
from random import choice as random_choice
from string import ascii_letters as string_ascii_letters
from string import digits as string_digits
from sys import version_info as sys_version_info
from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe

# basic vars
ga_config = {}
ga_config_server = {}
ga_config["version"] = "0.2"
ga_config["setup_version_file"] = "/etc/growautomation.version"
ga_config["setup_log_path"] = "/var/log/growautomation/"
ga_config["setup_log"] = "%ssetup_%s.log" % (ga_config["setup_log_path"], datetime.now().strftime("%Y-%m-%d_%H-%M"))
ga_config["setup_log_redirect"] = " 2>&1 | tee -a %s" % ga_config["setup_log"]


########################################################################################################################


# shell output
def ga_setup_shelloutput_header(output, symbol):
    shellhight, shellwidth = os_popen('stty size', 'r').read().split()
    print("\n%s\n%s\n%s\n" % (symbol * (int(shellwidth) - 1), output, symbol * (int(shellwidth) - 1)))
    ga_setup_log_write("\n%s\n%s\n%s\n" % (symbol * 36, output, symbol * 36))


def ga_setup_shelloutput_colors(style):
    if style == "warn":
        return colorama_fore.YELLOW
    elif style == "info":
        return colorama_fore.CYAN
    elif style == "err":
        return colorama_fore.RED
    elif style == "succ":
        return colorama_fore.GREEN
    else:
        return ""


def ga_setup_shelloutput_text(output, style="", point=True):
    styletype = ga_setup_shelloutput_colors(style)
    if point is True:
        print(styletype + "%s.\n" % output + colorama_fore.RESET)
    else:
        print(styletype + "%s\n" % output + colorama_fore.RESET)
    ga_setup_log_write(output)


def ga_setup_log_write(output, special=False):
    if os_path.exists(ga_config["setup_log_path"]) is False:
        os_system("mkdir -p %s %s" % (ga_config["setup_log_path"], ga_config["setup_log_redirect"]))
    tmplog = open(ga_config["setup_log"], "a")
    if special is True:
        tmplog.write(output)
    else:
        tmplog.write("\n" + output + "\n")
    tmplog.close()


def ga_log_write_vars():
    ga_setup_log_write("Setup vars:")

    def write(thatdict):
        for key, value in sorted(thatdict.items()):
            if "pwd" in key:
                pass
            else:
                ga_setup_log_write("%s - %s" % (key, value), True)
    write(ga_config)
    write(ga_config_server)


def ga_setup_pwd_gen(stringlength):
    chars = string_ascii_letters + string_digits + "!#-_"
    return ''.join(random_choice(chars) for i in range(stringlength))


def ga_setup_string_check(string, maxlength=10, minlength=2):
    char_blacklist = "!%$§?^´`µ{}()°><|\\*ÄÖÜüöä@,"
    if type(string) != "str":
        ga_setup_shelloutput_text("Input error. Expected string, got %s" % type(string), style="warn")
        return False
    elif len(string) > maxlength or len(string) < minlength:
        ga_setup_shelloutput_text("Input error. Input must be between %s and %s characters long" % (minlength, maxlength), style="warn")
        return False
    elif any((char in char_blacklist) for char in string):
        ga_setup_shelloutput_text("Input error. Input must not include the following characters: %s" % char_blacklist, style="warn")
        return False
    else:
        return True


def ga_setup_fstabcheck():
    with open("/etc/fstab", 'r') as readfile:
        stringcount = readfile.read().count("Growautomation")
        if stringcount > 0:
            ga_setup_shelloutput_text("WARNING!\nYou already have one or more remote shares configured.\nIf you want"
                                      " to install new ones you should disable the old ones by editing the "
                                      "'/etc/fstab' file.\nJust add a '#' in front of the old shares or delete "
                                      "those lines to disable them", style="warn")


def ga_setup_input(prompt, default="", poss="", intype="", style="", posstype="str", maxchar=10, minchar=2):
    styletype = ga_setup_shelloutput_colors(style)

    def ga_setup_input_posscheck():
        while True:
            try:
                if posstype == "str":
                    usrinput = str(input(styletype + "\n%s\n(Poss: %s - Default: %s)\n > " % (prompt, poss, default) + colorama_fore.RESET).lower() or default)
                elif posstype == "int":
                    usrinput = int(input(styletype + "\n%s\n(Poss: %s - Default: %s)\n > " % (prompt, poss, default) + colorama_fore.RESET).lower() or default)
                if type(poss) == list:
                    if usrinput in poss:
                        break
                elif type(poss) == str:
                    if usrinput == poss:
                        break
            except KeyError:
                ga_setup_shelloutput_text("Input error. Choose one of the following: %s\n" % poss, style="warn")
        return usrinput

    whilecount = 0
    if type(default) == bool:
        while True:
            try:
                return {"true": True, "false": False, "yes": True, "no": False, "y": True, "n": False, "f": False, "t": True,
                        "": default}[input(styletype + "\n%s\n(Poss: yes/true/no/false - Default: %s)\n > " % (prompt, default) + colorama_fore.RESET).lower()]
            except KeyError:
                ga_setup_shelloutput_text("WARNING: Invalid input please enter either yes/true/no/false!\n", style="warn", point=False)
    elif type(default) == str:
        if intype == "pass" and default != "":
            getpass(prompt="\n%s\n(Random: %s)\n > " % (prompt, default)) or "%s" % default
        elif intype == "pass":
            getpass(prompt="\n%s\n > " % prompt)
        elif intype == "passgen":
            usrinput = 0
            while usrinput < 8 or usrinput > 99:
                if (usrinput < 8 or usrinput > 99) and whilecount > 0:
                    ga_setup_shelloutput_text("Input error. Value should be between 8 and 99.\n", style="warn")
                whilecount += 1
                usrinput = int(input("\n%s\n(Poss: %s - Default: %s)\n > " % (prompt, poss, default)).lower() or "%s" % default)
            return usrinput
        elif intype == "free":
            if poss != "":
                return ga_setup_string_check(ga_setup_input_posscheck(), maxlength=maxchar, minlength=minchar)
        elif poss != "":
            return ga_setup_input_posscheck()
        elif default != "":
            return str(input(styletype + "\n%s\n(Default: %s)\n > " % (prompt, default) + colorama_fore.RESET).lower() or "%s" % default)
        else:
            return str(input(styletype + "\n%s\n > " % prompt + colorama_fore.RESET).lower())


def ga_mnt_creds(outtype, inputstr=""):
    if outtype == "usr":
        return ga_setup_input("Provide username for share authentication.", inputstr)
    elif outtype == "pwd":
        return ga_setup_input("Provide password for share authentication.", inputstr, intype="pass")
    elif outtype == "dom":
        return ga_setup_input("Provide domain for share authentication.", "workgroup")


def ga_setup_keycheck(dictkey):
    dict = ga_config
    if dict[dictkey] is None:
        ga_setup_log_write("WARNING! Dict key %s has value of None" % dictkey)
        return False
    elif dictkey in dict:
        return True
    else:
        ga_setup_log_write("WARNING! Dict key not found" % dictkey)
        return False


class ga_mysql(object):
    def __init__(self, dbinput, user="", pwd="", query=False):
        self.input = dbinput
        self.user = user
        self.pwd = pwd
        self.query = query
        self.start()

    def unixsock(self):
        global ga_config
        sql_sock = "/var/run/mysqld/mysqld.sock"
        if os_path.exists(sql_sock) is False:
            output, error = subprocess_popen(["systemctl status mysql.service | grep 'Active:'"], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
            outputstr = output.decode("ascii")
            if outputstr.find("Active: inactive") != -1:
                os_system("systemctl start mysql.service %s" % ga_config["setup_log_redirect"])
            if os_path.exists(sql_sock) is False:
                sql_customsock = ga_setup_input("Mysql was unable to find the mysql unix socket file at %s.\nThe path can be found in mysql via "
                                                "the command:\n > show variables like 'socket;'\nProvide the correct path to it.")
                ga_config["sql_sock"] = sql_customsock
                return sql_customsock
        else:
            ga_config["sql_sock"] = sql_sock
            return sql_sock

    def execute(self, command):
        if ga_config["sql_server_ip"] == "127.0.0.1":
            connection = mysql.connector.connect(host=ga_config["sql_server_ip"], port=ga_config["sql_server_port"], unix_socket=self.unixsock(), user=self.user, passwd=self.pwd)
        else:
            connection = mysql.connector.connect(host=ga_config["sql_server_ip"], port=ga_config["sql_server_port"], user=self.user, passwd=self.pwd)
        try:
            curser = connection.cursor(buffered=True)
            curser.execute(command)
            if self.query is True:
                data = curser.fetchall()
            else:
                connection.commit()
            curser.close()
            connection.close()
            if self.query is True:
                return data
            else:
                return True
        except mysql.connector.Error as error:
            connection.rollback()
            ga_setup_shelloutput_text("MySql was unable to perform action '%s'.\nError message:\n%s" % (command, error), style="warn")
            return False

    def start(self):
        if self.user == "":
            self.user = "root"

        if type(self.input) == str:
            return self.execute(self.input)
        elif type(self.input) == list:
            outputdict = {}
            anyfalse = True
            for command in self.input:
                output = self.execute(command)
                outputdict[command] = output
                if output is False:
                    anyfalse = False
            if anyfalse is False:
                return False
            return outputdict


def ga_mysql_conntest(dbuser="", dbpwd="", special=False):
    if (dbuser == "" or dbuser == "root") and ga_config["sql_server_ip"] == "127.0.0.1":
        if special is True:
            sqltest = ga_mysql("SELECT * FROM ga.AgentConfig ORDER BY changed DESC LIMIT 10;", "root", query=True)
        else:
            sqltest = ga_mysql("SELECT * FROM mysql.help_category LIMIT 10;", "root", query=True)
    elif dbpwd == "":
        return False
    else:
        sqltest = ga_mysql("SELECT * FROM ga.AgentConfig ORDER BY changed DESC LIMIT 10;", dbuser, dbpwd, True)
    if type(sqltest) == list:
        return True
    else:
        return False


class ga_setup_configparser_mysql(object):
    def __init__(self, search, user, pwd, agent="", table="config"):
        self.search = search
        self.user = user
        self.pwd = pwd
        self.agent = agent
        self.table = table
        self.start()

    def command(self):
        if self.table == "config":
            if self.agent == "":
                command_table = "Server"
                command_agents = ""
            else:
                command_table = "Agent"
                command_agents = " and agent = '%s'" % self.agent
            return "SELECT data FROM ga.%sConfig WHERE name = '%s'%s" % (command_table, self.search, command_agents)
        elif self.table == "devicetype" or self.table == "device":
            if self.table == "devicetype": command_table = "DeviceType"
            elif self.table == "device": command_table = "Device"
            return "SELECT data FROM ga.AgentConfig%sSetting WHERE setting = '%s'" % (command_table, self.search)

    def start(self):
        if type(self.search) == list:
            itemdatadict = {}
            for item in self.search:
                itemdatadict[item] = ga_mysql(self.command(), self.user, self.pwd, True)
            return itemdatadict
        elif type(self.search) == str:
            data = ga_mysql(self.command(), self.user, self.pwd, True)
            return data


def ga_setup_configparser_file(file, text):
    tmpfile = open(file, 'r')
    for line in tmpfile.readlines():
        if line.find(text) != -1:
            return line
    return False


def ga_setup_exit(shell, log):
    ga_log_write_vars()
    ga_setup_log_write("\nExit. %s.\n\n" % log)
    raise SystemExit(ga_setup_shelloutput_colors("err") + "\n%s!\nYou can find the full setup log at %s.\n\n" % (shell, ga_config["setup_log"]) + colorama_fore.RESET)


########################################################################################################################


ga_setup_log_write(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# prechecks
ga_setup_shelloutput_header("Installing setup dependencies", "#")

os_system("apt-get -y install python3-pip && python3 -m pip install mysql-connector-python colorama %s" % ga_config["setup_log_redirect"])
import mysql.connector
from colorama import Fore as colorama_fore


# check for root privileges
if os_getuid() != 0:
    ga_setup_exit("This script needs to be run with root privileges", "Script not started as root")

else:
    ga_setup_shelloutput_header("Starting Growautomation installation script\n"
                                "The newest versions can be found at: https://git.growautomation.at", "#")
    ga_config["setup_warning"] = ga_setup_input("WARNING!\n\nWe recommend using this installation script on dedicated systems.\n"
                                                "This installation script won't check your already installed programs for compatibility problems.\n"
                                                "If you already use web-/database or other complex software on this system you should back it up before installing this software.\n"
                                                "We assume no liability for problems that may be caused by this installation!\n\n"
                                                "Accept the risk if you want to continue.", False, style="warn")
    if ga_config["setup_warning"] is False:
        ga_setup_exit("Script cancelled by user\nYou can also install this software manually through the setup "
                      "manual.\nIt can be found at: https://git.growautomation.at/tree/master/manual",
                      "Setupwarning not accepted by user")

ga_setup_shelloutput_header("Checking if growautomation is already installed on the system", "#")

# check if growautomation is already installed
if os_path.exists(ga_config["setup_version_file"]) is True or os_path.exists("/etc/growautomation") is True:
    ga_setup_shelloutput_text("Growautomation version file or default root path found", style="info")


    def ga_config_vars_oldversion_replace():
        global ga_config
        ga_config["setup_old"] = True
        ga_config["setup_old_replace"] = ga_setup_input("Do you want to replace your current growautomation installation?", False, style="warn")
        if ga_config["setup_old_replace"] is True:
            ga_config["setup_old_replace_migrate"] = ga_setup_input("Should we try to keep your old configuration and data?", False, style="warn")
            if ga_config["setup_old_replace_migrate"] is True:
                ga_config["setup_fresh"] = False
            else:
                ga_config["setup_fresh"] = True
        if ga_config["setup_old_replace"] is True:
            ga_config["setup_old_backup"] = ga_setup_input("Do you want to backup your old growautomation installation?", True)
        else:
            ga_setup_exit("Stopping script. Current installation should not be overwritten",
                          "User chose that currently installed ga should not be overwritten")


    if os_path.exists(ga_config["setup_version_file"]) is True:
        ga_versionfile_line = ga_setup_configparser_file(ga_config["setup_version_file"], "version=")
        if ga_versionfile_line is False:
            if os_path.exists("/etc/growautomation") is True:
                ga_setup_shelloutput_text("Growautomation is currently installed. But its version number could not be found", style="warn")
                ga_config_vars_oldversion_replace()
            else:
                ga_setup_shelloutput_text("No data for previous growautomation installation found. Installing as new", style="warn")
                ga_config["setup_old"] = False
        else:
            print("A version of growautomation is/was already installed on this system!\n\n"
                  "Installed version: %s\nReplace version: %s" % (ga_versionfile_line[8:], ga_config["version"]))
            ga_config_vars_oldversion_replace()
    elif os_path.exists("/etc/growautomation") is True:
        ga_setup_shelloutput_text("Growautomation is currently installed. But its version number could not be found", style="warn")
        ga_config_vars_oldversion_replace()
else:
    ga_setup_shelloutput_text("No previous growautomation installation found", style="info")
    ga_config["setup_old"] = False

if ga_config["setup_old"] is False:
    ga_config["setup_fresh"] = True
    ga_config["setup_old_backup"] = False
    ga_setup_shelloutput_text("Growautomation will be installed completely new", style="succ")
else:
    ga_setup_shelloutput_text("Growautomation will be migrated to the new version", style="succ")
    if ga_config["setup_fresh"] is True:
        ga_setup_shelloutput_text("The configuration and data will be overwritten", style="warn")
    else:
        ga_setup_shelloutput_text("The configuration and data will be migrated", style="succ")

########################################################################################################################

# setup vars
ga_setup_shelloutput_header("Retrieving setup configuration through user input", "#")


def ga_config_var_base():
    global ga_config
    ga_setup_shelloutput_header("Checking basic information", "-")

    def ga_config_var_base_name():
        global ga_config
        if ga_config["setup_type"] == "agent":
            ga_config["hostname"] = ga_setup_input("Provide the name of this growautomation agent as configured on the server.", "gacon01")
        elif ga_config["setup_type"] == "server":
            ga_config["hostname"] = "gaserver"
        elif ga_config["setup_type"] == "standalone":
            ga_config["hostname"] = "gacon01"

    if ga_config["setup_fresh"] is False:
        ga_config["path_root"] = ga_setup_configparser_file(ga_config["setup_version_file"], "garoot=")[7:]
        ga_config["hostname"] = ga_setup_configparser_file(ga_config["setup_version_file"], "name=")[5:]
        ga_config["setup_type"] = ga_setup_configparser_file(ga_config["setup_version_file"], "type=")[5:]
        if ga_config["path_root"] is False:
            ga_setup_shelloutput_text("Growautomation rootpath not found in old versionfile", style="warn")
            ga_config["path_root"] = ga_setup_input("Want to choose a custom install path?", "/etc/growautomation")
            if ga_config["setup_old_backup"] is True:
                ga_config["path_old_root"] = ga_setup_input("Please provide the install path of your current installation (for backup).", "/etc/growautomation")
            else:
                ga_config["path_old_root"] = False

        if ga_config["hostname"] is False:
            ga_setup_shelloutput_text("Growautomation hostname not found in old versionfile", style="warn")
            ga_config_var_base_name()

        if ga_config["setup_type"] is False:
            ga_setup_shelloutput_text("Growautomation setuptype not found in old versionfile.\n\n"
                                      "WARNING!\nTo keep your old configuration the setuptype must be the same as before", style="warn")
            ga_config["setup_type"] = ga_setup_input("Setup as growautomation standalone, agent or server?", "standalone", "agent/standalone/server")
            if ga_config["setup_old_backup"] is False:
                ga_setup_shelloutput_text("Turning on migration backup option - just in case", style="info")
                ga_config["setup_old_backup"] = True

    if ga_config["setup_fresh"] is True:
        ga_config["setup_type"] = ga_setup_input("Setup as growautomation standalone, agent or server?", "standalone", ["agent", "standalone", "server"])
        if ga_config["setup_type"] == "agent":
            ga_config["setup_yousure"] = ga_setup_input("WARNING!\nYou should install/update the growautomation server component before the agent because of dependencies.\n"
                                                        "Find more information about the creation of new agents at:\nhttps://git.growautomation.at/tree/master/manual/agent\n\n"
                                                        "Agree if you have already installed/updated the ga server or disagree to stop the installation.", False, style="warn")
            if ga_config["setup_yousure"] is False:
                ga_setup_exit("Stopping script. Server was not installed before agent", "User has not installed the server before the agent")
        ga_config["path_root"] = ga_setup_input("Want to choose a custom install path?", "/etc/growautomation")
        if ga_config["setup_old"] and ga_config["setup_old_backup"] is True:
            ga_config["path_old_root"] = ga_setup_input("Please provide the install path of your current installation (for backup).", "/etc/growautomation")
        else:
            ga_config["path_old_root"] = False
        ga_config_var_base_name()

    if ga_config["setup_type"] == "server" or ga_config["setup_type"] == "standalone":
        ga_config["setup_type_ss"] = True
    else:
        ga_config["setup_type_ss"] = False

    if ga_config["setup_type"] == "agent" or ga_config["setup_type"] == "standalone":
        ga_config["setup_type_as"] = True
    else:
        ga_config["setup_type_as"] = False


def ga_config_var_setup():
    global ga_config
    ga_setup_shelloutput_header("Checking setup options", "-")
    ga_config["setup_pwd_length"] = int(ga_setup_input("This setup will generate random passwords for you.\nPlease define the length of those random passwords!", "12", "8-99", "passgen"))

    ga_config["setup_ca"] = ga_setup_input("Need to import internal ca certificate for git/pip? Mainly needed if your firewall uses ssl inspection.", False)

    if ga_config["setup_ca"] is True:
        ga_config["setup_ca_path"] = ga_setup_input("Provide path to the ca file.", "/etc/ssl/certs/internalca.cer")
    else:
        ga_config["setup_ca_path"] = "notprovided"

    ga_config["setup_linuxupgrade"] = ga_setup_input("Want to upgrade your software and distribution before growautomation installation?", True)


def ga_config_var_db():
    global ga_config
    ga_setup_shelloutput_header("Checking for database credentials", "-")
    whilecount = 0
    if ga_config["setup_type"] == "agent":
        if ga_config["setup_fresh"] is True:
            ga_config["sql_agent_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
            while True:
                if whilecount > 0:
                    ga_setup_shelloutput_text("SQL connection failed. Please try again", style="warn")
                whilecount += 1
                ga_config["sql_server_ip"] = ga_setup_input("Provide the ip address of the growautomation server.", "192.168.0.201")
                ga_config["sql_server_port"] = ga_setup_input("Provide the mysql port of the growautomation server.", "3306")
                print("The following credentials can be found in the serverfile '$garoot/core/core.conf'\n")
                ga_config["sql_server_agent_usr"] = ga_setup_input("Please provide the user used to connect to the database.", ga_config["hostname"])
                ga_config["sql_server_agent_pwd"] = ga_setup_input("Please provide the password used to connect to the database.", ga_config["sql_agent_pwd"], intype="pass")
                if ga_mysql_conntest(ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"]) is True:
                    ga_setup_shelloutput_text("Server SQL connection verified", style="succ")
                    ga_config["sql_server_repl_usr"] = ga_setup_input("Please provide sql replication user.", ga_config["hostname"] + "replica")
                    ga_config["sql_server_repl_pwd"] = ga_setup_input("Please provide sql replication password.", ga_config["sql_server_agent_pwd"])
                    break
        else:
            ga_config["sql_agent_usr"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_local_user=")[10:]
            ga_config["sql_agent_pwd"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_local_pwd=")[14:]

            if ga_mysql_conntest(ga_config["sql_agent_usr"], ga_config["sql_agent_pwd"]) is True:
                ga_setup_shelloutput_text("Local SQL connection verified", style="succ")

            while True:
                if whilecount > 0:
                    ga_setup_shelloutput_text("You can reset/configure the agent database credentials on the "
                                              "growautomation server. Details can be found in the manual: "
                                              "https://git.growautomation.at/tree/master/manual", style="info")
                ga_config["sql_server_agent_usr"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_agent_user=")[10:]
                ga_config["sql_server_agent_pwd"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_agent_pwd=")[14:]
                ga_config["sql_server_ip"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_server_ip=")[9:]
                if ga_mysql_conntest(ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"]) is True:
                    break

            ga_setup_shelloutput_text("Server SQL connection verified", style="succ")
            # other config will be received via sql query
            return "default"

    else:
        ga_config["sql_server_ip"] = "127.0.0.1"
        ga_config["sql_server_port"] = "3306"
        if ga_config["setup_fresh"] is True:
            ga_config["sql_server_admin_usr"] = ga_setup_input("How should the growautomation database admin user be named?", "gadmin")
            ga_config["sql_server_admin_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
            if ga_mysql_conntest("root") is False:
                ga_setup_shelloutput_text("Unable to connect to local mysql server with root privileges", style="err")
            else:
                ga_setup_shelloutput_text("Server SQL connection verified", style="succ")
        else:
            ga_config["sql_server_admin_usr"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_admin_user=")[11:]
            ga_config["sql_server_admin_pwd"] = ga_setup_configparser_file("%s/core/core.conf" % ga_config["path_root"], "sql_admin_pwd=")[15:]
            while True:
                if whilecount > 0:
                    ga_setup_shelloutput_text("SQL connection failed. Please try again.\nThe following credentials can normally be found in the serverfile '$garoot/core/core.conf'", style="warn")
                if whilecount > 1:
                    ga_config["setup_server_admin_reset"] = ga_setup_input("Do you want to reset the database admin via the setup?", False)
                    if ga_config["setup_server_admin_reset"] is True:
                        if ga_mysql_conntest() is False:
                            ga_setup_shelloutput_text("Database admin can't be reset since the database check as root failed.\nThis could happen "
                                                      "if the growautomation database doesn't exist", style="warn")
                            ga_config["sql_server_noaccess_yousure"] = ga_setup_input("Do you want to continue the setup anyway? The problem might maybe get fixed by the setup process.", False)
                            if ga_config["sql_server_noaccess_yousure"] is False:
                                ga_setup_exit("All database connections failed", "User chose to exit since all database connections failed")
                            ga_config["setup_server_admin_reset"] = False
                            if ga_config["setup_old_backup"] is False:
                                ga_setup_shelloutput_text("Turning on migration backup option - just in case", style="info")
                                ga_config["setup_old_backup"] = True
                            return "none"
                        else:
                            ga_setup_shelloutput_text("SQL connection verified", style="succ")
                            return "root"

                    ga_config["sql_server_admin_usr"] = ga_setup_input("Provide the name of the growautomation database admin user.", "gadmin")
                    ga_config["sql_server_admin_pwd"] = ga_setup_input("Please provide the password used to connect to the database.", intype="pass")
                    if ga_mysql_conntest(ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"]) is True:
                        break
                    whilecount += 1

            ga_setup_shelloutput_text("SQL connection verified", style="succ")
            return "default"


def ga_config_var_certs():
    global ga_config
    ga_setup_shelloutput_header("Checking certificate information", "-")
    if ga_config["setup_type"] == "agent":
        ga_setup_shelloutput_text("The following certificates can be found in the serverpath '$garoot/ca/certs/'\n", style="info")
        ga_config["sql_ca"] = ga_setup_input("Provide the path to the ca-certificate from your ga-server.", "%s/ssl/ca.cer.pem" % ga_config["path_root"])
        ga_config["sql_cert"] = ga_setup_input("Provide the path to the agent server certificate.", "%s/ssl/%s.cer.pem" % (ga_config["path_root"], ga_config["hostname"]))
        ga_config["sql_key"] = ga_setup_input("Provide the path to the agent server key.", "%s/ssl/%s.key.pem" % (ga_config["path_root"], ga_config["hostname"]))


########################################################################################################################
# Basic config
ga_config_var_base()
ga_config_var_setup()
ga_config_var_db()


########################################################################################################################
# Config migration from old installation


if ga_config["setup_fresh"] is False:
    ga_setup_shelloutput_header("Retrieving existing configuration from database", "-")
    ga_config_list_agent = ["backup", "path_backup", "mnt_backup", "mnt_backup_type", "mnt_backup_server",
                            "mnt_backup_share", "mnt_backup_usr", "mnt_backup_pwd", "mnt_backup_dom", "path_log",
                            "mnt_log", "mnt_shared_creds", "mnt_shared_server", "mnt_shared_type", "mnt_log_type",
                            "mnt_log_server", "mnt_log_share", "mnt_log_usr", "mnt_log_pwd", "mnt_log_dom", "ga_ufw"]
    ga_config_list_server = []
    if ga_config["setup_type"] == "server":
        ga_configdict_sql = ga_setup_configparser_mysql("ga_config_list_server", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"])
    elif ga_config["setup_type"] == "standalone":
        ga_configdict_sql_agent = ga_setup_configparser_mysql("ga_config_list_agent", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"], ga_config["hostname"])
        ga_configdict_sql_server = ga_setup_configparser_mysql("ga_config_list_server", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"], ga_config["hostname"])
        ga_configdict_sql = {**ga_configdict_sql_agent, **ga_configdict_sql_server}
    else:
        ga_configdict_sql = ga_setup_configparser_mysql("ga_config_list_agent", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"], ga_config["hostname"])

    ga_config = {**ga_configdict_sql, **ga_config}

########################################################################################################################
# Configuration without migration
if ga_config["setup_fresh"] is True:
    ga_setup_shelloutput_header("Checking directory information", "-")

    ga_config["path_backup"] = ga_setup_input("Want to choose a custom backup path?", "/mnt/growautomation/backup/")
    ga_config["backup"] = ga_setup_input("Want to enable backup?", True)
    if ga_config["backup"] is True:
        ga_config["mnt_backup"] = ga_setup_input("Want to mount remote share as backup destination? Smb and nfs available.", True)
        if ga_config["mnt_backup"] is True:
            ga_setup_fstabcheck()
            ga_config["mnt_backup_type"] = ga_setup_input("Mount nfs or smb/cifs share as backup destination?", "nfs", "nfs/cifs")
            ga_config["mnt_backup_srv"] = ga_setup_input("Provide the server ip.", "192.168.0.201")
            ga_config["mnt_backup_share"] = ga_setup_input("Provide the share name.", "growautomation/backup")
            if ga_config["mnt_backup_type"] == "cifs":
                ga_mnt_backup_tmppwd = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
                ga_config["mnt_backup_usr"] = ga_mnt_creds("usr", "gabackup")
                ga_config["mnt_backup_pwd"] = ga_mnt_creds("pwd", ga_mnt_backup_tmppwd)
                ga_config["mnt_backup_dom"] = ga_mnt_creds("dom")
            # else:
            #     ga_setup_shelloutput_text("Not mounting remote share for backup!\nCause: No sharetype, "
            #                               "serverip or sharename provided.\n")
    else:
        ga_config["mnt_backup"] = False
        ga_config["mnt_backup_type"] = "False"
    
    ga_config["path_log"] = ga_setup_input("Want to choose a custom log path?", "/var/log/growautomation")
    ga_config["mnt_log"] = ga_setup_input("Want to mount remote share as log destination? Smb and nfs available.", False)
    if ga_config["mnt_log"] is True:
        ga_setup_fstabcheck()
        if ga_config["mnt_backup"] is True:
            ga_config["mnt_samecreds"] = ga_setup_input("Use same server as for remote backup?", True)
            if ga_config["mnt_samecreds"] is True:
                ga_config["mnt_log_type"] = ga_config["mnt_backup_type"]
                ga_config["mnt_log_server"] = ga_config["mnt_backup_srv"]
        else:
            ga_config["mnt_log_type"] = ga_setup_input("Mount nfs or smb/cifs share as log destination?", "nfs", "nfs/cifs")
            ga_config["mnt_log_server"] = ga_setup_input("Provide the server ip.", "192.168.0.201")
        ga_config["mnt_log_share"] = ga_setup_input("Provide the share name.", "growautomation/log")
    
        if ga_config["mnt_log_type"] == "cifs":

            def ga_mnt_log_creds():
                global ga_config
                ga_config["mnt_backup_usr"] = ga_mnt_creds("usr", "galog")
                ga_config["mnt_backup_pwd"] = ga_mnt_creds("pwd", ga_setup_pwd_gen(ga_config["setup_pwd_length"]))
                ga_config["mnt_backup_dom"] = ga_mnt_creds("dom")

            if ga_config["mnt_backup"] is True and ga_config["mnt_backup_type"] == "cifs" and \
                    ga_config["mnt_samecreds"] is True:
                ga_config["mnt_samecreds"] = ga_setup_input("Use same share credentials as for remote backup?", True)
                if ga_config["mnt_samecreds"] is True:
                    ga_config["mnt_log_usr"] = ga_config["mnt_backup_usr"]
                    ga_config["ga_mnt_log_pwd"] = ga_config["mnt_backup_pwd"]
                    ga_config["ga_mnt_log_dom"] = ga_config["mnt_backup_dom"]
                else:
                    ga_mnt_log_creds()
            else:
                ga_mnt_log_creds()
    else:
        ga_config["mnt_log_type"] = "False"  # for nfs/cifs apt installation

########################################################################################################################
# always vars
if ga_config["setup_type"] == "agent":
    ga_config_var_certs()

ga_ufw = ga_setup_input("Do you want to install the linux software firewall (ufw)?\n"
                        "It will be configured for growautomation", False)

########################################################################################################################

ga_setup_shelloutput_header("Logging setup information", "-")

ga_log_write_vars()

ga_setup_shelloutput_text("Thank you for providing the setup information.\nThe installation will start now")

########################################################################################################################


# functions
def ga_foldercreate(path):
    if os_path.exists(path) is False:
        os_system("mkdir -p %s && chown -R growautomation:growautomation %s %s" % (path, path, ga_config["setup_log_redirect"]))


def ga_setup_config_file(opentype, openinput, openfile=""):
    if openfile == "":
        file = "%s/core/core.conf" % ga_config["path_root"]
    else:
        file = openfile
    file_open = open(file, opentype)
    if opentype == "a" or opentype == "w":
        file_open.write(openinput)
        os_system("chown growautomation:growautomation %s && chmod 440 %s %s" % (file, file, ga_config["setup_log_redirect"]))
    elif opentype == "r":
        return file_open.readlines()
    file_open.close()
    

def ga_mounts(mname, muser, mpwd, mdom, msrv, mshr, mpath, mtype):
    ga_setup_shelloutput_header("Mounting %s share" % mname, "-")
    if mtype == "cifs":
        mcreds = "username=%s,password=%s,domain=%s" % (muser, mpwd, mdom)
    else:
        mcreds = "auto"
    ga_fstab = open("/etc/fstab", 'a')
    ga_fstab.write("#Growautomation %s mount\n//%s/%s %s %s %s 0 0\n\n" % (mname, msrv, mshr, mpath, mtype, mcreds))
    ga_fstab.close()
    os_system("mount -a %s" % ga_config["setup_log_redirect"])


def ga_replaceline(file, replace, insert):
    os_system("sed -i 's/%s/%s/p' %s %s" % (replace, insert, file, ga_config["setup_log_redirect"]))


def ga_openssl_setup():
    ga_foldercreate("%s/ca/private" % ga_config["path_root"])
    ga_foldercreate("%s/ca/certs" % ga_config["path_root"])
    ga_foldercreate("%s/ca/crl" % ga_config["path_root"])
    os_system("chmod 770 %s/ca/private %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))
    ga_replaceline("%s/ca/openssl.cnf", "= /root/ca", "= %s/ca") % (ga_config["path_root"], ga_config["path_root"])
    ga_setup_shelloutput_header("Creating root certificate", "-")
    os_system("openssl genrsa -aes256 -out %s/ca/private/ca.key.pem 4096 && chmod 400 %s/ca/private/ca.key.pe %s"
              % (ga_config["path_root"], ga_config["path_root"], ga_config["setup_log_redirect"]))
    os_system("openssl req -config %s/ca/openssl.cnf -key %s/ca/private/ca.key.pem -new -x509 -days 7300 -sha256 -extensions v3_ca -out %s/ca/certs/ca.cer.pem %s"
              % (ga_config["path_root"], ga_config["path_root"], ga_config["path_root"], ga_config["setup_log_redirect"]))


def ga_openssl_server_cert(certname):
    ga_setup_shelloutput_header("Generating server certificate", "-")
    os_system("openssl genrsa -aes256 -out %s/ca/private/%s.key.pem 2048 %s" % (ga_config["path_root"], certname, ga_config["setup_log_redirect"]))
    os_system("eq -config %s/ca/openssl.cnf -key %s/ca/private/%s.key.pem -new -sha256 -out %s/ca/csr/%s.csr.pem %s"
              % (ga_config["path_root"], ga_config["path_root"], certname, ga_config["path_root"], certname, ga_config["setup_log_redirect"]))
    os_system("openssl ca -config %s/ca/openssl.cnf -extensions server_cert -days 375 -notext -md sha256 -in %s/ca/csr/%s.csr.pem -out %s/ca/certs/%s.cert.pem %s"
              % (ga_config["path_root"], ga_config["path_root"], certname, ga_config["path_root"], certname, ga_config["setup_log_redirect"]))


def ga_sql_all():
    ga_setup_shelloutput_header("Starting sql setup", "#")
    ga_sql_backup_pwd = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
    ga_setup_shelloutput_header("Creating mysql backup user", "-")
    ga_mysql(["CREATE USER 'gabackup'@'localhost' IDENTIFIED BY '%s';" % ga_sql_backup_pwd, "GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, "
             "TRIGGER ON *.* TO 'gabackup'@'localhost' IDENTIFIED BY '%s';" % ga_sql_backup_pwd, "FLUSH PRIVILEGES;"])

    ga_setup_shelloutput_text("Set a secure password and answer all other questions with Y/yes", style="info")
    ga_setup_shelloutput_text("Example random password:", style="info", point=False)
    print(ga_setup_pwd_gen(ga_config["setup_pwd_length"]))
    ga_setup_shelloutput_text("\nMySql will not ask for the password if you start it locally (mysql -u root) with sudo/root privileges (set & forget)", style="info")
    os_system("mysql_secure_installation %s" % ga_config["setup_log_redirect"])

    ga_setup_config_file("a", "[mysqldump]\nuser=gabackup\npassword=%s\n" % ga_sql_backup_pwd, "/etc/mysql/conf.d/ga.mysqldump.cnf")

    os_system("usermod -a -G growautomation mysql %s" % ga_config["setup_log_redirect"])
    ga_foldercreate("/etc/mysql/ssl")


def ga_sql_server():
    ga_setup_shelloutput_header("Configuring sql as growautomation server", "#")
    os_system("mysql -u root < /tmp/controller/setup/server/ga_db_setup.sql %s" % ga_config["setup_log_redirect"])
    if ga_config["setup_type"] == "server":
        os_system("cp /tmp/controller/setup/server/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config["setup_log_redirect"])
    elif ga_config["setup_type"] == "standalone":
        os_system("cp /tmp/controller/setup/standalone/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config["setup_log_redirect"])

    ga_setup_shelloutput_header("Creating mysql admin user", "-")
    ga_mysql(["CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (ga_config["sql_server_admin_usr"], "%", ga_config["sql_server_admin_pwd"]),
              "GRANT ALL ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (ga_config["sql_server_admin_usr"], "%", ga_config["sql_server_admin_pwd"]), "FLUSH PRIVILEGES;"])

    ga_setup_config_file("a", "\n[db_growautomation]\nsql_admin_user=%s\nsql_admin_pwd=%s\n" % (ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"]))

    if ga_config["setup_type"] == "server":
        print("Creating mysql server certificate\n")
        ga_openssl_server_cert("mysql")
        os_system("ln -s %s/ca/certs/ca.cer.pem /etc/mysql/ssl/cacert.pem && ln -s %s/ca/certs/mysql.cer.pem /etc/mysql/ssl/server-cert.pem && "
                  "ln -s %s/ca/private/mysql.key.pem /etc/mysql/ssl/server-key.pem %s"
                  % (ga_config["path_root"], ga_config["path_root"], ga_config["path_root"], ga_config["setup_log_redirect"]))


def ga_sql_agent():
    ga_setup_shelloutput_header("Configuring sql as growautomation agent", "#")
    ga_config["sql_agent_pwd"] = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
    os_system("cp /tmp/controller/setup/agent/50-server.cnf /etc/mysql/mariadb.conf.d/ %s" % ga_config["setup_log_redirect"])
    ga_setup_shelloutput_header("Configuring mysql master-slave setup", "-")
    ga_setup_shelloutput_text("Replicating server db to agent for the first time", style="info")
    os_system("mysqldump -h %s --port %s -u %s -p %s ga > /tmp/ga.dbdump.sql && mysql -u root ga < /tmp/ga.dbdump.sql "
              "%s" % (ga_config["sql_server_ip"], ga_config["sql_server_port"], ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"], ga_config["setup_log_redirect"]))
    tmpsearchdepth = 500
    tmpfile = open("/tmp/ga.dbdump.sql", 'r')
    tmplines = tmpfile.readlines()[:tmpsearchdepth]
    for line in tmplines:
        if line.find("Master_Log_File: ") != -1:
            ga_config["sql_server_repl_file"] = line.split("Master_Log_File: ")[1].split("\n", 1)[0]
        elif line.find("Master_Log_Pos: ") != -1:
            ga_config["sql_server_repl_pos"] = line.split("Master_Log_Pos: ")[1].split("\n", 1)[0]

    ga_sql_server_agent_id = int(ga_mysql("SELECT id FROM ga.ServerConfigAgents WHERE controller = %s;"
                                          % ga_config["hostname"], ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"], True) + 100)
    ga_replaceline("/etc/mysql/mariadb.conf.d/50-server.cnf", "server-id              = 1", "server-id = %s" % ga_sql_server_agent_id)
    os_system("systemctl restart mysql %s" % ga_config["setup_log_redirect"])

    ga_setup_shelloutput_header("Creating local mysql controller user (read only)", "-")
    ga_mysql(["CREATE USER 'gacon'@'localhost' IDENTIFIED BY '%s';" % ga_config["sql_agent_pwd"],
              "GRANT SELECT ON ga.* TO 'gacon'@'localhost' IDENTIFIED BY '%s';" % ga_config["sql_agent_pwd"], "FLUSH PRIVILEGES;"])

    ga_setup_config_file("a", "[db_local]\nsql_local_user=gacon\nsql_local_pwd=%s\n[server]\nsql_agent_user=%s\nsql_agent_pwd=%s\nsql_server_ip=%s\nsql_server_port=%s"
                         % (ga_config["sql_agent_pwd"], ga_config["sql_server_agent_usr"], ga_config["sql_server_agent_pwd"], ga_config["sql_server_ip"], ga_config["sql_server_port"]))
    
    if ga_setup_keycheck(ga_config["sql_server_repl_file"]) is False or ga_setup_keycheck(ga_config["sql_server_repl_pos"]) is False:
        ga_setup_shelloutput_text("SQL master slave configuration not possible due to missing information.\nShould be found in mysql dump from server "
                                  "(searching in first %s lines).\nNot found: 'Master_Log_File:'/'Master_Log_Pos:'" % tmpsearchdepth, style="warn")
    else:
        ga_mysql(["CHANGE MASTER TO MASTER_HOST='%s', MASTER_USER='%s', MASTER_PASSWORD='%s', MASTER_LOG_FILE='%s', MASTER_LOG_POS=%s;"
                  % (ga_config["sql_server_ip"], ga_config["sql_server_repl_usr"], ga_config["sql_server_repl_pwd"], ga_config["sql_server_repl_file"],
                     ga_config["sql_server_repl_pos"]), " START SLAVE;", " SHOW SLAVE STATUS;"])
        # \G

    ga_setup_shelloutput_header("Linking mysql certificate", "-")
    os_system("ln -s %s /etc/mysql/ssl/cacert.pem && ln -s %s /etc/mysql/ssl/server-cert.pem && ln -s %s /etc/mysql/ssl/server-key.pem %s"
              % (ga_config["sql_ca"], ga_config["sql_cert"], ga_config["sql_key"], ga_config["setup_log_redirect"]))


def ga_sql_server_create_agent():
    ga_setup_shelloutput_header("Registering a new growautomation agent to the server", "#")
    create_agent = ga_setup_input("Do you want to register an agent to the ga-server?", True)
    if create_agent is True:
        server_agent_list = ga_mysql("SELECT controller FROM ga.ServerConfigAgents WHERE enabled = 1;", ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"], True)
        if len(server_agent_list) > 0:
            ga_setup_shelloutput_text("List of registered agents:\n%s\n" % server_agent_list, style="info")
        else:
            ga_setup_shelloutput_text("No agents are registered/enabled yet.\n", style="info")

        create_agent_namelen = 0
        while create_agent_namelen > 10:
            if create_agent_namelen > 10:
                ga_setup_shelloutput_text("Agent could not be created due to a too long name.\nMax 10 characters supported.\nProvided: %s" % create_agent_namelen, style="warn")
            create_agent_name = ga_setup_input("Provide agent name.", "gacon01", poss="max. 10 characters long")
            if create_agent_name in server_agent_list:
                ga_setup_shelloutput_text("Controllername already registered to server. Choose a diffent name", style="warn")
                create_agent_name = "-----------"
            create_agent_namelen = len(create_agent_name)

        create_agent_pwdlen = 0
        while create_agent_pwdlen > 99 or create_agent_pwdlen < 8:
            if create_agent_pwdlen > 99 or create_agent_pwdlen < 8:
                ga_setup_shelloutput_text("Input error. Value should be between 8 and 99", style="warn")
            create_agent_pwd = ga_setup_input("Provide agent password.", ga_setup_pwd_gen(ga_config["setup_pwd_length"]), poss="between 8 and 99 characters")
            create_agent_pwdlen = len(create_agent_pwd)

        ga_setup_shelloutput_header("Creating mysql controller user", "-")
        create_agent_desclen = 0
        while create_agent_desclen > 50:
            if create_agent_desclen > 50:
                ga_setup_shelloutput_text("Description longer than 50 characters. Try again.", style="warn")
            create_agent_desc = ga_setup_input("Do you want to add a description to the agent?", poss="String up to 50 characters")
            create_agent_desclen = len(create_agent_desc)

        ga_mysql(["CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (create_agent_name, "%", create_agent_pwd),
                  "GRANT CREATE, DELETE, INSERT, SELECT, UPDATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (create_agent_name, "%", create_agent_pwd),
                  "FLUSH PRIVILEGES;", "INSERT INTO ga.ServerConfigAgents (author, controller, description) VALUES (%s, %s, %s);"
                  % ("gasetup", create_agent_name, create_agent_desc)], ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"])

        create_replica_usr = create_agent_name + "replica"
        create_replica_pwd = ga_setup_pwd_gen(ga_config["setup_pwd_length"])
        ga_mysql(["CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (create_replica_usr, "%", create_replica_pwd),
                  "GRANT REPLICATE ON ga.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (create_replica_usr, "%", create_replica_pwd),
                  "FLUSH PRIVILEGES;"], ga_config["sql_server_admin_usr"], ga_config["sql_server_admin_pwd"])

        ga_setup_config_file("a", "[db_agent_%s]\nsql_server_ip=%s\nsql_server_port=%s\nsql_agent_user=%s\nsql_agent_pwd=%s\nsql_replica_user=%s\nsql_replica_pwd=%s"
                             % (create_agent_name, ga_config["sql_server_ip"], ga_config["sql_server_port"], create_agent_name, create_agent_pwd, create_replica_usr, create_replica_pwd))

        ga_setup_shelloutput_header("Creating mysql agent certificate\n", "-")
        ga_openssl_server_cert(create_agent_name)


def ga_ufw_setup():
    ga_setup_shelloutput_header("Configuring firewall", "-")
    os_system("ufw default deny outgoing && ufw default deny incoming && ufw allow out to any port 80 proto tcp && ufw allow out to any port 443 proto tcp && "
              "ufw allow out to any port 22 proto tcp && ufw allow out to any port 53 proto udp && ufw allow out to any port 53 proto tcp && ufw allow out to any port 123 proto udp && "
              "ufw allow proto tcp from 192.168.0.0/16 to any port 22 && ufw allow proto tcp from 172.16.0.0/12 to any port 22 && ufw allow proto tcp from 10.0.0.0/10 to any port 22 %s"
              % ga_config["setup_log_redirect"])
    if ga_config["setup_type"] == "server" or ga_config["setup_type"] == "agent":
        os_system("ufw allow 3306/tcp from 192.168.0.0/16 && ufw allow 3306/tcp from 172.16.0.0/12 && ufw allow 3306/tcp from 10.0.0.0/10 %s" % ga_config["setup_log_redirect"])
    ga_ufw_enable = ga_setup_input("Firewall rules were configured. Do you want to enable them?\nSSH and MySql connections from public ip ranges will be denied!", True)
    if ga_ufw_enable is True:
        os_system("ufw enable %s" % ga_config["setup_log_redirect"])


########################################################################################################################


# install packages
def ga_setup_apt():
    ga_setup_shelloutput_header("Installing software packages", "#")
    os_system("apt-get update" + ga_config["setup_log_redirect"])
    if ga_config["setup_linuxupgrade"] is True:
        os_system("apt-get -y dist-upgrade && apt-get -y upgrade %s && apt -y autoremove" % ga_config["setup_log_redirect"])

    os_system("apt-get -y install python3 mariadb-server mariadb-client git %s" % ga_config["setup_log_redirect"])

    if ga_config["setup_type_as"] is True:
        os_system("apt-get -y install python3 python3-pip python3-dev python-smbus git %s" % ga_config["setup_log_redirect"])
    else:
        os_system("apt-get -y install openssl %s" % ga_config["setup_log_redirect"])

    if (ga_config["mnt_backup"] or ga_config["mnt_log"]) is True:
        if ga_config["mnt_backup_type"] == "nfs" or ga_config["mnt_log_type"] == "nfs":
            os_system("apt-get -y install nfs-common %s" % ga_config["setup_log_redirect"])
        elif ga_config["mnt_backup_type"] == "cifs" or ga_config["mnt_log_type"] == "cifs":
            os_system("apt-get -y install cifs-utils %s" % ga_config["setup_log_redirect"])

    if ga_ufw is True:
        os_system("apt-get -y install ufw %s" % ga_config["setup_log_redirect"])


def ga_setup_pip():
    if ga_config["setup_ca"] is True:
        os_system("git core --global http.sslCAInfo %s && python3 -m pip core set global.cert %s %s" % (ga_config["setup_ca_path"], ga_config["setup_ca_path"], ga_config["setup_log_redirect"]))
    ga_setup_shelloutput_header("Installing python packages", "-")
    os_system("python3 -m pip install mysql-connector-python RPi.GPIO Adafruit_DHT adafruit-ads1x15 selenium pyvirtualdisplay --default-timeout=100 %s" % ga_config["setup_log_redirect"])


ga_setup_apt()
if ga_config["setup_type_as"] is True:
    ga_setup_pip()


# folders
# Create folders
def ga_infra_oldversion_rootcheck():
    if ga_config["path_old_root"] is False:
        return ga_config["path_root"]
    else:
        return ga_config["path_old_root"]


def ga_infra_oldversion_cleanconfig():
    movedir = "/tmp/ga_setup_%s" % (datetime.now().strftime("%Y-%m-%d_%H-%M"))
    os_system("mkdir -p %s" % movedir)
    os_system("mv %s %s %s" % (ga_infra_oldversion_rootcheck(), movedir, ga_config["setup_log_redirect"]))
    os_system("mysqldump ga > /tmp/ga.dbdump_%s.sql %s" % (datetime.now().strftime("%Y-%m-%d_%H-%M"), ga_config["setup_log_redirect"]))
    if ga_mysql_conntest("root", special=True) is True:
        ga_mysql("DROP DATABASE ga;")


def ga_infra_oldversion_backup():
    global ga_config
    ga_setup_shelloutput_header("Backing up old growautomation root directory and database", "-")
    oldbackup = ga_config["path_backup"] + "install_%s" % datetime.now().strftime("%Y-%m-%d_%H-%M")
    os_system("mkdir -p %s && cp -r %s %s %s" % (oldbackup, ga_infra_oldversion_rootcheck(), oldbackup, ga_config["setup_log_redirect"]))
    os_system("mv %s %s %s" % (ga_config["setup_version_file"], oldbackup, ga_config["setup_log_redirect"]))
    os_system("mysqldump ga > %s/ga.dbdump.sql %s" % (oldbackup, ga_config["setup_log_redirect"]))
    ga_setup_shelloutput_text("Backupfolder: %s\n%s\nRoot backupfolder:\n%s" % (oldbackup, os_listdir(oldbackup), os_listdir(oldbackup + "/growautomation")), style="info")
    if os_path.exists(oldbackup + "/ga.dbdump.sql") is False or \
            os_path.exists(oldbackup + "/growautomation/") is False:
        ga_setup_shelloutput_text("Success of backup couldn't be verified. Please check it yourself to be sure that it was successfully created. (Strg+Z "
                                  "to get to Shell -> 'fg' to get back)\nBackuppath: %s" % oldbackup, style="warn")
        ga_config["setup_old_backup_failed_yousure"] = ga_setup_input("Please verify that you want to continue the setup", False)
    else:
        ga_config["setup_old_backup_failed_yousure"] = True
    ga_infra_oldversion_cleanconfig()


def ga_setup_infra_mounts():
    if ga_config["mnt_backup"] is True or ga_config["mnt_log"] is True:
        ga_setup_shelloutput_header("Mounting shares", "#")
        if ga_config["mnt_backup"] is True:
            ga_mounts("backup", ga_config["mnt_backup_usr"], ga_config["mnt_backup_pwd"], ga_config["mnt_backup_dom"], ga_config["mnt_backup_srv"],
                      ga_config["mnt_backup_share"], ga_config["path_backup"], ga_config["mnt_backup_type"])
        if ga_config["mnt_log"] is True:
            ga_mounts("log", ga_config["mnt_log_usr"], ga_config["ga_mnt_log_pwd"], ga_config["ga_mnt_log_dom"], ga_config["mnt_log_server"], ga_config["mnt_log_share"],
                      ga_config["path_log"], ga_config["mnt_log_type"])


def ga_setup_infra():
    ga_setup_shelloutput_header("Setting up directories", "#")
    os_system("useradd growautomation %s" % ga_config["setup_log_redirect"])

    ga_foldercreate(ga_config["path_backup"])

    if ga_config["setup_old"] is True and ga_config["setup_old_backup"] is True:
        ga_infra_oldversion_backup()
    elif ga_config["setup_old"] is True:
        ga_infra_oldversion_cleanconfig()

    ga_setup_config_file("w", "version=%s\npath_root=%s\nhostname=%s\nsetuptype=%s\n"
                         % (ga_config["version"], ga_config["path_root"], ga_config["hostname"], ga_config["setup_type"]), ga_config["setup_version_file"])
    os_system("chmod 664 %s && chown growautomation:growautomation %s %s" % (ga_config["setup_version_file"], ga_config["setup_version_file"], ga_config["setup_log_redirect"]))
    ga_foldercreate(ga_config["path_root"])
    ga_foldercreate(ga_config["path_log"])
    ga_setup_infra_mounts()


# code setup
def ga_setup_infra_code():
    ga_setup_shelloutput_header("Setting up growautomation code", "#")
    if os_path.exists("/tmp/controller") is True:
        os_system("mv /tmp/controller /tmp/controller_%s %s" % (datetime.now().strftime("%Y-%m-%d_%H-%M"), ga_config["setup_log_redirect"]))

    os_system("cd /tmp && git clone https://github.com/growautomation-at/controller.git %s" % ga_config["setup_log_redirect"])

    if ga_config["setup_type_as"] is True:
        os_system("cp -r /tmp/controller/code/agent/* %s %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

    if ga_config["setup_type_ss"] is True:
        os_system("cp -r /tmp/controller/code/server/* %s %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

    os_system("cp /tmp/controller/setup/setup-linux.py %s/core %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

    os_system("find %s -type f -iname '*.py' -exec chmod 754 {} \\; %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))
    os_system("chown -R growautomation:growautomation %s %s" % (ga_config["path_root"], ga_config["setup_log_redirect"]))

    ga_pyvers = "%s.%s" % (sys_version_info.major, sys_version_info.minor)
    ga_pyvers_modpath = "/usr/local/lib/python%s/dist-packages/ga" % ga_pyvers
    if os_path.exists(ga_pyvers_modpath) is False:
        os_system("ln -s %s %s %s" % (ga_config["path_root"], ga_pyvers_modpath, ga_config["setup_log_redirect"]))

    os_system("ln -s %s %s/backup && ln -s %s %s/log %s" % (ga_config["path_backup"], ga_config["path_root"], ga_config["path_log"], ga_config["path_root"], ga_config["setup_log_redirect"]))

    ga_setup_config_file("w", "[core]\nhostname=%s\nsetuptype=%s" % (ga_config["hostname"], ga_config["setup_type"]))


# creating systemd service and timers
class ga_setup_service(object):
    def __init__(self):
        self.element = None
        self.path = None
        self.start()

    def check(self, request="exists", out=""):
        if request == "exists":
            command = "systemctl list-unit-files | grep %s" % self.element
        elif request == "enabled":
            command = "systemctl list-unit-files | grep %s | grep enabled" % self.element
        elif request == "status" and self.element.find(".service") != -1:
            command = "systemctl status %s | grep 'Active:'" % self.element
        else:
            return "Input error."

        output, error = subprocess_popen([command], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe).communicate()
        outputstr = output.decode("ascii")
        errorstr = error.decode("ascii")

        if request == "exists":
            if outputstr.find(self.element) == -1:
                return False
            elif out == "":
                return True
            elif out == "info":
                return outputstr
            elif out == "err":
                return errorstr
        elif request == "status":
            if outputstr.find("Active:") == -1:
                return False
            elif outputstr.find("active (running)") != -1:
                return True
            else:
                return False

    def enabled(self, check=True):
        if check is True:
            enabled = self.check("enabled")
        else:
            enabled = False

        if enabled is True:
            ga_setup_shelloutput_text("%s is already enabled" % self.element, style="succ")
        else:
            os_system("systemctl enable %s %s" % (self.element, ga_config["setup_log_redirect"]))
            ga_setup_shelloutput_text("Enabled %s" % self.element, style="info")

    def exists(self, check=True):
        if check is True:
            exists = self.check()
        else:
            exists = False
        if exists is True:
            ga_setup_shelloutput_text("%s already exists" % self.element, style="succ")
            self.enabled()
        else:
            os_system("systemctl link %s %s" % (self.path, ga_config["setup_log_redirect"]))
            ga_setup_shelloutput_text("Linked %s" % self.element, style="info")
            self.enabled()

    def start(self):
        service_dir = "%s/service/systemd/" % ga_config["path_root"]

        if os_path.exists(service_dir) is False:
            ga_setup_infra_code()

        for file in os_listdir(service_dir):
            filepath = service_dir + file
            if os_path.isfile(filepath):
                if (file.find(".service") != -1 or file.find(".timer") != -1) and file.find("DEFAULT") == -1:
                    self.element = file
                    self.path = filepath
                    self.exists()
        os_system("systemctl daemon-reload %s" % ga_config["setup_log_redirect"])
        ga_setup_shelloutput_text("Systemd services reloaded", style="info")

    # in work
    # def ga_setup_infra_timer_add(systemd_element=""):
    #     ga_timer_path = "%s/service/systemd" % ga_config["path_root"]
    #     if systemd_element == "":
    #         ga_config["setup_systemd_add_timer"] = ga_setup_input("Do you want to add a sensor/an action timer?", True)
    #     elif ga_config["setup_systemd_add_timer"] is True or systemd_element != "":
    #         while True:
    #             if systemd_element != "":
    #                 devicetype = systemd_element
    #             else:
    #                 while True:
    #                     devicetype = ga_setup_input("Please provide the name of the device ")
    #                     if ga_setup_string_check(devicetype) is True:
    #                         break
    #                 # systemd interval -> sql config either from DeviceSettings or DeviceTypeSettings (prio = DeviceSettings)
    #                 ga_setup_configparser_mysql(devicetype, ga_config["setup_sql_usr"], ga_config["setup_sql_pwd"], table="devicetype")
    #             os_system("cp %s/ga@DEFAULT.timer %s/ga@%s.timer %s" % (ga_timer_path, ga_timer_path, devicetype, ga_config["setup_log_redirect"]))
    #             ga_replaceline("%s/ga@%s.timer" % (ga_timer_path, devicetype), "Unit=", "Unit=ga@%s.service" % devicetype)
    #             ga_setup_infra_service_exists(devicetype, ga_timer_path + "/ga@%s.timer" % devicetype, check=False)
    #             ga_setup_infra_service_enabled(devicetype, check=False)
    #
    #             if systemd_element == "":
    #                 again = ga_setup_input("Do you want to add another timer?", True)
    #                 if again is False:
    #                     break
    #             else:
    #                 break

# check path inputs for ending / and remove it
# delete old fstab entries and replace them (ask user)
# systemd systemd setup for agentdata and serverbackup
# ga service check for python path /usr/bin/python3 and growautomation root -> change execstart execstop etc
# ga_config["backup"] should do something.. but what?
# simple setup -> preconfigure most settings
# advanced setup -> like now
# dont repeat output if wrong input -> only warning
# oldconf
#    db functions for oldconfig checken -> less to do?
#    should certs be renewed?
#    tell user that type cant be changed without replace option (done already?)
#    adv setup value overwrite x5 or so (manually)
# ufw error ERROR: Couldn't determine iptables version
# keepconfig -> doesnt get setup_type / doesnt start basic vars function
# mysql bug workaround MySql was unable to perform action 'CREATE USER
# check all string inputs with ga_setup_string_check (reference in input function if poss/default is str?)
# replaceline error if not found ?
# configure first sensors / actions -> with systemd timers


ga_setup_infra()
ga_setup_infra_code()

# creating openssl ca
if ga_config["setup_type"] == "server":
    ga_openssl_setup()

# db setup
ga_sql_all()

if ga_config["setup_type_ss"] is True:
    ga_sql_server()

if ga_config["setup_type"] == "server":
    ga_sql_server_create_agent()

elif ga_config["setup_type"] == "agent":
    ga_sql_agent()

if ga_config["setup_type_ss"] is True:
    ga_config["setup_sql_usr"] = ga_config["sql_server_admin_usr"]
    ga_config["setup_sql_pwd"] = ga_config["sql_server_admin_pwd"]
else:
    ga_config["setup_sql_usr"] = ga_config["sql_server_agent_usr"]
    ga_config["setup_sql_pwd"] = ga_config["sql_server_agent_pwd"]

if ga_ufw is True:
    ga_ufw_setup()


########################################################################################################################
# post setup tasks

# defining default values
ga_config["backup_time"] = "2000"
ga_config["backup_log"] = False
ga_config["log_level"] = 2


def ga_mysql_write_config(thatdict, thattype="agent"):
    insertdict = {}
    for key, value in thatdict.items():
        if "setup_" in key or "sql_server_agent_pwd" in key or "sql_agent_pwd" in key or "sql_agent_usr" in key or "sql_server_admin_pwd" in key:
            pass
        else:
            insertdict[key] = value

    for key, value in sorted(insertdict.items()):
        if thattype == "agent":
            command = "INSERT INTO ga.AgentConfig (author, agent, setting, data) VALUES ('%s', '%s', '%s', '%s');" % ("gasetup", ga_config["hostname"], key, value)
        else:
            command = "INSERT INTO ga.ServerConfig (author, setting, data) VALUES ('%s', '%s', '%s');" % ("gasetup", key, value)
        ga_mysql(command, ga_config["setup_sql_usr"], ga_config["setup_sql_pwd"])
    ga_setup_shelloutput_text("Wrote %s configuration to database. (%s settings)" % (thattype, len(insertdict)), style="succ", point=False)


ga_setup_shelloutput_header("Writing configuration to database", "#")
ga_log_write_vars()
ga_mysql_write_config(ga_config_server, "server")
ga_mysql_write_config(ga_config)

ga_setup_shelloutput_header("Setup finished! Please reboot the system", "#")
ga_setup_log_write("Setup finished.")
