username=$username
apikey=$apikey
concat_string=$username
concat_string+=":"
concat_string+=$apikey
echo $concat_string|base64