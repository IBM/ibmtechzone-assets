#!/usr/bin/bash

# Log in to OCP cluster

# Get WKC Db2u pod
opxdb2pod="c-db2oltp-1677417105436063-db2u-0"
echo "OpenPages Db2u Pod:" $opxdb2pod

# copy script to pod
oc cp /home/ibmuser/scripts/refresh_openpages_db2_certs.sh $opxdb2pod:/tmp/

# Execute script in pod
oc exec $opxdb2pod -c db2u -- /bin/bash -l /tmp/refresh_openpages_db2_certs.sh

# Delete OpenPages DB2u pod
oc delete pod $opxdb2pod