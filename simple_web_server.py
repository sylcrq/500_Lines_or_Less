import http.server
import os
import subprocess

# custom exception need defined first
class ServerException(Exception):
    pass

# 1st case: file not exist
class case_no_file(object):
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException('no file error')

# 2nd case: show file content
class case_is_file(object):
    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)

# 3rd case: list dir files
class case_is_dir(object):
    def test(self, handler):
        return os.path.isdir(handler.full_path)

    def act(self, handler):
        handler.handle_list_dir(handler.full_path)

# 4th case: exec cgi file
class case_is_cgi_file(object):
    def test(self, handler):
        return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')

    def act(self, handler):
        # exec in another process
        with subprocess.Popen(['python3', handler.full_path], stdout=subprocess.PIPE) as proc:
            out = proc.stdout.read().decode('utf-8')
            handler.send_page(out)

# last case: always fail
class case_always_fail(object):
    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException('always fail')

class MyRequestHandler(http.server.BaseHTTPRequestHandler):
    #类属性
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

    List_Page = '''
    <html>
    <body>
    <ul>
    {0}
    </ul>
    </body>
    </html>
    '''

    Cases = [
        case_no_file(),
        case_is_cgi_file(),
        case_is_file(),
        case_is_dir(),
        case_always_fail()
    ]

    #full_path = ''

    def do_GET(self):
        #print(self.Page)
        #page = self.create_page()
        #self.send_page(page)
        try:
            self.full_path = os.getcwd() + self.path
            '''
            if not os.path.exists(path):
                #self.handle_error("{0} not found".format(self.path))
                raise ServerException("{0} not found".format(self.path))
            elif os.path.isfile(path):
                self.handle_file(path)
            else:
                #self.handle_error("Unknown object {0}".format(self.path))
                raise ServerException("Unknown object {0}".format(self.path))
            '''
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break
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

    # send file content page
    def handle_file(self, path):
        try:
            with open(path, 'r') as reader:
                # can be optimize here
                content = reader.read()
            self.send_page(content)
        except IOError as msg:
            self.handle_error("{0} can not be read {1}".format(self.path, msg))

    # send list dir file page
    def handle_list_dir(self, path):
        entries = os.listdir(path)
        tmp = ['<li>{0}</li>'.format(e) for e in entries]
        self.send_page(self.List_Page.format("\n".join(tmp)))

    # send error page
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

