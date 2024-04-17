#!/bin/bash -e

if [[ $# -lt 1 ]]; then
    echo "Usage: bash run_openldap.sh <host-ip-or-hostname>"
    echo ""
    echo "       host-ip-or-hostname      VM IP or hostname where you are running this script"
    echo ""
    echo "       e.g., bash run_openldap.sh 9.30.253.13"
    echo ""
    exit 1
fi

HOST_IP=$1

echo ""
echo "Cleanup existing services..."
docker rm -f icp-phpldapadmin-service || true
docker rm -f icp-openldap-service || true
echo "DONE!"

echo ""
echo "Start openldap services..."
docker run --env LDAP_ORGANISATION="IBM" --env LDAP_DOMAIN="ibm.com" \
   --env LDAP_ADMIN_PASSWORD="Passw0rdAssetLdap \
   --publish 389:389 --publish 636:636 \
   --name icp-openldap-service --detach osixia/openldap:1.1.8

docker run --env PHPLDAPADMIN_LDAP_HOSTS=$HOST_IP --publish 6443:443 \
   --name icp-phpldapadmin-service --detach osixia/phpldapadmin:0.7.0

sleep 2
echo "DONE!"

echo ""
echo "Test LDAP conenction..."
#sudo apt-get install ldap-utils
ldapsearch -x -H ldap://$HOST_IP:389 -b dc=ibm,dc=com -D cn=admin,dc=ibm,dc=com -w Passw0rd#3@i%b^m$
echo ""
echo "DONE!"

echo ""
echo ""
echo "Go to: https://$HOST_IP:6443"
echo "Login DN: cn=admin,dc=ibm,dc=com"
echo "Password: Passw0rdAssetLdap"