username=$username
apikey=$apikey
concat_string=$username
concat_string+=":"
concat_string+=$apikey
TOKEN=$concat_string|base64
echo "[CP4D]">>cp4d_info.conf
echo "TOKEN=$TOKEN">>cp4d_info.conf
cat cp4d_info.conf