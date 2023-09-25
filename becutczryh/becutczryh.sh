db2 force application all

for dbName in OPX
do
db2 deactivate db ${dbName}
done

db2stop force

ipclean -a
cd /mnt/blumeta0/db2/ssl_keystore
source /db2u/scripts/include/db2_ssl_functions.sh && rotate_ssl_certs
db2start

for dbName in OPX
do
db2 activate db ${dbName}
done