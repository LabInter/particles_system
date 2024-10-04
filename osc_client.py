from pythonosc import udp_client

class OscClient:

    def __init__(self, ip = "10.197.94.14", port = 7400):
        self.ip = ip
        self.port = port
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
        self.error_already_printed = False
        print(f"connection... ip: {self.ip}, port: {self.port}")

    def send_message(self, atr, message):
        try:
            self.client.send_message(atr, message)
        except Exception as e:
            if not self.error_already_printed:
                print(f"Failed to send message: {e}")
                self.error_already_printed = True
