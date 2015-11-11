from geventwebsocket.handler import WebSocketHandler


class DjangoWebSocketHandler(WebSocketHandler):

    def run_websocket(self):
        """
        Just run the websocket request on the application. Dont use client
        tracking because we are using unix domain sockets and the client addr
        is the same for every socket.
        """
        try:
            self.application(self.environ, lambda s, h, e=None: [])
        finally:
            # not sure all this tidy up is necessary
            self.environ.update({'wsgi.websocket': None})
            if not self.websocket.closed:
                self.websocket.close()
            self.websocket = None

    @property
    def active_client(self):
        """
        Since we are tracking clients return None here.
        """
        return
