from collections import OrderedDict
from utility.printable import Printable


class Transaction(Printable):
    """
    Sender: The sender of the coins.
    Recipient: The recipient of the coins.
    Signature: The signature of the transactions
    Amount: The amount of coins sent.
    """
    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])
