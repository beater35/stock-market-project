def calculate_broker_commission(transaction_amount):
	"""Calculate the broker commission based on the transaction amount."""
	if transaction_amount <= 2500:
		return 10 
	elif 2501 <= transaction_amount <= 50000:
		return transaction_amount * 0.0036
	elif 50001 <= transaction_amount <= 500000:
		return transaction_amount * 0.0033 
	elif 500001 <= transaction_amount <= 2000000:
		return transaction_amount * 0.0031 
	elif 2000001 <= transaction_amount <= 10000000:
		return transaction_amount * 0.0027 
	else:
		return transaction_amount * 0.0024 
	

def calculate_sebon_fee(transaction_amount):
	"""Calculate the SEBON fee based on the transaction amount"""
	if transaction_amount <= 500000:
		return max(transaction_amount * 0.0015, 10) 
	elif 500001 <= transaction_amount <= 5000000:
		return transaction_amount * 0.0012
	else:
		return transaction_amount * 0.001
	

def calculate_capital_gain_tax(profit, user_type, short_term_profit=0, long_term_profit=0):
    """Calculate capital gain tax based on user type and holding period (short/long term)."""
    if profit <= 0:
        return 0  

    if user_type == 'institutional':
        return profit * 0.10 

    if user_type == 'individual':
        short_term_profit_cgt = short_term_profit * 0.075 
        long_term_profit_cgt = long_term_profit * 0.05
        total_capital_gain_tax = short_term_profit_cgt + long_term_profit_cgt
        return total_capital_gain_tax 
		
    return 0 


def calculate_total_amount_paid(transaction_amount, broker_commission, sebon_fee):
    """Calculate the total amount paid for BUY transactions after fees."""
    return transaction_amount + broker_commission + sebon_fee + 25 


def calculate_total_amount_received(transaction_amount, broker_commission, sebon_fee, capital_gain_tax):
    """Calculate the total amount received for SELL transactions after fees and taxes."""
    return transaction_amount - broker_commission - sebon_fee - capital_gain_tax - 25 