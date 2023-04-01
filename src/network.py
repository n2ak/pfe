
class Network:
    def __init__(
        self,
        on_client_connect=lambda: print("Client Connected"),
    ) -> None:
        self.on_client_connect = on_client_connect
        pass
