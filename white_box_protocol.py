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

    def push_tag(self, tag: str):
        self.processed_tags.add(tag)

    def manage_mrr(self, mrr: int, net_list: List[str]) -> Dict[str, int]:
        if not net_list:
            return {}
        by_net = max(1, mrr // len(net_list))
        return {ip: by_net for ip in net_list}

    def is_reachable(self, net: str, key: str) -> bool:
        return key in self.routing_table.get(net, {})

    def good_deal(self, network: str, ip_send: str) -> bool:
        return True

    def next_hop(self, key: str) -> str:
        return f"node_{random.randint(1, 100)}"

    def handle_operation(self, msg: Message):
        tag = self.new_tag(msg.ip_send)
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

    def handle_find(self, msg: Message):
        if msg.ttl == 0 or self.game_over(msg.tag):
            return

        self.push_tag(msg.tag)
        next_mrr = self.manage_mrr(msg.mrr, self.net_list)

        for net in self.net_list:
            if self.is_reachable(net, msg.key):
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

    def handle_found(self, msg: Message):
        self.good_deal_update(msg.ip_send)

        if msg.code == "GET":
            value = self.routing_table.get(msg.ip_send, {}).get(msg.key)
            print(f"Retrieved value: {value}")
        elif msg.code == "PUT" and msg.mrr >= 0:
            if msg.ip_send not in self.routing_table:
                self.routing_table[msg.ip_send] = {}
            self.routing_table[msg.ip_send][msg.key] = msg.value

    def good_deal_update(self, ip_send: str):
        # on doit avoir une stratégie pour mettre à jour le bon deal
        pass

    def handle_invite(self, network: str, ip_send: str):
        if self.good_deal(network, ip_send):
            self.handle_join(network, ip_send)

    def handle_join(self, network: str, ip_send: str):
        if self.good_deal(network, ip_send):
            self.net_list.append(network)