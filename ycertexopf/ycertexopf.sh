#!/bin/bash -e
sudo dpkg-reconfigure slapd
cat /etc/ldap/ldap.conf