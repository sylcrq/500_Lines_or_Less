import http.server
import os

class MyRequestHandler(http.server.BaseHTTPRequestHandler):
    Page = '''
    <html>
    <body>
    <table>
    <tr>  <td>Header</td>         <td>Value</td>          </tr>
    <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
    <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
    <tr>  <td>Client port</td>    <td>{client_port}s</td> </tr>
    <tr>  <td>Command</td>        <td>{command}</td>      </tr>
    <tr>  <td>Path</td>           <td>{path}</td>         </tr>
    </table>
    </body>
    </html>
    '''

    Error_Page = '''
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    '''

    def do_GET(self):
        #print(self.Page)
        #page = self.create_page()
        #self.send_page(page)
        try:
            path = os.getcwd() + self.path

            if not os.path.exists(path):
                #self.handle_error("{0} not found".format(self.path))
                raise ServerException("{0} not found".format(self.path))
            elif os.path.isfile(path):
                self.handle_file(path)
            else:
                #self.handle_error("Unknown object {0}".format(self.path))
                raise ServerException("Unknown object {0}".format(self.path))
        except Exception as msg:
            self.handle_error(msg)

    def create_page(self):
        values = {
            'date_time' : self.date_time_string(),
            'client_host' : self.client_address[0],
            'client_port' : self.client_address[1],
            'command' : self.command,
            'path' : self.path
        }
        page = self.Page.format(**values)
        return page

    def send_page(self, page):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(bytes(page, "utf-8"))

    def handle_file(self, path):
        try:
            with open(path, 'r') as reader:
                # can be optimize here
                content = reader.read()
            self.send_page(content)
        except IOError as msg:
            self.handle_error("{0} can not be read {1}".format(self.path, msg))

    def handle_error(self, msg):
        values = {
            'path' : self.path,
            'msg' : msg
        }
        page = self.Error_Page.format(**values)
        self.send_page(page)

if __name__ == '__main__':
    server_address = ('', 8080) # tuple
    http_server = http.server.HTTPServer(server_address, MyRequestHandler)
    http_server.serve_forever()

