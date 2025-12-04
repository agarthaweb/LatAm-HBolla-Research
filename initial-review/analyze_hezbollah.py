#!/usr/bin/env python3
"""
OFAC SDN - Hezbollah Analysis
Enhanced search for Hezbollah-related entities
"""

import pandas as pd
import numpy as np

def identify_hezbollah_entities():
    """Identify all Hezbollah-related entities using multiple criteria"""
    
    print("="*60)
    print("IDENTIFYING HEZBOLLAH-RELATED ENTITIES")
    print("="*60)
    
    # Load data
    entities = pd.read_csv('/home/claude/sdn_full_entities.csv')
    programs = pd.read_csv('/home/claude/sdn_full_programs.csv')
    aliases = pd.read_csv('/home/claude/sdn_full_aliases.csv')
    
    hezbollah_uids = set()
    
    # 1. LEBANON program
    print("\n1. Entities in LEBANON program:")
    lebanon = programs[programs['program'] == 'LEBANON']['uid'].unique()
    hezbollah_uids.update(lebanon)
    print(f"   Found {len(lebanon)} entities")
    
    # 2. FTO (Foreign Terrorist Organizations)
    print("\n2. Entities in FTO program:")
    fto = programs[programs['program'] == 'FTO']['uid'].unique()
    fto_hezbollah = []
    for uid in fto:
        entity = entities[entities['uid'] == uid]
        name = str(entity['last_name'].values[0]) if len(entity) > 0 else ""
        remarks = str(entity['remarks'].values[0]) if len(entity) > 0 else ""
        
        # Check if Hezbollah is mentioned
        if any(term in name.upper() for term in ['HEZBOLLAH', 'HIZBALLAH', 'HIZBOLLAH', 'HIZB ALLAH']) or \
           any(term in remarks.upper() for term in ['HEZBOLLAH', 'HIZBALLAH', 'HIZBOLLAH', 'HIZB ALLAH']):
            fto_hezbollah.append(uid)
    
    hezbollah_uids.update(fto_hezbollah)
    print(f"   Found {len(fto_hezbollah)} Hezbollah entities in FTO")
    
    # 3. SDGT (Specially Designated Global Terrorists)
    print("\n3. Entities in SDGT program with Hezbollah mentions:")
    sdgt = programs[programs['program'] == 'SDGT']['uid'].unique()
    sdgt_hezbollah = []
    for uid in sdgt:
        entity = entities[entities['uid'] == uid]
        name = str(entity['last_name'].values[0]) if len(entity) > 0 else ""
        first_name = str(entity['first_name'].values[0]) if len(entity) > 0 else ""
        remarks = str(entity['remarks'].values[0]) if len(entity) > 0 else ""
        
        # Check if Hezbollah is mentioned
        if any(term in name.upper() for term in ['HEZBOLLAH', 'HIZBALLAH', 'HIZBOLLAH', 'HIZB ALLAH']) or \
           any(term in first_name.upper() for term in ['HEZBOLLAH', 'HIZBALLAH', 'HIZBOLLAH', 'HIZB ALLAH']) or \
           any(term in remarks.upper() for term in ['HEZBOLLAH', 'HIZBALLAH', 'HIZBOLLAH', 'HIZB ALLAH', 'LEBANESE HIZBALLAH']):
            sdgt_hezbollah.append(uid)
    
    hezbollah_uids.update(sdgt_hezbollah)
    print(f"   Found {len(sdgt_hezbollah)} Hezbollah entities in SDGT")
    
    # 4. Name-based search across all entities
    print("\n4. Direct name/remarks search across all entities:")
    name_search = entities[
        entities['last_name'].str.contains('HEZBOLLAH|HIZBALLAH|HIZBOLLAH|HIZB ALLAH', case=False, na=False) |
        entities['first_name'].str.contains('HEZBOLLAH|HIZBALLAH|HIZBOLLAH|HIZB ALLAH', case=False, na=False) |
        entities['remarks'].str.contains('HEZBOLLAH|HIZBALLAH|HIZBOLLAH|HIZB ALLAH|LEBANESE HIZBALLAH', case=False, na=False)
    ]
    name_search_uids = name_search['uid'].unique()
    hezbollah_uids.update(name_search_uids)
    print(f"   Found {len(name_search_uids)} entities via name/remarks search")
    
    # 5. Alias search
    print("\n5. Alias search:")
    alias_search = aliases[
        aliases['last_name'].str.contains('HEZBOLLAH|HIZBALLAH|HIZBOLLAH|HIZB ALLAH', case=False, na=False) |
        aliases['first_name'].str.contains('HEZBOLLAH|HIZBALLAH|HIZBOLLAH|HIZB ALLAH', case=False, na=False)
    ]
    alias_uids = alias_search['entity_uid'].unique()
    hezbollah_uids.update(alias_uids)
    print(f"   Found {len(alias_uids)} entities via alias search")
    
    print(f"\n{'='*60}")
    print(f"TOTAL UNIQUE HEZBOLLAH ENTITIES: {len(hezbollah_uids)}")
    print(f"{'='*60}")
    
    return list(hezbollah_uids)

def create_hezbollah_dataset(hezbollah_uids):
    """Create complete dataset for Hezbollah entities"""
    
    print("\nCreating comprehensive Hezbollah dataset...")
    
    # Load all data
    entities = pd.read_csv('/home/claude/sdn_full_entities.csv')
    programs = pd.read_csv('/home/claude/sdn_full_programs.csv')
    aliases = pd.read_csv('/home/claude/sdn_full_aliases.csv')
    addresses = pd.read_csv('/home/claude/sdn_full_addresses.csv')
    dob = pd.read_csv('/home/claude/sdn_full_dob.csv')
    pob = pd.read_csv('/home/claude/sdn_full_pob.csv')
    nationalities = pd.read_csv('/home/claude/sdn_full_nationalities.csv')
    ids = pd.read_csv('/home/claude/sdn_full_ids.csv')
    
    # Filter all tables
    hezbollah_data = {
        'entities': entities[entities['uid'].isin(hezbollah_uids)],
        'programs': programs[programs['uid'].isin(hezbollah_uids)],
        'aliases': aliases[aliases['entity_uid'].isin(hezbollah_uids)],
        'addresses': addresses[addresses['entity_uid'].isin(hezbollah_uids)],
        'dob': dob[dob['entity_uid'].isin(hezbollah_uids)],
        'pob': pob[pob['entity_uid'].isin(hezbollah_uids)],
        'nationalities': nationalities[nationalities['entity_uid'].isin(hezbollah_uids)],
        'ids': ids[ids['entity_uid'].isin(hezbollah_uids)]
    }
    
    # Save
    for key, df in hezbollah_data.items():
        filename = f'/home/claude/hezbollah_{key}.csv'
        df.to_csv(filename, index=False)
        print(f"✓ Saved {filename} ({len(df)} rows)")
    
    return hezbollah_data

def analyze_south_america(hezbollah_data):
    """Analyze South American connections"""
    
    print("\n" + "="*60)
    print("SOUTH AMERICAN CONNECTION ANALYSIS")
    print("="*60)
    
    south_american_countries = [
        'Argentina', 'Brazil', 'Paraguay', 'Uruguay',
        'Colombia', 'Venezuela', 'Chile', 'Peru', 'Bolivia',
        'Ecuador', 'Guyana', 'Suriname', 'French Guiana'
    ]
    
    # Triple border focus
    triple_border = ['Argentina', 'Brazil', 'Paraguay']
    
    # Address analysis
    print("\n1. ADDRESS ANALYSIS:")
    sa_addresses = hezbollah_data['addresses'][
        hezbollah_data['addresses']['country'].isin(south_american_countries)
    ]
    
    print(f"   Total SA addresses: {len(sa_addresses)}")
    if len(sa_addresses) > 0:
        print("\n   By country:")
        for country, count in sa_addresses['country'].value_counts().items():
            marker = "★" if country in triple_border else " "
            print(f"   {marker} {country}: {count}")
    
    sa_address_uids = sa_addresses['entity_uid'].unique()
    
    # Nationality analysis
    print("\n2. NATIONALITY ANALYSIS:")
    sa_nationalities = hezbollah_data['nationalities'][
        hezbollah_data['nationalities']['country'].isin(south_american_countries)
    ]
    
    print(f"   Total SA nationality records: {len(sa_nationalities)}")
    if len(sa_nationalities) > 0:
        print("\n   By country:")
        for country, count in sa_nationalities['country'].value_counts().items():
            marker = "★" if country in triple_border else " "
            print(f"   {marker} {country}: {count}")
    
    sa_nationality_uids = sa_nationalities['entity_uid'].unique()
    
    # ID documents
    print("\n3. ID DOCUMENT ANALYSIS:")
    sa_ids = hezbollah_data['ids'][
        hezbollah_data['ids']['id_country'].isin(south_american_countries)
    ]
    
    print(f"   Total SA ID documents: {len(sa_ids)}")
    if len(sa_ids) > 0:
        print("\n   By country:")
        for country, count in sa_ids['id_country'].value_counts().items():
            marker = "★" if country in triple_border else " "
            print(f"   {marker} {country}: {count}")
        
        print("\n   By ID type:")
        for id_type, count in sa_ids['id_type'].value_counts().head(10).items():
            print(f"     {id_type}: {count}")
    
    sa_id_uids = sa_ids['entity_uid'].unique()
    
    # Combined analysis
    all_sa_uids = set(sa_address_uids) | set(sa_nationality_uids) | set(sa_id_uids)
    
    print(f"\n{'='*60}")
    print(f"TOTAL ENTITIES WITH SA CONNECTIONS: {len(all_sa_uids)}")
    print(f"{'='*60}")
    print(f"  - Via addresses: {len(sa_address_uids)}")
    print(f"  - Via nationality: {len(sa_nationality_uids)}")
    print(f"  - Via ID documents: {len(sa_id_uids)}")
    
    # Get entity details
    sa_entities = hezbollah_data['entities'][
        hezbollah_data['entities']['uid'].isin(all_sa_uids)
    ]
    
    # Save SA-specific data
    sa_data = {
        'entities': sa_entities,
        'addresses': sa_addresses,
        'nationalities': sa_nationalities,
        'ids': sa_ids,
        'programs': hezbollah_data['programs'][
            hezbollah_data['programs']['uid'].isin(all_sa_uids)
        ],
        'aliases': hezbollah_data['aliases'][
            hezbollah_data['aliases']['entity_uid'].isin(all_sa_uids)
        ]
    }
    
    for key, df in sa_data.items():
        filename = f'/home/claude/hezbollah_southamerica_{key}.csv'
        df.to_csv(filename, index=False)
        print(f"\n✓ Saved {filename}")
    
    return sa_data, all_sa_uids

def print_sample_entities(hezbollah_data, sa_uids):
    """Print sample entities with SA connections"""
    
    print("\n" + "="*60)
    print("SAMPLE ENTITIES WITH SOUTH AMERICAN CONNECTIONS")
    print("="*60)
    
    sa_entities = hezbollah_data['entities'][
        hezbollah_data['entities']['uid'].isin(sa_uids)
    ]
    
    for idx, row in sa_entities.head(10).iterrows():
        uid = row['uid']
        print(f"\nUID: {uid}")
        print(f"Type: {row['sdn_type']}")
        name = f"{row['first_name'] if pd.notna(row['first_name']) else ''} {row['last_name']}"
        print(f"Name: {name.strip()}")
        
        # Programs
        progs = hezbollah_data['programs'][hezbollah_data['programs']['uid'] == uid]
        if len(progs) > 0:
            print(f"Programs: {', '.join(progs['program'].unique())}")
        
        # SA Addresses
        addrs = hezbollah_data['addresses'][
            (hezbollah_data['addresses']['entity_uid'] == uid) &
            (hezbollah_data['addresses']['country'].isin(['Argentina', 'Brazil', 'Paraguay', 'Uruguay', 
                                                           'Colombia', 'Venezuela', 'Chile', 'Peru']))
        ]
        if len(addrs) > 0:
            print("SA Addresses:")
            for _, addr in addrs.iterrows():
                loc = f"{addr['city'] if pd.notna(addr['city']) else ''}, {addr['country']}"
                print(f"  - {loc}")
        
        # Remarks
        if pd.notna(row['remarks']) and len(str(row['remarks'])) > 0:
            remarks = str(row['remarks'])[:200]
            print(f"Remarks: {remarks}...")

if __name__ == "__main__":
    # Identify all Hezbollah entities
    hezbollah_uids = identify_hezbollah_entities()
    
    # Create full dataset
    hezbollah_data = create_hezbollah_dataset(hezbollah_uids)
    
    # Analyze South American connections
    sa_data, sa_uids = analyze_south_america(hezbollah_data)
    
    # Print samples
    if len(sa_uids) > 0:
        print_sample_entities(hezbollah_data, sa_uids)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print("\nFiles created:")
    print("  - hezbollah_*.csv - All Hezbollah entities and related data")
    print("  - hezbollah_southamerica_*.csv - SA connections only")
