import math

def get_country_ratio(country):
    ratios = {
        "United States": 1.00,
        "United States of America": 1.00,
        "Switzerland": 0.95,
        "Australia": 0.75,
        "Canada": 0.72,
        "United Kingdom": 0.68,
        "Germany": 0.65,
        "Netherlands": 0.62,
        "Sweden": 0.60,
        "Norway": 0.60,
        "Denmark": 0.58,
        "Israel": 0.55,
        "New Zealand": 0.52,
        "France": 0.50,
        "Belgium": 0.48,
        "Austria": 0.48,
        "Finland": 0.46,
        "Japan": 0.42,
        "South Korea": 0.38,
        "Spain": 0.35,
        "Italy": 0.34,
        "Czech Republic": 0.30,
        "Portugal": 0.28,
        "Poland": 0.27,
        "Greece": 0.25,
        "Hungary": 0.22,
        "Romania": 0.20,
        "Turkey": 0.18,
        "China": 0.17,
        "Russia": 0.16,
        "Malaysia": 0.15,
        "Mexico": 0.14,
        "Brazil": 0.13,
        "India": 0.18,
        "Argentina": 0.10,
        "Colombia": 0.10,
        "South Africa": 0.12,
        "Philippines": 0.10,
        "Indonesia": 0.09,
        "Vietnam": 0.09,
        "Thailand": 0.10,
        "Egypt": 0.08,
        "Pakistan": 0.08,
        "Bangladesh": 0.07,
        "Nigeria": 0.07,
        "Nepal": 0.06,
        "Sri Lanka": 0.08,
        "Missing": 1.00 # Assume US metrics if they don't provide country for now
    }
    return ratios.get(country, 0.30)

def calibrate_salary(raw_usd, country, years_exp):
    c_ratio = get_country_ratio(country)
    # The machine learning model already factors in YearsCode (experience).
    # Applying an additional multiplier here results in double-penalization.
    # We rely on the model for the experience curve and use c_ratio for the market adjustment.
    calibrated_usd = raw_usd * c_ratio
    return calibrated_usd, c_ratio, 1.0 # Return 1.0 for exp_mult to avoid breaking other logic

def get_calibrated_salary_range(country, years_exp, role, currency_info):
    c_ratio = get_country_ratio(country)
    y = float(years_exp) if years_exp else 0.0
    
    # Baseline constraints for India (in INR at a 0.18 country ratio)
    if y <= 2:
        low = 300000
        high = 900000
        label = f"Typical range for {role} fresher (0-2 years)"
    elif y <= 5:
        low = 800000
        high = 2000000
        label = f"Typical range for {role} mid-level (3-5 years)"
    else:
        low = 1800000
        high = 4500000
        label = f"Typical range for {role} senior (6+ years)"
        
    # Scale ranges using proportional logic:
    # India ratio is 0.18. 
    # To get actual USD baseline for the global market equivalent:
    # Baseline USD = INR_Baseline / 83.5 / 0.18
    base_low_usd = low / 83.5 / 0.18
    base_high_usd = high / 83.5 / 0.18
    
    # Now for current country, specific calibrated USD range:
    country_low_usd = base_low_usd * c_ratio
    country_high_usd = base_high_usd * c_ratio
    
    # Local currency value:
    local_low = country_low_usd * currency_info['rate']
    local_high = country_high_usd * currency_info['rate']
    
    if country == "India":
        l_lpa = local_low / 100000.0
        h_lpa = local_high / 100000.0
        return f"{label}: {currency_info['sym']}{l_lpa:.1f} LPA - {currency_info['sym']}{h_lpa:.1f} LPA"
    
    # Fallback to proper comma separation
    return f"{label}: {currency_info['sym']}{local_low:,.0f} - {currency_info['sym']}{local_high:,.0f}"
