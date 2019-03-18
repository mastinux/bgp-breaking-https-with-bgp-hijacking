import SimpleHTTPServer
import SocketServer
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--text', default="Default web server")
parser.add_argument('--hostname', default="localhost")
FLAGS = parser.parse_args()

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


print "starting webserver on %s serving", (FLAGS.hostname, FLAGS.text)

PORT = 80
httpd = SocketServer.TCPServer(("", PORT), Handler)
httpd.serve_forever()
