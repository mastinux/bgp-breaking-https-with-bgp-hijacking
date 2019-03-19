
sudo python run.py --node h5-1 --cmd "sudo python webserver-https.py --text \"Malicious HTTPS web server\" --address 13.0.1.1 --certfile ./malicious-server/newcert.pem --keyfile ./malicious-server/newkey_unencrypted.pem"

