import re
import phonenumbers
from dateutil.parser import parse
import pycountry
import os
import pandas as pd

# --- 1. CONFIGURATION & PATTERNS ---

# Comprehensive Date Patterns
DATE_PATTERNS = [
    r'\b\d{4}-\d{2}-\d{2}\b',                   # ISO_YYYY-MM-DD
    r'\b\d{1,2}/\d{1,2}/\d{4}\b',               # MM/DD/YYYY
    r'\b\d{1,2}-\d{1,2}-\d{4}\b',               # DD-MM-YYYY
    r'\b\d{1,2}\.\d{1,2}\.\d{4}\b',             # Dotted
    r'\b\d{8}\b',                               # YYYYMMDD
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\b',  # Mon_DD,_YYYY
    r'\b\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4}\b'        # DD-Mon-YYYY
]

# Comprehensive Phone Patterns
PHONE_PATTERNS = [
    r'\+\d{1,3}\s?\d{7,14}',                    # International
    r'\(\d{3}\)\s?\d{3}[-\s]?\d{4}',            # National
    r'\b\d{3}-\d{3}-\d{4}\b',                   # Dashes
    r'\b\d{3}\.\d{3}\.\d{4}\b',                 # Dots
    r'\b\d{3}\s\d{3,4}\s\d{3,4}\b'              # Spaces
]

# --- 2. LOAD LOOKUP DATA ---
def load_lookup_data():
    countries = {c.name.lower() for c in pycountry.countries}
    
    # Base legal suffixes
    legal_suffixes = {"pvt ltd", "ltd", "inc", "gmbh", "co kg", "plc", "llc", "corp", "private limited", "group", "holdings"}
    
    # Load from files if they exist
    if os.path.exists('Training_data/legal.txt'):
        try:
            with open('Training_data/legal.txt', 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip().lower() for line in f.readlines() if line.strip()]
                legal_suffixes.update(lines)
        except: pass
            
    if os.path.exists('Training_data/countries.txt'):
        try:
            with open('Training_data/countries.txt', 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip().lower() for line in f.readlines() if line.strip()]
                countries.update(lines)
        except: pass

    return countries, list(legal_suffixes)

COUNTRIES, LEGAL_SUFFIXES = load_lookup_data()

# --- 3. CLASSIFICATION LOGIC ---
def get_column_stats(series):
    """
    Returns the confidence score for each category for a given column.
    """
    clean_series = series.dropna().astype(str)
    total_rows = len(clean_series)
    
    if total_rows == 0:
        return {"Phone Number": 0, "Company Name": 0, "Country": 0, "Date": 0, "Other": 1}

    # Sample for speed
    sample = clean_series.head(100).tolist()
    scores = {"Phone Number": 0, "Date": 0, "Country": 0, "Company Name": 0, "Other": 0}

    for item in sample:
        clean_item = item.strip()
        lower_item = clean_item.lower()
        matched = False

        # A. Check Date (Using Patterns first, then Library)
        if not matched:
            # Fast Regex Check
            for pattern in DATE_PATTERNS:
                if re.search(pattern, clean_item, re.IGNORECASE):
                    scores["Date"] += 1
                    matched = True
                    break
            # Fallback to slower library check if regex failed but looks promising
            if not matched and len(clean_item) > 5 and re.search(r'\d', clean_item):
                try:
                    parse(clean_item, fuzzy=False)
                    scores["Date"] += 1
                    matched = True
                except: pass

        # B. Check Phone (Using Patterns first, then Library)
        if not matched:
            # Fast Regex Check
            for pattern in PHONE_PATTERNS:
                if re.search(pattern, clean_item):
                    scores["Phone Number"] += 1
                    matched = True
                    break
            
            # Fallback to library check (Strict)
            if not matched:
                digit_count = sum(c.isdigit() for c in clean_item)
                if digit_count >= 7:
                    try:
                        z = phonenumbers.parse(clean_item, "US") 
                        if phonenumbers.is_possible_number(z):
                            scores["Phone Number"] += 1
                            matched = True
                    except: pass

        # C. Check Country
        if not matched:
            if lower_item in COUNTRIES:
                scores["Country"] += 1
                matched = True

        # D. Check Company
        if not matched:
            # Suffix check
            if any(suffix in lower_item for suffix in LEGAL_SUFFIXES):
                scores["Company Name"] += 1
                matched = True
            # Simple Heuristic: Capitalized words that aren't dates/countries often are companies
            elif not re.search(r'\d', clean_item) and clean_item.istitle() and len(clean_item.split()) > 1:
                 scores["Company Name"] += 0.5 # Give half a point for "maybe"

        # E. Other
        if not matched:
            scores["Other"] += 1
            
    # Normalize scores
    return {k: v / len(sample) for k, v in scores.items()}

def get_column_type(series):
    """Returns the single best semantic type."""
    stats = get_column_stats(series)
    best_cat = max(stats, key=stats.get)
    
    # Confidence threshold: if winner has < 20% votes, it's Other
    if stats[best_cat] < 0.2:
        return "Other"
    return best_cat

# --- 4. PARSING LOGIC (For Part B) ---
def parse_phone(phone_str):
    """Parses phone string into (Country, Number)"""
    phone_str = str(phone_str)
    try:
        parsed = phonenumbers.parse(phone_str, "US")
        from phonenumbers.phonenumberutil import region_code_for_number
        region_code = region_code_for_number(parsed)
        country_name = pycountry.countries.get(alpha_2=region_code).name if region_code else ""
        return country_name, str(parsed.national_number)
    except:
        return "", phone_str

def parse_company(company_str):
    """Parses company string into (Name, Legal)"""
    company_str = str(company_str)
    clean_str = company_str.lower().strip()
    
    sorted_suffixes = sorted(LEGAL_SUFFIXES, key=len, reverse=True)
    
    for suffix in sorted_suffixes:
        pattern = re.compile(r'\b' + re.escape(suffix) + r'[\.]?$', re.IGNORECASE)
        match = pattern.search(company_str)
        if match:
            found_suffix = match.group().strip()
            name_part = company_str[:match.start()].strip()
            name_part = name_part.rstrip(",.- ")
            return name_part, found_suffix
            
    return company_str, ""