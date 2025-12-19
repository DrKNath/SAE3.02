import random
from crypto import crypto

class OnionRouter:
    def __init__(self, core):
        self.core = core
        self.crypto = crypto()

    def gen_route(self, nb_hop: int = 3):
        with self.__lock:
            routers = list(self.__list_router)

        if not routers:
            print("[ERREUR] Aucun router disponible.")
            return []

        nb_hop = min(nb_hop, len(routers))
        return random.sample(routers, nb_hop)
    
    def build_onion(self, message: str, route, destination_ip, destination_port):
        layer = f"{destination_ip}::{destination_port}::{message}"
        
        for router in reversed(route):
            pubkey = router["public_key"]
            encrypted_layer = self.__crypto.encrypt(layer, pubkey)
            
            # Si ce n'est PAS le premier routeur
            if router != route[0]:
                ip = router["ip"]
                port = router["port"]
                layer = f"{ip}::{port}::{encrypted_layer}"
            else:
                # Pour le premier, pas d'enrobage
                layer = encrypted_layer
        
        return layer
