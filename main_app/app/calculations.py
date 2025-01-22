def calculate_broker_commission(transaction_amount):
	"""Calculate the broker commission based on the transaction amount."""
	if transaction_amount <= 2500:
		return 10 # Flat Rs. 10 for transactions up to Rs. 2500
	elif 2501 <= transaction_amount <= 50000:
		return transaction_amount * 0.0036 # 0.36%
	elif 50001 <= transaction_amount <= 500000:
		return transaction_amount * 0.0033 # 0.36%
	elif 500001 <= transaction_amount <= 2000000:
		return transaction_amount * 0.0031 # 0.31%
	elif 2000001 <= transaction_amount <= 10000000:
		return transaction_amount * 0.0027 # 0.27%
	else:
		return transaction_amount * 0.0024 # 0.24% for transactions above Rs. 10,000,000
	

def calculate_sebon_fee(transaction_amount):
	"""Calculate the SEBON fee based on the transaction amount"""
	if transaction_amount <= 500000:
		return max(transaction_amount * 0.0015, 10) # 0.15% or Rs. 10 whichever is higher
	elif 500001 <= transaction_amount <= 5000000:
		return transaction_amount * 0.0012 # 0.12%
	else:
		return transaction_amount * 0.001 # 0.10% for transactions above Rs. 5,000,000
	

def calculate_capital_gain_tax(profit, user_type, short_term_profit=0, long_term_profit=0):
    """Calculate capital gain tax based on user type and holding period (short/long term)."""
    if profit <= 0:
        return 0  # No tax on losses

    # Institutional investors pay a flat 10% tax on profit
    if user_type == 'institutional':
        return profit * 0.10  # 10% tax rate for institutional investors

    # Individual investors
    if user_type == 'individual':
        short_term_profit_cgt = short_term_profit * 0.075 # 7.5% tax rate for short term capital gains
        long_term_profit_cgt = long_term_profit * 0.05  # 5% tax rate for long-term capital gains
        total_capital_gain_tax = short_term_profit_cgt + long_term_profit_cgt
        return total_capital_gain_tax # Return total capital gain tax of both short term stocks and long term stocks

    return 0  # Default case (no tax)


def calculate_total_amount_paid(transaction_amount, broker_commission, sebon_fee):
    """Calculate the total amount paid for BUY transactions after fees."""
    return transaction_amount + broker_commission + sebon_fee + 25 # 25 is the fixed dp amount


def calculate_total_amount_received(transaction_amount, broker_commission, sebon_fee, capital_gain_tax):
    """Calculate the total amount received for SELL transactions after fees and taxes."""
    return transaction_amount - broker_commission - sebon_fee - capital_gain_tax - 25 # 25 is the fixed dp amount