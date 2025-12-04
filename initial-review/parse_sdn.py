#!/usr/bin/env python3
"""
OFAC SDN XML Parser
Extracts and structures data from the OFAC Specially Designated Nationals list
"""

import xml.etree.ElementTree as ET
import pandas as pd
import json
from datetime import datetime

def parse_sdn_xml(xml_file):
    """Parse the SDN XML file and extract all relevant data"""
    
    print("Parsing SDN XML file...")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Define namespace
    ns = {'sdn': 'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/XML'}
    
    # Get publication info
    pub_info = root.find('sdn:publshInformation', ns)
    if pub_info is not None:
        pub_date = pub_info.find('sdn:Publish_Date', ns).text
        record_count = pub_info.find('sdn:Record_Count', ns).text
        print(f"Publication Date: {pub_date}")
        print(f"Total Records: {record_count}")
    
    # Lists to store structured data
    entities = []
    aliases = []
    addresses = []
    dates_of_birth = []
    places_of_birth = []
    nationalities = []
    identifications = []
    programs = []
    
    # Parse each SDN entry
    entries = root.findall('sdn:sdnEntry', ns)
    print(f"\nProcessing {len(entries)} entries...")
    
    for entry in entries:
        # Basic entity information
        uid = entry.find('sdn:uid', ns).text
        last_name = entry.find('sdn:lastName', ns)
        last_name = last_name.text if last_name is not None else None
        first_name = entry.find('sdn:firstName', ns)
        first_name = first_name.text if first_name is not None else None
        sdn_type = entry.find('sdn:sdnType', ns).text
        title = entry.find('sdn:title', ns)
        title = title.text if title is not None else None
        
        # Remarks/notes
        remarks = entry.find('sdn:remarks', ns)
        remarks = remarks.text if remarks is not None else None
        
        # Entity data
        entity_data = {
            'uid': uid,
            'sdn_type': sdn_type,
            'first_name': first_name,
            'last_name': last_name,
            'title': title,
            'remarks': remarks
        }
        entities.append(entity_data)
        
        # Programs
        program_list = entry.find('sdn:programList', ns)
        if program_list is not None:
            for prog in program_list.findall('sdn:program', ns):
                programs.append({
                    'uid': uid,
                    'program': prog.text
                })
        
        # Aliases (AKA)
        aka_list = entry.find('sdn:akaList', ns)
        if aka_list is not None:
            for aka in aka_list.findall('sdn:aka', ns):
                aka_uid = aka.find('sdn:uid', ns).text
                aka_type = aka.find('sdn:type', ns).text
                aka_category = aka.find('sdn:category', ns)
                aka_category = aka_category.text if aka_category is not None else None
                aka_last_name = aka.find('sdn:lastName', ns)
                aka_last_name = aka_last_name.text if aka_last_name is not None else None
                aka_first_name = aka.find('sdn:firstName', ns)
                aka_first_name = aka_first_name.text if aka_first_name is not None else None
                
                aliases.append({
                    'entity_uid': uid,
                    'aka_uid': aka_uid,
                    'type': aka_type,
                    'category': aka_category,
                    'first_name': aka_first_name,
                    'last_name': aka_last_name
                })
        
        # Addresses
        address_list = entry.find('sdn:addressList', ns)
        if address_list is not None:
            for addr in address_list.findall('sdn:address', ns):
                addr_uid = addr.find('sdn:uid', ns).text
                addr1 = addr.find('sdn:address1', ns)
                addr1 = addr1.text if addr1 is not None else None
                addr2 = addr.find('sdn:address2', ns)
                addr2 = addr2.text if addr2 is not None else None
                addr3 = addr.find('sdn:address3', ns)
                addr3 = addr3.text if addr3 is not None else None
                city = addr.find('sdn:city', ns)
                city = city.text if city is not None else None
                state_prov = addr.find('sdn:stateOrProvince', ns)
                state_prov = state_prov.text if state_prov is not None else None
                postal = addr.find('sdn:postalCode', ns)
                postal = postal.text if postal is not None else None
                country = addr.find('sdn:country', ns)
                country = country.text if country is not None else None
                
                addresses.append({
                    'entity_uid': uid,
                    'address_uid': addr_uid,
                    'address1': addr1,
                    'address2': addr2,
                    'address3': addr3,
                    'city': city,
                    'state_province': state_prov,
                    'postal_code': postal,
                    'country': country
                })
        
        # Dates of Birth
        dob_list = entry.find('sdn:dateOfBirthList', ns)
        if dob_list is not None:
            for dob in dob_list.findall('sdn:dateOfBirthItem', ns):
                dob_uid = dob.find('sdn:uid', ns).text
                dob_date = dob.find('sdn:dateOfBirth', ns)
                dob_date = dob_date.text if dob_date is not None else None
                main_entry = dob.find('sdn:mainEntry', ns)
                main_entry = main_entry.text if main_entry is not None else None
                
                dates_of_birth.append({
                    'entity_uid': uid,
                    'dob_uid': dob_uid,
                    'date_of_birth': dob_date,
                    'main_entry': main_entry
                })
        
        # Places of Birth
        pob_list = entry.find('sdn:placeOfBirthList', ns)
        if pob_list is not None:
            for pob in pob_list.findall('sdn:placeOfBirthItem', ns):
                pob_uid = pob.find('sdn:uid', ns).text
                pob_place = pob.find('sdn:placeOfBirth', ns)
                pob_place = pob_place.text if pob_place is not None else None
                main_entry = pob.find('sdn:mainEntry', ns)
                main_entry = main_entry.text if main_entry is not None else None
                
                places_of_birth.append({
                    'entity_uid': uid,
                    'pob_uid': pob_uid,
                    'place_of_birth': pob_place,
                    'main_entry': main_entry
                })
        
        # Nationalities
        nat_list = entry.find('sdn:nationalityList', ns)
        if nat_list is not None:
            for nat in nat_list.findall('sdn:nationality', ns):
                nat_uid = nat.find('sdn:uid', ns).text
                nat_country = nat.find('sdn:country', ns)
                nat_country = nat_country.text if nat_country is not None else None
                main_entry = nat.find('sdn:mainEntry', ns)
                main_entry = main_entry.text if main_entry is not None else None
                
                nationalities.append({
                    'entity_uid': uid,
                    'nationality_uid': nat_uid,
                    'country': nat_country,
                    'main_entry': main_entry
                })
        
        # ID Numbers (passports, tax IDs, etc.)
        id_list = entry.find('sdn:idList', ns)
        if id_list is not None:
            for id_item in id_list.findall('sdn:id', ns):
                id_uid = id_item.find('sdn:uid', ns).text
                id_type = id_item.find('sdn:idType', ns)
                id_type = id_type.text if id_type is not None else None
                id_number = id_item.find('sdn:idNumber', ns)
                id_number = id_number.text if id_number is not None else None
                id_country = id_item.find('sdn:idCountry', ns)
                id_country = id_country.text if id_country is not None else None
                issue_date = id_item.find('sdn:issueDate', ns)
                issue_date = issue_date.text if issue_date is not None else None
                expiration_date = id_item.find('sdn:expirationDate', ns)
                expiration_date = expiration_date.text if expiration_date is not None else None
                
                identifications.append({
                    'entity_uid': uid,
                    'id_uid': id_uid,
                    'id_type': id_type,
                    'id_number': id_number,
                    'id_country': id_country,
                    'issue_date': issue_date,
                    'expiration_date': expiration_date
                })
    
    # Convert to DataFrames
    df_entities = pd.DataFrame(entities)
    df_programs = pd.DataFrame(programs)
    df_aliases = pd.DataFrame(aliases)
    df_addresses = pd.DataFrame(addresses)
    df_dob = pd.DataFrame(dates_of_birth)
    df_pob = pd.DataFrame(places_of_birth)
    df_nationalities = pd.DataFrame(nationalities)
    df_ids = pd.DataFrame(identifications)
    
    print(f"\n✓ Parsed {len(entities)} entities")
    print(f"✓ Found {len(programs)} program associations")
    print(f"✓ Found {len(aliases)} aliases")
    print(f"✓ Found {len(addresses)} addresses")
    print(f"✓ Found {len(dates_of_birth)} dates of birth")
    print(f"✓ Found {len(places_of_birth)} places of birth")
    print(f"✓ Found {len(nationalities)} nationalities")
    print(f"✓ Found {len(identifications)} identification documents")
    
    return {
        'entities': df_entities,
        'programs': df_programs,
        'aliases': df_aliases,
        'addresses': df_addresses,
        'dob': df_dob,
        'pob': df_pob,
        'nationalities': df_nationalities,
        'ids': df_ids,
        'pub_date': pub_date if pub_info is not None else None
    }

def filter_hezbollah(data):
    """Filter for Hezbollah-related entities"""
    
    print("\n" + "="*60)
    print("FILTERING FOR HEZBOLLAH-RELATED ENTITIES")
    print("="*60)
    
    # Get UIDs of all entities in Hezbollah program
    hezbollah_uids = data['programs'][
        data['programs']['program'].str.contains('HEZBOLLAH|HIZBALLAH|HIZBOLLAH', case=False, na=False)
    ]['uid'].unique()
    
    print(f"\nFound {len(hezbollah_uids)} entities with Hezbollah program designation")
    
    # Filter all dataframes
    hezbollah_data = {
        'entities': data['entities'][data['entities']['uid'].isin(hezbollah_uids)],
        'programs': data['programs'][data['programs']['uid'].isin(hezbollah_uids)],
        'aliases': data['aliases'][data['aliases']['entity_uid'].isin(hezbollah_uids)],
        'addresses': data['addresses'][data['addresses']['entity_uid'].isin(hezbollah_uids)],
        'dob': data['dob'][data['dob']['entity_uid'].isin(hezbollah_uids)],
        'pob': data['pob'][data['pob']['entity_uid'].isin(hezbollah_uids)],
        'nationalities': data['nationalities'][data['nationalities']['entity_uid'].isin(hezbollah_uids)],
        'ids': data['ids'][data['ids']['entity_uid'].isin(hezbollah_uids)],
        'pub_date': data['pub_date']
    }
    
    return hezbollah_data

def analyze_south_america(hezbollah_data):
    """Analyze Hezbollah entities with South American connections"""
    
    print("\n" + "="*60)
    print("SOUTH AMERICAN ANALYSIS")
    print("="*60)
    
    south_american_countries = [
        'Argentina', 'Brazil', 'Paraguay', 'Uruguay',
        'Colombia', 'Venezuela', 'Chile', 'Peru', 'Bolivia',
        'Ecuador', 'Guyana', 'Suriname', 'French Guiana'
    ]
    
    # Find entities with South American addresses
    sa_addresses = hezbollah_data['addresses'][
        hezbollah_data['addresses']['country'].isin(south_american_countries)
    ]
    
    sa_uids = sa_addresses['entity_uid'].unique()
    
    print(f"\nFound {len(sa_uids)} Hezbollah entities with South American addresses")
    print(f"Total South American addresses: {len(sa_addresses)}")
    
    # Country breakdown
    print("\nBreakdown by country:")
    country_counts = sa_addresses['country'].value_counts()
    for country, count in country_counts.items():
        print(f"  {country}: {count} addresses")
    
    # Get entities with SA connections
    sa_entities = hezbollah_data['entities'][
        hezbollah_data['entities']['uid'].isin(sa_uids)
    ]
    
    # Get all nationalities
    sa_nationalities = hezbollah_data['nationalities'][
        hezbollah_data['nationalities']['country'].isin(south_american_countries)
    ]
    
    print(f"\nFound {len(sa_nationalities)} South American nationality records")
    
    return {
        'uids': sa_uids,
        'entities': sa_entities,
        'addresses': sa_addresses,
        'nationalities': sa_nationalities
    }

def save_data(data, prefix='sdn'):
    """Save data to CSV files"""
    
    print(f"\n" + "="*60)
    print(f"SAVING DATA TO CSV FILES")
    print("="*60)
    
    for key, df in data.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            filename = f"/home/claude/{prefix}_{key}.csv"
            df.to_csv(filename, index=False)
            print(f"✓ Saved {filename} ({len(df)} rows)")

if __name__ == "__main__":
    # Parse the full SDN list
    sdn_data = parse_sdn_xml('/mnt/user-data/uploads/SDN.XML')
    
    # Save full dataset
    save_data(sdn_data, prefix='sdn_full')
    
    # Filter for Hezbollah
    hezbollah_data = filter_hezbollah(sdn_data)
    save_data(hezbollah_data, prefix='hezbollah')
    
    # Analyze South American connections
    sa_analysis = analyze_south_america(hezbollah_data)
    
    # Save South American subset
    sa_data = {
        'entities': sa_analysis['entities'],
        'addresses': sa_analysis['addresses'],
        'nationalities': sa_analysis['nationalities']
    }
    save_data(sa_data, prefix='hezbollah_south_america')
    
    print("\n" + "="*60)
    print("PARSING COMPLETE!")
    print("="*60)
    print("\nOutput files created:")
    print("  - sdn_full_*.csv - Complete OFAC SDN dataset")
    print("  - hezbollah_*.csv - All Hezbollah-designated entities")
    print("  - hezbollah_south_america_*.csv - Hezbollah entities with SA connections")
