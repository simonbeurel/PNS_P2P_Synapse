import uuid
from random import random
from typing import List, Set, Dict, Optional

from attr import dataclass


@dataclass
class Message:
    code: str  # OPE, FIND, FOUND
    ttl: int # Time To Live
    mrr: int  # Maximum Replication Rate
    tag: str # Identifie le message
    key: str
    value: Optional[str]
    ip_dest: str
    ip_send: str # IP du noeud émetteur

class SynapseNode:
    def __init__(self, ip: str):
        self.ip = ip
        self.net_list: List[str] = []
        self.processed_tags: Set[str] = set()
        self.routing_table: Dict[str, Dict] = {}

    def new_tag(self, ip_sender: str) -> str:
        return str(uuid.uuid4())

    def game_over(self, tag: str) -> bool:
        return tag in self.processed_tags

    # push_tag ajoute un tag à la liste des tags qui ont été traités
    def push_tag(self, tag: str):
        self.processed_tags.add(tag)

    # Divise le MRR entre les noeuds du réseau
    def distrib_mrr(self, mrr: int, net_list: List[str]) -> Dict[str, int]:
        if not net_list:
            return {}
        by_net = max(1, mrr // len(net_list))
        return {ip: by_net for ip in net_list}


    def is_responsible(self, net: str, key: str) -> bool:
        return key in self.routing_table.get(net, {})

    def good_deal(self, network: str, ip_send: str) -> bool:
        # strategie pour savoir si on accepte un noeud ou non
        return True

    def next_hop(self, key: str) -> str:
        return f"node_{random.randint(1, 100)}"

    # Comportement du noeud lorsqu'il reçoit un message OPE
    def handle_operation(self, msg: Message):
        tag = self.new_tag(msg.ip_send)
        print(f"Received OPE message: {msg}")
        self.handle_find(Message(
            code=msg.code,
            ttl=10,  # une valeur par défaut au lieu de 0
            mrr=msg.mrr,
            tag=tag,
            key=msg.key,
            value=msg.value,
            ip_dest=msg.ip_dest,
            ip_send=self.ip
        ))

    def good_deal_update(self, ip_send: str):
        # cette fonction sert a mettre a jour la table des bon deal
        # elle depend de la strategie en place, ici j'ai toujours accepter les noeuds donc on peut l'ignorer
        pass

    # Comportement du noeud lorsqu'il reçoit un message FIND
    def handle_find(self, msg: Message):
        if msg.ttl == 0 or self.game_over(msg.tag):
            return

        self.push_tag(msg.tag)
        next_mrr = self.distrib_mrr(msg.mrr, self.net_list)
        print(f"Received FIND message: {msg}")
        for net in self.net_list:
            if self.is_responsible(net, msg.key):
                self.handle_found(Message(
                    code=msg.code,
                    ttl=msg.ttl,
                    mrr=msg.mrr,
                    tag=msg.tag,
                    key=msg.key,
                    value=self.routing_table[net].get(msg.key),
                    ip_dest=msg.ip_dest,
                    ip_send=self.ip
                ))
            elif self.good_deal(net, msg.ip_send):
                next_node = self.next_hop(msg.key)
                new_msg = Message(
                    code=msg.code,
                    ttl=msg.ttl - 1,
                    mrr=next_mrr[net],
                    tag=msg.tag,
                    key=msg.key,
                    value=msg.value,
                    ip_dest=msg.ip_dest,
                    ip_send=self.ip
                )
                # Forward to next_node (simplified)
                print(f"Forwarding to {next_node}: {new_msg}")

    # Comportement du noeud lorsqu'il reçoit un message FOUND
    def handle_found(self, msg: Message):
        self.good_deal_update(msg.ip_send)
        print(f"Received FOUND message: {msg}")
        match msg.code:
            case "GET":
                value = self.routing_table.get(msg.ip_send, {}).get(msg.key)
                print(f"Retrieved value: {value}")
            case "PUT" if msg.mrr >= 0:
                if msg.ip_send not in self.routing_table:
                    self.routing_table[msg.ip_send] = {}
                self.routing_table[msg.ip_send][msg.key] = msg.value

    # Comportement du noeud lorsqu'il reçoit un message INVITE
    def handle_invite(self, network: str, ip_send: str):
        print(f"Received INVITE message: {network} from {ip_send}")
        if self.good_deal(network, ip_send):
            self.handle_join(network, ip_send)

    # Comportement du noeud lorsqu'il reçoit un message JOIN
    def handle_join(self, network: str, ip_send: str):
        print(f"Received JOIN message: {network} from {ip_send}")
        if self.good_deal(network, ip_send):
            self.net_list.append(network)



# Setting up test environment for each message type in the protocol
# Setting up two nodes
node_A = SynapseNode("192.168.1.1")
node_B = SynapseNode("192.168.1.2")


# Test 1: Testing OPE (operation) message handling
print("Testing handle_operation with OPE message")
ope_message = Message(code="OPE", ttl=10, mrr=5, tag="", key="test_key", value="test_value", ip_dest="192.168.1.2", ip_send="192.168.1.1")
node_A.handle_operation(ope_message)



# Test 2: Testing FIND message handling (forwarding and responsibility)
print("\nTesting handle_find with FIND message")
find_message = Message(code="FIND", ttl=3, mrr=5, tag=node_A.new_tag("192.168.1.1"), key="test_key", value="test_value", ip_dest="192.168.1.2", ip_send="192.168.1.1")
node_A.handle_find(find_message)

# Test 3 : Testing FOUND with a PUT
print("\nTesting PUT + handle_found with FOUND message")
found_message = Message(code="PUT", ttl=3, mrr=5, tag=node_A.new_tag("192.168.1.1"), key="test_key", value="Hello World!", ip_dest="192.168.1.1", ip_send="192.168.1.2")
node_A.handle_found(found_message)

# Test 3: Testing FOUND message handling (retrieving or storing values)
print("\nTesting handle_found with FOUND message")
found_message = Message(code="GET", ttl=3, mrr=5, tag=node_A.new_tag("192.168.1.1"), key="test_key", value="Hello World!", ip_dest="192.168.1.1", ip_send="192.168.1.2")
node_A.handle_found(found_message)

# Test 4: Testing INVITE and JOIN message handling
print("\nTesting handle_invite and handle_join with INVITE and JOIN messages")
node_A.handle_invite("network_1", "192.168.1.2")



# Checking resulting network list in node A to ensure join was successful

print(f"\nNode A's network list after JOIN: {node_A.net_list}")