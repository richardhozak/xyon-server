from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import json
import sys
import socketserver
import pafy


class AudioTcpHandler(socketserver.StreamRequestHandler):

    def handle(self):
        try:
            print("Client", self.client_address[0], "connected")
            while True:
                print("Waiting for request...")
                data = self.rfile.readline().strip().decode('utf-8')
                print(data)
                # print(self.client_address[0], "sent", data)
                d = json.loads(data)
                print(d['method'], d['params'])
                search_response = self.server.youtube.dict[d['method']](d['params'])
                method_response = {"method": "response_" + d['method'], "params": search_response}
                json_response = json.dumps(method_response).encode('utf-8')
                print(json_response)
                self.wfile.write(json_response)
        except:
            print("Client", self.client_address[0], "disconnected")
            return


class LinkHost:

    def __init__(self):
        self.dict = {}
        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and not name.startswith("__") and not name.endswith("__"):
                self.dict[name] = attr
            # if not name.startswith("__") and not name.endswith("__"):

    def search(self, query):
        def create_query_object(result):
            href = result['href']
            is_list = 'list' in href
            return {'type': 'list' if is_list else 'video',
                    'id': href[26:] if is_list else href[9:],
                    'title': result['title']}

        query_string = urllib.parse.urlencode({"search_query": query})
        html_content = urllib.request.urlopen(
            "http://www.youtube.com/results?" + query_string)
        soup = BeautifulSoup(html_content.read().decode())
        search_results = soup.find_all("a", {"class": "yt-uix-tile-link"})
        return list(map(create_query_object, search_results))

    def get_stream_link(self, vid):
        print("Getting audio stream link", vid)
        video = pafy.new(vid)
        audio = video.getbestaudio(preftype="ogg")
        print(audio.url_https)
        print(audio.extension)
        return audio.url


if __name__ == "__main__":
    host, port = "localhost", 2323
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((host, port), AudioTcpHandler)
    server.youtube = LinkHost()
    # server.youtube = LinkHost()
    print("Starting server...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)

