import difflib , re


def calculate_similarity(s1, s2):
    # Normalize the strings
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()
    
    # Basic similarity ratio
    basic_ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
    
    # Split strings into components for name reordering check
    s1_parts = sorted(re.split(r'\s+', s1))
    s2_parts = sorted(re.split(r'\s+', s2))
    
    # Check for exact match or reordered names
    if s1 == s2:
        return str(100.00)
    elif s1_parts == s2_parts:
        return str(100.00)
    elif basic_ratio > 0.8:  # Adjust this threshold as needed
        return str(round(basic_ratio * 100, 2))
    else:
        return str(round(basic_ratio * 100 * 0.9, 2))

