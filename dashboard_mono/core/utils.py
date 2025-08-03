"""
Funzioni di utilità per deduplica, calcoli, ecc.
"""

def deduplicate_pnl_history(pnl_history):
    seen = set()
    deduped = []
    for entry in pnl_history:
        key = (entry.get('timestamp'), entry.get('pnl'))
        if key not in seen:
            seen.add(key)
            deduped.append(entry)
    return deduped
