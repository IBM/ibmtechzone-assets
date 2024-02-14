username=$username
apikey=$apikey
concat_string=$username
concat_string+=":"
concat_string+=$apikey
echo $concat_string
TOKEN=$(echo $concat_string|base64)
echo $TOKEN
echo "[CP4D]">>cp4d_info.conf
echo "TOKEN=${TOKEN}">>cp4d_info.conf
cat cp4d_info.conf