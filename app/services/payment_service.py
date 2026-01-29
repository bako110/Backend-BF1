
from typing import Optional
from datetime import datetime

class PaymentResult:
	def __init__(self, success: bool, transaction_id: Optional[str] = None, message: Optional[str] = None):
		self.success = success
		self.transaction_id = transaction_id
		self.message = message

async def process_payment(user_id: str, amount: float, method: str, offer: Optional[str] = None) -> PaymentResult:
	# Ici, tu pourrais intégrer Orange Money, MTN, InTouch, etc.
	# Simulation d'un paiement réussi
	transaction_id = f"MOCK-{user_id}-{int(datetime.utcnow().timestamp())}"
	return PaymentResult(success=True, transaction_id=transaction_id, message="Paiement simulé OK")
