# Spending categories

analyze.py reads the rule lines below. Format: `- category: KEYWORD, KEYWORD`.
Keywords match inside the normalized merchant name (uppercase, store numbers and card suffixes removed).
Rules are checked top to bottom, and the first match wins. Spend that matches nothing goes to `uncategorized`.
Edit or add lines to fit your bank. Keep more specific keywords above broader ones.

- subscriptions: NETFLIX, SPOTIFY, ADOBE, HULU, DISNEY, ICLOUD, APPLE.COM, YOUTUBE PREMIUM, PLANET FITNESS
- utilities: PG&E, ELECTRIC, WATER, COMCAST, XFINITY, VERIZON, AT&T, T-MOBILE
- groceries: SAFEWAY, TRADER JOE, WHOLE FOODS, KROGER, PUBLIX, ALDI, COSTCO, WEGMANS
- coffee: STARBUCKS, PHILZ, DUNKIN, PEET
- dining: CHIPOTLE, SWEETGREEN, PHO, SUSHI, STEAKHOUSE, RESTAURANT, PIZZA, DOORDASH, GRUBHUB, UBER EATS
- transport: UBER, LYFT, METRO, TRANSIT, PARKING
- gas: SHELL, CHEVRON, EXXON, BP, MOBIL, SUNOCO
- shopping: AMAZON, TARGET, BEST BUY, WALMART, EBAY
