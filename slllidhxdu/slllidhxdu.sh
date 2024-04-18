#!/bin/bash -e
sudo dpkg-reconfigure slapd
cat /etc/ldap/ldap.conf
BASE dc=example,dc=com
URI ldap://ldap01.example.com