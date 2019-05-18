# bgp-breaking-https-with-bgp-hijacking

## Installazione VM

Scaricare la VM Mininet [http://www.scs.stanford.edu/~jvimal/mininet-sigcomm14/mininet-tutorial-vm-64bit.zip](http://www.scs.stanford.edu/~jvimal/mininet-sigcomm14/mininet-tutorial-vm-64bit.zip).  
Per accedere:

- username: mininet
- password: mininet

## Preparazione mininet

- `$ git clone https://github.com/mininet/mininet`

- `$ cd mininet`

- `$ git checkout 2.3.0d4`

- `$ ./util/install.sh -a`

- `$ mn --test pingall`

- `$ mn --version`

## Quagga preparation

Scaricare quagga-1.2.4 from [http://download.savannah.gnu.org/releases/quagga/](http://download.savannah.gnu.org/releases/quagga/) nella tua `$HOME` ed estrai il package

- `$ cd ~/quagga-1.2.4`

- `# chown mininet:mininet /var/run/quagga`

- modifica il file `configure`, aggiungendo `${quagga_statedir_prefix}/var/run/quagga` prima di tutte le opzioni del loop su `QUAGGA_STATE_DIR` 

- `$ ./configure --enable-user=mininet --enable-group=mininet`

- `$ make`

---

## Descrizione dell'attacco

![topology](./images/bgp-breaking-https-with-bgp-hijacking.png)

Prima dell'attacco gli AS1, AS2, AS3 e AS4 sono attivi.  
Il server vittima (V) è nell'AS3.  
Il client (C) e la Certification Authority (CA) sono nell'AS4.  
Il router R5 che gestisce l'AS5 non è attivo e sarà sotto il controllo dell'attaccante.  
Il server sotto il controllo dell'attaccante (A) è nell'AS5.

![topology](./images/bgp-breaking-https-with-bgp-hijacking-0.png)

Il client C raggiunge il server vittima V. Il traffico attraversa gli AS AS4, AS1, AS2, AS3.

![topology](./images/bgp-breaking-https-with-bgp-hijacking-1.png)

L'attaccante attiva l'hijacking dirottando il traffico destinato alla rete 13.0.0.0/8 verso l'AS5.  

![topology](./images/bgp-breaking-https-with-bgp-hijacking-2.png)

La CA chiede di pubblicare un contenuto sull'host indicato nel campo Common Name della richiesta.  
La CA verifica la proprietà dell'host accedendo a tale contenuto.  
La CA viene dirottata verso il server A sotto il controllo dell'attaccante.  
La CA emette il certificato per il server A.

![topology](./images/bgp-breaking-https-with-bgp-hijacking-3.png)

Il client C accede al server A sotto il controllo dell'attaccante verificando correttamente il certificato. Il traffico attraversa gli AS AS4, AS1, AS5.

## Esecuzione dell'attacco

**1. installa openssl**

`apt install openssl`

**2. pulisci la $HOME da .rnd**

`rm ~/.rnd`

**3. crea una CA** in `./CA`

> https://workaround.org/certificate-authority/

in `./CA` lanciare

`/usr/lib/ssl/misc/CA.pl -newca`

	PEM pass phrase: password

	Country Name (2 letter code) [AU]:IT  
	State or Province Name (full name) [Some-State]:Lazio   
	Locality Name (eg, city) []:Roma  
	Organization Name (eg, company) [Internet Widgits Pty Ltd]:RootCA  
	Organizational Unit Name (eg, section) []:IT  
	Common Name (e.g. server FQDN or YOUR name) []:rootca.it  
	Email Address []:admin@rootca.it

	A challenge password []:password  
	An optional company name []:RootCA  
	Enter pass phrase for ./demoCA/private/cakey.pem: password

`./CA/demoCA/cacert.pem` certificato pubblico della CA

**4. crea la richiesta del server alla CA** in `./server`

`/usr/lib/ssl/misc/CA.pl -newreq`

	PEM pass phrase: server

	Country Name (2 letter code) [AU]:IT  
	State or Province Name (full name) [Some-State]:Lazio  
	Locality Name (eg, city) []:Roma  
	Organization Name (eg, company) [Internet Widgits Pty Ltd]:MainServer  
	Organizational Unit Name (eg, section) []:IT  
	Common Name (e.g. server FQDN or YOUR name) []:13.0.1.1  
	Email Address []:admin@mainserver.it

	A challenge password []:server  
	An optional company name []:MainServer

`./server/newkey.pem` chiave privata  
`./server/newreq.pem` richiesta

**5. firma la richiesta e crea il certificato per il server**

copia `./server/newreq.pem` in `./CA`

in `./CA` firma la richiesta

`/usr/lib/ssl/misc/CA.pl -sign`

Enter pass phrase for ./demoCA/private/cakey.pem:password  
Sign the certificate? [y/n]:y  
1 out of 1 certificate requests certified, commit? [y/n]y

copia il certificato `./CA/newcert.pem` in `./server`

**6. prepara il certificato per server**

> https://stackoverflow.com/a/20908026

in `./server`

`openssl rsa -in newkey.pem -out newkey_unencrypted.pem`

**7. accedi al server verificando il certificato**

`./client-curls-server-https.sh`

**8. crea la richiesta del malicious-server alla CA** in `./malicious-server`

`/usr/lib/ssl/misc/CA.pl -newreq`

	Enter PEM pass phrase:malicious

	Country Name (2 letter code) [AU]:IT  
	State or Province Name (full name) [Some-State]:Lazio  
	Locality Name (eg, city) []:Roma  
	Organization Name (eg, company) [Internet Widgits Pty Ltd]:MainServer  
	Organizational Unit Name (eg, section) []:IT  
	Common Name (e.g. server FQDN or YOUR name) []:13.0.1.1  
	Email Address []:admin@13.0.1.1  

	A challenge password []:malicious  
	An optional company name []:MainServer

**9. lancia l'hijacking**

`./start-malicious-AS.sh`

**10. avvia il malicious-server**

`./start-malicious-server.sh`

**11. verifica che la CA raggiunga il malicious-server**

`./CA-curls-server.sh`

**12. firma la richiesta e crea il certificato per il malicious-server**

copia `./malicious-server/newreq.pem` in `./CA`

in `./CA/demoCA/index.txt.attr` imposta il flag `unique_subject` a `no`

NB. di default la CA non può firmare un secondo certificato con lo stesso Common Name di un certificato già firmato  
il flag modificato rimuove questo vincolo

in `./CA` firma la richiesta

`/usr/lib/ssl/misc/CA.pl -sign`

copia il certificato `./CA/newcert.pem` in `./malicious-server`

**13. prepara il certificato per malicious-server**

in `./malicious-server`

`openssl rsa -in newkey.pem -out newkey_unencrypted.pem`

**14. avvia il malicious-server col certificato ottenuto**

`./start-malicious-server-https.sh`

**15. accedi al malicious-server verificando il certificato**

controlla l'output di `./client-curls-server-https.sh`

**16. ferma la simulazione**

`mininet> exit`
