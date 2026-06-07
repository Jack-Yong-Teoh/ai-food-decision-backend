from enum import Enum


class TransactionType(Enum):
    PAYMENT = "payment"
    TOP_UP = "top_up"
    REFUND = "refund"
    DEDUCT = "deduct"
