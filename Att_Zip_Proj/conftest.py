import pytest
from sshcheckers import ssh_checkout
import random, string
import yaml
from datetime import datetime


with open('config.yaml') as f:
   data = yaml.safe_load(f)

@pytest.fixture()
def start_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@pytest.fixture()
def make_folders():
   return ssh_checkout(data["ip"], data["user"], data["passwd"], "mkdir {} {} {} {}".format(data["folder_in"], data["folder_out"], data["folder_ext"], data["folder_ext2"]), "")


@pytest.fixture()
def clear_folders():
   return ssh_checkout(data["ip"], data["user"], data["passwd"], "rm -rf {}/* {}/* {}/* {}/*".format(data["folder_in"], data["folder_out"], data["folder_ext"], data["folder_ext2"]), "")


@pytest.fixture()
def make_files():
   list_of_files = []
   for i in range(data["count"]):
       filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
       if ssh_checkout(data["ip"], data["user"], data["passwd"], "cd {}; dd if=/dev/urandom of={} bs=1M count=1 iflag=fullblock".format(data["folder_in"], filename), ""):
           list_of_files.append(filename)
   return list_of_files


@pytest.fixture()
def make_subfolder():
   testfilename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
   subfoldername = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
   if not ssh_checkout(data["ip"], data["user"], data["passwd"], "cd {}; mkdir {}".format(data["folder_in"], subfoldername), ""):
       return None, None
   if not ssh_checkout(data["ip"], data["user"], data["passwd"], "cd {}/{}; dd if=/dev/urandom of={} bs=1M "
                            "count=1 iflag=fullblock".format(data["folder_in"], subfoldername, testfilename), ""):
       return subfoldername, None
   else:
       return subfoldername, testfilename


@pytest.fixture()
def make_bad_arx():
   ssh_checkout(data["ip"], data["user"], data["passwd"], "cd {}; 7z a {}/arxbad -t{}".format(data["folder_in"],
                                                                               data["folder_out"], data["type"]), "Everything is Ok")
   ssh_checkout(data["ip"], data["user"], data["passwd"], "truncate -s 1 {}/arxbad.{}".format(data["folder_out"],
                                                                               data["type"]), "Everything is Ok")
   yield "arxbad"
   ssh_checkout(data["ip"], data["user"], data["passwd"], "rm -f {}/arxbad.{}".format(data["folder_out"], data["type"]), "")


@pytest.fixture(autouse=True)
def print_time():
   print("Start: {}".format(datetime.now().strftime("%H:%M:%S.%f")))
   yield print("Stop: {}".format(datetime.now().strftime("%H:%M:%S.%f")))


@pytest.fixture()
def log_stat(make_files):
    count_of_files = len(make_files)
    size_of_files = data["bs"]
    stat_file_path = 'stat.txt'
    yield

    with open('/proc/loadavg', 'r') as loadavg_file:
        loadavg_stats = loadavg_file.read().strip()
    current_time = datetime.now().strftime("%H-%M-%S-%f")
    log_entry = f'{current_time=}, {count_of_files=}, {size_of_files=}, {loadavg_stats=}\n'

    with open(stat_file_path, 'a') as stat_file:
        stat_file.write(log_entry)


