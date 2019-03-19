import BaseHTTPServer, SimpleHTTPServer
import ssl
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--text', default="Default web server")
parser.add_argument('--address', default="127.0.0.1")
parser.add_argument('--keyfile', default="./server/newkey_unencrypted.pem")
parser.add_argument('--certfile', default="./server/newcert.pem")
FLAGS = parser.parse_args()

# https://blog.anvileight.com/posts/simple-python-http-server/#python-2-x-1


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    # Disable logging DNS lookups
    def address_string(self):
        return str(self.client_address[0])

    def do_GET(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write("<h1>%s</h1>\n" % FLAGS.text)
		self.wfile.flush()


print "starting HTTPS webserver on %s serving %s" % (FLAGS.address, FLAGS.text)

httpd = BaseHTTPServer.HTTPServer((FLAGS.address, 443), Handler)

httpd.socket = ssl.wrap_socket (httpd.socket, \
		keyfile=FLAGS.keyfile, \
		certfile=FLAGS.certfile, \
		server_side=True)

httpd.serve_forever()
