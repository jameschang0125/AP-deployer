#!/usr/bin/env python3

import pexpect
import json
# import hmac

class ApInit:
    def __init__(self):
        # Loads configuration file.

        with open('env.json', 'r') as f:
            self.data = json.load(f)

        self.ap_target  = self.data["AP_IP"]
        self.ZD_IP      = self.data["ZONEDIRECTOR_IP"]
        self.gateway    = self.data["AP_GATEWAY_IP"]
        self.vlan       = int(self.data["AP_MGNT_VLAN"])
        self.username   = self.data["AP_USERNAME"]
        self.passwd     = self.data["AP_PASSWORD"]
        self.lock_secret = self.data["LOCK_SECRET"]
        self.lock_digits = int(self.data["LOCK_DIGITS"])
        self.name       = self.data["NAME"]
        self.ID         = self.data["ID"]
        self.IP         = self.data["ASSIGN_IP"]
        print("init done")

    def success(self):
        print("AP target:", self.ap_target)
        print("Zone director:", self.ZD_IP)
        print("Vlan:", self.vlan)
        print("Assigned device name:", self.name)
        print("Assigned IP:", self.IP)
        # print("Lock password", self.GenPassword())

    def run(self):
        with pexpect.spawn(
            f"ssh -o StrictHostKeyChecking=no {self.ap_target}"
        ) as ssh:
            # Real login here.
            ssh.expect([ "login" ])
            ssh.sendline(self.username)
            ssh.expect([ "password" ])
            ssh.sendline(self.passwd)

            # Sets up interface.
            ssh.expect([ "rkscli:" ])
            ssh.sendline("set interface eth0 type vlan-trunk untag 1")
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set interface eth1 type vlan-trunk untag 1")
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline(
                f"set ipaddr wan vlan {self.vlan} {self.IP} 255.255.248.0 {self.gateway}"
            )
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set ipmode wan ipv4")
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline(f"set director ip {self.ZD_IP}")
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline(f"set device-name {self.name}")
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline("reboot")
            ssh.expect([ "OK" ])

            print('The AP has been rebooted')

            pexpect.spawn(f"ssh-keygen -R {self.ap_target}").close()
        self.success()

    # def GenPassword(self):
    #     assert self.lock_digits <= 154
    #     password = ('%0155d' % (int(hmac.new(
    #         key=self.lock_secret.encode('utf-8'),
    #         msg=self.ID.encode('utf-8'),
    #         digestmod='sha512'
    #     ).hexdigest(), 16)))[-self.lock_digits:]
    #     return password

if __name__ == '__main__':
    initer = ApInit()
    initer.run()

