# bgp-breaking-https-with-bgp-hijacking

Descrizione dell'attacco disponibile qui: https://www.blackhat.com/docs/us-15/materials/us-15-Gavrichenkov-Breaking-HTTPS-With-BGP-Hijacking.pdf

---

SERVER HTTPS CON PYTHON https://gist.github.com/dergachev/7028596

CREARE UNA CA https://workaround.org/certificate-authority/

CERTIFICATO PER APACHE SERVER https://www.linux.com/learn/creating-self-signed-ssl-certificates-apache-linux

VERIFICARE CERTIFICATO DA COMMAND LINE https://www.cyberciti.biz/faq/test-ssl-certificates-diagnosis-ssl-certificate/

---

## Preparazione Mininet

- `git clone https://github.com/mininet/mininet`

- `cd mininet`

- `git checkout 2.3.0d4`

- `util/install.sh -a`

- `mn --test pingall`

- `mn --version`

## Preparazione Quagga

- esegui il download quagga-1.2.4 da [qui](http://download.savannah.gnu.org/releases/quagga/) nella tua `$HOME` ed estrai il file compresso

- `cd ~/quagga-1.2.4`

- `chown mininet:mininet /var/run/quagga`

- modifica il file `configure`, aggiungendo `${quagga_statedir_prefix}/var/run/quagga` prima di tutte le opzioni nel loop `for` per `QUAGGA_STATE_DIR`

- `./configure --enable-user=mininet --enable-group=mininet`

- `make`

---

## Descrizione dell'attacco

\# TODO

## Esecuzione dell'attacco

\# TODO

<!--

Per provare la simulazione, seguiamo i seguenti passi.

**1. Avviamo l'ambiente di simulazione.**

Avviamo le istanze dei router, degli AS e degli host eseguendo il comando.

`$ python bgp.py`

L'output sarà simile al seguente.

```
*** Creating network
*** Adding controller
*** Adding hosts:
h1-1 h1-2 h1-3 h2-1 h2-2 h2-3 h3-1 h3-2 h3-3 h4-1 h4-2 h4-3 
*** Adding switches:
R1 R2 R3 R4 
*** Adding links:
(R1, R2) (R1, R4) (R1, h1-1) (R1, h1-2) (R1, h1-3) (R2, R3) (R2, h2-1) (R2, h2-2) (R2, h2-3) (R3, h3-1) (R3, h3-2) (R3, h3-3) (R4, h4-1) (R4, h4-2) (R4, h4-3) 
*** Configuring hosts
h1-1 h1-2 h1-3 h2-1 h2-2 h2-3 h3-1 h3-2 h3-3 h4-1 h4-2 h4-3 
*** Starting controller
*** Starting 4 switches
R1 R2 R3 R4 
Waiting 3 seconds for sysctl changes to take effect...
Starting zebra and bgpd on R1
Starting zebra and bgpd on R2
Starting zebra and bgpd on R3
Starting web servers
*** Starting CLI:
mininet> 
```

**2. Accediamo al deamon di routing.**

In un altro terminale avviamo una sessione con il deamon di routing dell'AS1. La password per accedere come utente è `en`. 

`$ ./connect.sh`

L'output sarà simile al seguente.

```
Connecting to R1 shell
Trying ::1...
Connected to localhost.
Escape character is '^]'.

Hello, this is Quagga (version 0.99.22.4).
Copyright 1996-2005 Kunihiro Ishiguro, et al.


User Access Verification

Password: 
```

Per accedere alla shell di amministratore lanciamo il comando `en`; la password di accesso è `en`.

```
bgpd-R1> en
Password: 
bgpd-R1# 
```

**3. Controlliamo la routing table.**

Verifichiamo le entry di routing nell'AS1. Lanciamo il comando:

`bgpd-R1# sh ip bgp`

L'output sarà simile al seguente.

```
BGP table version is 0, local router ID is 9.0.0.1
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
              r RIB-failure, S Stale, R Removed
Origin codes: i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
*> 11.0.0.0         0.0.0.0                  0         32768 i
*> 12.0.0.0         9.0.0.2                  0             0 2 i
*> 13.0.0.0         9.0.0.2                                0 2 3 i

Total number of prefixes 3
```

Vediamo che l'AS1 raggiunge la rete 13.0.0.0/8 tramite il path "2 3", cioè attraversando AS2 e poi AS3.

**4. Visitiamo il web server.**

In un'altra finestra, visitiamo il server che mininet ha avviato nell'AS3 e verifichiamo che lo si possa raggiungere dall'host h1-1 connesso all'AS1. In questa fase lo script esegue il comando `curl -s 13.0.0.1` dall'host h1-1 in un ciclo. Lanciamo lo script.

`$ ./website.sh`

L'output sarà simile al seguente.

```
Fri May 18 02:30:35 PDT 2018 -- <h1>Default web server</h1>
Fri May 18 02:30:36 PDT 2018 -- <h1>Default web server</h1>
Fri May 18 02:30:37 PDT 2018 -- <h1>Default web server</h1>
...
```

**5. Lanciamo l'attacco.**

In un'altra finestra, avviamo l'AS attaccante. Esso si connetterà all'AS1 e diffonderà una rotta per 13.0.0.0/8 usando un path più corto. Quindi, l'AS1 sceglierà questo path. Lanciamo lo script:

`$ ./start_rogue.sh`

L'output sarà simile al seguente.

```
Killing any existing rogue AS
Starting rogue AS
```

Dopo un po' di tempo, a causa della convergenza del BGP, dovremmo vedere che l'output dello script `website.sh` cambia in questo modo.

```
...
Fri May 18 02:36:45 PDT 2018 -- <h1>Default web server</h1>
Fri May 18 02:36:46 PDT 2018 -- <h1>Default web server</h1>
Fri May 18 02:36:47 PDT 2018 -- <h1>Default web server</h1>
Fri May 18 02:36:48 PDT 2018 -- <h1>*** Attacker web server ***</h1>
Fri May 18 02:36:49 PDT 2018 -- <h1>*** Attacker web server ***</h1>
Fri May 18 02:36:50 PDT 2018 -- <h1>*** Attacker web server ***</h1>
...
```

Possiamo ricontrollare la tabella di routing usando la shell dell'AS1.

```
BGP table version is 0, local router ID is 9.0.0.1
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
              r RIB-failure, S Stale, R Removed
Origin codes: i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
*> 11.0.0.0         0.0.0.0                  0         32768 i
*> 12.0.0.0         9.0.0.2                  0             0 2 i
*> 13.0.0.0         9.0.4.2                  0             0 4 i
*                   9.0.0.2                                0 2 3 i

Total number of prefixes 3
```

Vediamo che il path scelto per raggiungere 13.0.0.0/8 passa per AS4.

**6. Fermiamo l'ambiente di simulazione.**

Fermiamo l'attacco lanciando lo script.

`$ ./stop_rogue.sh`

Fermiamo lo script che richiede la pagina web con Control-C.

Fermiamo il terminale connesso a R1.

`bgpd-R1# exit`

Fermiamo le istanze digitando exit nel terminale di mininet.

`mininet> exit`

-->
