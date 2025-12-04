# QUICK START GUIDE
## Hezbollah South America Research Project

### What You Have Now

✓ **Complete OFAC SDN dataset** parsed and structured  
✓ **146 Hezbollah entities** identified and extracted  
✓ **3 South American entities** with direct OFAC connections  
✓ **Python tools** for data integration and cross-referencing  

---

## Key Files Overview

### Documentation
- `RESEARCH_SUMMARY.md` - Comprehensive findings and analysis
- `QUICK_START_GUIDE.md` - This file
- `FILE_MANIFEST.txt` - Complete file listing

### Core Datasets (CSV)
- `hezbollah_entities.csv` - 146 entities (core data)
- `hezbollah_aliases.csv` - 425 aliases/AKAs
- `hezbollah_addresses.csv` - 211 addresses worldwide
- `hezbollah_ids.csv` - 521 identification documents

### South America Subset
- `hezbollah_southamerica_entities.csv` - 3 entities with SA connections
- `hezbollah_southamerica_aliases.csv` - Their aliases
- `hezbollah_southamerica_addresses.csv` - SA addresses  
- `hezbollah_southamerica_ids.csv` - SA ID documents

### Python Scripts
- `parse_sdn.py` - Parse OFAC SDN XML files
- `analyze_hezbollah.py` - Hezbollah-specific analysis
- `data_integration_toolkit.py` - Cross-reference new sources

---

## The 3 South American Entities

### 🔴 HIGH PRIORITY

**1. Salman Raouf SALMAN (UID: 27039)**
- **Colombian national** with multiple passports/IDs
- **7 aliases** including "Andree MARQUEZ"
- OFAC Program: SDGT (Linked to Hizballah)
- Documents: 3 Colombian passports/IDs

**2. Amer Mohamed Akil RADA (UID: 44499)**
- **Colombia-Venezuela nexus**
- Colombian cedula + Venezuelan ID
- OFAC Program: SDGT (Linked to Hizballah)
- Possible family connection to #3

**3. Samer Akil RADA (UID: 44522)**
- **Venezuela address** (city not specified)
- Colombian ID number
- OFAC Program: SDGT (Linked to Hizballah)
- Shares "RADA" surname with #2

---

## Next Steps: Integrating Your Sources

### Step 1: Prepare Your Data

**For blog posts/articles:**
```python
# Save as CSV with columns: name, location, date, source_url, summary
# Example:
# name,location,date,source_url,summary
# "Hussein Jammal","Ciudad del Este",2023-05-15,"http://...",Business owner suspected...
```

**For PDFs:**
- Extract text to CSV using the toolkit
- Focus on: names, locations, dates, activities, companies

### Step 2: Run Cross-Reference

```python
from data_integration_toolkit import HezbollahDataIntegrator
import pandas as pd

# Initialize
integrator = HezbollahDataIntegrator()

# Load your data
your_data = pd.read_csv('your_sources.csv')

# Process and match
results = integrator.process_new_source(
    your_data, 
    name_column='name',
    location_column='location'
)

# View matches
print(results[results['ofac_match'] != 'none'])

# Save results
results.to_csv('cross_reference_results.csv')
```

### Step 3: Expand the Network

For each match found:
1. Get full OFAC profile
2. Look for family members (check last names)
3. Find business associates
4. Map corporate connections
5. Track financial flows

```python
# Get detailed profile
uid = results.iloc[0]['ofac_uid']  # First match
profile = integrator.get_entity_profile(uid)

# See all data
print(f"Aliases: {len(profile['aliases'])}")
print(f"Addresses: {len(profile['addresses'])}")
print(f"ID Documents: {len(profile['ids'])}")
```

---

## Common Research Tasks

### Task 1: Search for a Name

```python
integrator = HezbollahDataIntegrator()

# Exact match
uid = integrator.exact_match("Salman Raouf SALMAN")

# Fuzzy match (handles typos, variations)
matches = integrator.fuzzy_match("Salman Salman", threshold=80)
for match in matches:
    print(f"{match['ofac_name']}: {match['match_score']}%")
```

### Task 2: Batch Search Many Names

```python
# List of names from your sources
names_to_check = [
    "Hussein Jammal",
    "Assad Barakat", 
    "Ali Khalil",
    # ... etc
]

results = integrator.batch_search_names(names_to_check, fuzzy=True)
print(results[results['match_type'] != 'no_match'])
```

### Task 3: Find Entities by Location

```python
# Search by country
colombia = integrator.search_by_location(country="Colombia")
print(f"Found {len(colombia)} Colombian connections")

# Search by city
ciudad_del_este = integrator.search_by_location(city="Ciudad del Este")
```

### Task 4: Search by ID Number

```python
# If you have passport/ID numbers from sources
results = integrator.search_by_id(id_number="AD059541")
```

---

## Building Your Database

### Recommended Schema

Create a master database with these tables:

**1. Entities** (your main table)
- entity_id (your own ID system)
- ofac_uid (link to OFAC if matched)
- full_name
- aliases (JSON or separate table)
- entity_type (individual/organization)
- confidence_level (high/medium/low/unverified)

**2. Activities**
- activity_id
- entity_id (FK)
- date
- location
- activity_type (financial, operational, etc.)
- description
- source_url
- evidence_file

**3. Relationships**
- relationship_id
- entity_1_id (FK)
- entity_2_id (FK)
- relationship_type (family, business, associate)
- confidence_level
- source

**4. Locations**
- location_id
- entity_id (FK)
- address
- city, country
- location_type (residence, business, etc.)
- dates_active (from-to)

**5. Financial**
- transaction_id
- entity_id (FK)
- amount
- currency
- source_account
- destination_account
- date
- source

---

## Tips for Your Federal Presentation

### Do's:
✓ **Cite everything** - Every claim needs a source  
✓ **Show confidence levels** - OFAC match = high, fuzzy = medium, unverified = low  
✓ **Map networks visually** - Use network graphs  
✓ **Include timelines** - Show activity over time  
✓ **Quantify** - "X entities, Y connections, Z transactions"  
✓ **Focus on tri-border** - Argentina/Brazil/Paraguay is your unique contribution  

### Don'ts:
✗ **Don't over-claim** - Distinguish proven vs suspected  
✗ **Don't ignore data quality** - Be upfront about gaps  
✗ **Don't forget context** - Explain why this matters  
✗ **Don't skip validation** - Cross-check across multiple sources  

### Key Metrics to Present:
- Total entities identified
- OFAC-designated vs newly discovered
- Geographic concentration (heat map)
- Network density (how connected)
- Timeline of activity
- Financial flows (if available)
- Evidence quality breakdown

---

## Common Questions

**Q: Why only 3 SA entities in OFAC?**  
A: Hezbollah operations in the tri-border area are more covert. Many operatives use local identities and aren't yet designated. Your research fills this gap.

**Q: How do I handle name variations?**  
A: Use the fuzzy matching with 80-85% threshold. Review all matches manually.

**Q: What if I find someone not in OFAC?**  
A: Document them thoroughly! This is valuable intelligence. Note all evidence and sources.

**Q: How should I structure my final deliverable?**  
A: See RESEARCH_SUMMARY.md for recommended format. Focus on: Executive Summary → Entity Profiles → Network Analysis → Evidence → Recommendations.

**Q: What about data security?**  
A: Keep a secure backup. Don't share raw data publicly. For federal submission, use secure transfer methods.

---

## When You're Ready for Dashboard Development

We can build:
- Interactive network visualization (D3.js, Plotly)
- Geographic heat maps (Folium, Plotly)
- Timeline visualizations
- Entity relationship diagrams
- Search/filter interface
- PDF export capability
- Data validation tools

Let me know when you want to start on that phase!

---

## Troubleshooting

**Issue: "Module not found" error**  
Solution: Install required packages:
```bash
pip install pandas fuzzywuzzy python-Levenshtein --break-system-packages
```

**Issue: CSV encoding errors**  
Solution: Specify encoding when reading:
```python
df = pd.read_csv('file.csv', encoding='utf-8')
# or try: encoding='latin-1'
```

**Issue: Too many fuzzy matches**  
Solution: Increase threshold:
```python
matches = integrator.fuzzy_match(name, threshold=90)  # More strict
```

---

## Contact Points

As you work through your other sources, send me:
1. **Sample data** (CSV or text) for initial processing
2. **Specific questions** about entities you find
3. **Integration challenges** if the toolkit doesn't handle your data format
4. **Dashboard requirements** when you're ready to visualize

**Next Steps:** Share your blog post/PDF data and we'll start cross-referencing!

---

*This toolkit is designed to grow with your research. As you discover new entities and connections, the database becomes more valuable. Focus on quality documentation and source citation - that's what makes this useful for federal authorities.*
