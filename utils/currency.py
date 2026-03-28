def get_currency_info(country):
    rates = {
        "United States": {"rate": 1.0, "sym": "$", "code": "USD"},
        "India": {"rate": 83.0, "sym": "₹", "code": "INR"},
        "United Kingdom": {"rate": 0.79, "sym": "£", "code": "GBP"},
        "Germany": {"rate": 0.92, "sym": "€", "code": "EUR"},
        "Canada": {"rate": 1.35, "sym": "C$", "code": "CAD"},
        "France": {"rate": 0.92, "sym": "€", "code": "EUR"},
        "Pakistan": {"rate": 278.0, "sym": "Rs", "code": "PKR"},
        "Nigeria": {"rate": 1200.0, "sym": "₦", "code": "NGN"},
        "Brazil": {"rate": 5.0, "sym": "R$", "code": "BRL"},
        "Indonesia": {"rate": 15600.0, "sym": "Rp", "code": "IDR"},
    }
    return rates.get(country, {"rate": 1.0, "sym": "$", "code": "USD"})

def format_salary(salary_usd, country):
    info = get_currency_info(country)
    local_sal = salary_usd * info['rate']
    
    if country == "India":
        lpa = local_sal / 100000.0
        return f"{info['sym']}{lpa:.1f} LPA (approximately ${salary_usd:,.0f} USD)", local_sal, info['sym']
    elif country == "United States" or country not in ["India", "United Kingdom", "Germany", "Canada", "France", "Pakistan", "Nigeria", "Brazil", "Indonesia"]:
        return f"${salary_usd:,.0f}", local_sal, "$"
    else:
        return f"{info['sym']}{local_sal:,.0f} (approximately ${salary_usd:,.0f} USD)", local_sal, info['sym']

def format_currency_amount(amount_usd, country, always_full=False):
    info = get_currency_info(country)
    local_val = amount_usd * info['rate']
    
    if country == "United States" or info['code'] == "USD":
        return f"${local_val:,.0f}"
        
    if country == "India" and not always_full:
        if abs(local_val) >= 100000:
            return f"{info['sym']}{(local_val/100000.0):.1f} LPA"
        return f"{info['sym']}{local_val:,.0f}"
    return f"{info['sym']}{local_val:,.0f}"
