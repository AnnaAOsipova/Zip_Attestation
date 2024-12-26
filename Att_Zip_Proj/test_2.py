from sshcheckers import ssh_checkout_negative, ssh_checkout, upload_files
import yaml

with open('config.yaml') as f:
    # читаем документ yaml
    data = yaml.safe_load(f)


class TestNeg:

    def test_install(self, start_time, log_stat):
        res = []
        upload_files(data["ip"], data["user"], data["passwd"], data["pkgname"] + ".deb",
                     "/home/{}/{}.deb".format(data["user"], data["pkgname"]))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"],
                                "echo '{}' | sudo -S dpkg -i /home/{}/{}.deb".format(data["passwd"], data["user"],
                                                                                     data["pkgname"]),
                                "Setting up p7zip"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"],
                                "echo '{}' | sudo -S dpkg -s {}".format(data["passwd"], data["pkgname"]),
                                "Status: install ok installed"))
        assert all(res), "test FAIL"


    def test_nstep1(self, make_bad_arx, log_stat):
        assert ssh_checkout_negative(data["ip"], data["user"], data["passwd"],
                                 "cd {}; 7z e {}.{} -o{} -y".format(data["folder_out"],
                                                                    make_bad_arx, data["type"], data["folder_ext"]),
                                 "ERROR:"), "test1 FAIL"


    def test_nstep2(self, make_bad_arx, log_stat):
        assert ssh_checkout_negative(data["ip"], data["user"], data["passwd"],
                                 "cd {}; 7z t {}.{}".format(data["folder_out"],
                                                            make_bad_arx, data["type"]), "ERROR:"), "test2 FAIL"


    def test_nstep3(self, log_stat):
        res = []
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], "echo '{}' | sudo -S dpkg -r"
                                                                          " {}".format(data["passwd"], data["pkgname"]),
                                "remove"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], "echo '{}' | "
                                                                          "sudo -S dpkg -s {}".format(data["passwd"],
                                                                                                      data["pkgname"]),
                                "Status: deinstall ok"))
        assert all(res), "test3 FAIL"
