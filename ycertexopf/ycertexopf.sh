#!/bin/bash -e
sudo dpkg-reconfigure slapd

cat << EOF >> /etc/ldap/ldap.conf 
BASE dc=example,dc=com
URI ldap://ldap01.example.com
EOF

cat << EOF > ldap.diff
> dn: ou=People,dc=example,dc=com
> objectClass: organizationalUnit
> ou: People
> 
> dn: ou=Groups,dc=example,dc=com
> objectClass: organizationalUnit
> ou: Groups
> 
> dn: cn=DEPARTMENT,ou=Groups,dc=example,dc=com
> objectClass: posixGroup
> cn: SUBGROUP
> gidNumber: 5000
> 
> dn: uid=USER,ou=People,dc=example,dc=com
> objectClass: inetOrgPerson
> objectClass: posixAccount
> objectClass: shadowAccount
> uid: USER
> sn: LASTNAME
> givenName: FIRSTNAME
> cn: FULLNAME
> displayName: DISPLAYNAME
> uidNumber: 10000
> gidNumber: 5000
> userPassword: USER
> gecos: FULLNAME
> loginShell: /bin/bash
> homeDirectory: USERDIRECTORY
> EOF

cat /etc/ldap/ldap.conf

ldapsearch -x -LLL -H ldap:/// -b dc=example,dc=com dn
