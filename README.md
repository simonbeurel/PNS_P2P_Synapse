# PNS_P2P_Synapse
Implementation of Synapse's protocol (made by Luigi Liquori)

## Python

To use the project you need python 3.11, because the project uses the `match` statement and typing features.

## Implementation

The file `white_box.py` contains the implement of the pseudo-code of the White-Box Protocol describe in the papers in `/doc`.

To simulate a `Message`, I defined a class `Message` in the file with the class decorator `@dataclass` to handle the message's attributes.
Then I have a `SynapseNode` class that contains the implementation of the protocol. 

## Future Work

Maybe implement the protocol in a more realistic way, with a network and a real message exchange. 

