import http.server
import socketserver
import os
from jinja2 import Template

# Define the port to run the server on
PORT = 8080


# Create a custom handler to handle file uploads and downloads
class FileSharingHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Handle file uploads
        if self.path == '/upload':
            file_data = self.rfile.read(int(self.headers.get('Content-Length')))
            with open("uploads/" + self.headers.get('file'), 'wb') as file:
                file.write(file_data)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        # Serve the HTML template
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # List files in the 'uploads' directory
            files = os.listdir("uploads")

            # Render the HTML template with the file list
            with open("htmlfile.html", 'r') as template_file:
                template = Template(template_file.read())
                rendered_template = template.render(files=files)
                self.wfile.write(rendered_template.encode())
        # Serve uploaded files for download
        elif self.path.startswith('/download/'):
            file_path = "uploads/" + self.path[len('/download/'):]

            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', 'attachment; filename=' + os.path.basename(file_path))
                self.end_headers()

                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


# Create a directory for uploads if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Start the web server
with socketserver.TCPServer(("", PORT), FileSharingHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
