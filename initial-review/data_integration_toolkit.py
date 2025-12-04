#!/usr/bin/env python3
"""
Data Integration Toolkit
Tools for cross-referencing new sources with OFAC data
"""

import pandas as pd
import re
from fuzzywuzzy import fuzz
from datetime import datetime

class HezbollahDataIntegrator:
    """Integrate and cross-reference Hezbollah data from multiple sources"""
    
    def __init__(self, ofac_data_dir='/home/claude/'):
        """Load OFAC baseline data"""
        print("Loading OFAC baseline data...")
        self.entities = pd.read_csv(f'{ofac_data_dir}hezbollah_entities.csv')
        self.aliases = pd.read_csv(f'{ofac_data_dir}hezbollah_aliases.csv')
        self.addresses = pd.read_csv(f'{ofac_data_dir}hezbollah_addresses.csv')
        self.ids = pd.read_csv(f'{ofac_data_dir}hezbollah_ids.csv')
        
        # Build name index for fast lookups
        self.name_index = self._build_name_index()
        print(f"✓ Loaded {len(self.entities)} OFAC entities")
        print(f"✓ Built index with {len(self.name_index)} names/aliases")
    
    def _build_name_index(self):
        """Build searchable index of all names and aliases"""
        names = {}
        
        # Primary names
        for _, entity in self.entities.iterrows():
            full_name = f"{entity['first_name'] if pd.notna(entity['first_name']) else ''} {entity['last_name']}"
            full_name = full_name.strip().upper()
            names[full_name] = entity['uid']
        
        # Aliases
        for _, alias in self.aliases.iterrows():
            full_name = f"{alias['first_name'] if pd.notna(alias['first_name']) else ''} {alias['last_name']}"
            full_name = full_name.strip().upper()
            names[full_name] = alias['entity_uid']
        
        return names
    
    def normalize_name(self, name):
        """Normalize name for comparison"""
        if pd.isna(name):
            return ""
        name = str(name).upper()
        # Remove common titles
        name = re.sub(r'\b(MR|MRS|MS|DR|PROF|SR|JR)\b\.?', '', name)
        # Remove extra whitespace
        name = ' '.join(name.split())
        return name
    
    def exact_match(self, name):
        """Check for exact match in OFAC data"""
        normalized = self.normalize_name(name)
        return self.name_index.get(normalized)
    
    def fuzzy_match(self, name, threshold=85):
        """Find fuzzy matches using Levenshtein distance"""
        normalized = self.normalize_name(name)
        matches = []
        
        for ofac_name, uid in self.name_index.items():
            score = fuzz.ratio(normalized, ofac_name)
            if score >= threshold:
                matches.append({
                    'uid': uid,
                    'ofac_name': ofac_name,
                    'input_name': name,
                    'match_score': score
                })
        
        return sorted(matches, key=lambda x: x['match_score'], reverse=True)
    
    def search_by_location(self, country=None, city=None):
        """Find entities with connections to specific locations"""
        results = self.addresses.copy()
        
        if country:
            results = results[results['country'].str.contains(country, case=False, na=False)]
        if city:
            results = results[results['city'].str.contains(city, case=False, na=False)]
        
        return results
    
    def search_by_id(self, id_number=None, id_type=None):
        """Search by ID number or type"""
        results = self.ids.copy()
        
        if id_number:
            results = results[results['id_number'].str.contains(str(id_number), case=False, na=False)]
        if id_type:
            results = results[results['id_type'].str.contains(id_type, case=False, na=False)]
        
        return results
    
    def get_entity_profile(self, uid):
        """Get complete profile for an entity"""
        # Convert to int if string
        if isinstance(uid, str):
            uid = int(uid)
        
        entity_df = self.entities[self.entities['uid'] == uid]
        if len(entity_df) == 0:
            return None
        
        entity = entity_df.iloc[0]
        
        profile = {
            'uid': uid,
            'basic_info': entity.to_dict(),
            'aliases': self.aliases[self.aliases['entity_uid'] == uid].to_dict('records'),
            'addresses': self.addresses[self.addresses['entity_uid'] == uid].to_dict('records'),
            'ids': self.ids[self.ids['entity_uid'] == uid].to_dict('records')
        }
        
        return profile
    
    def batch_search_names(self, names_list, fuzzy=True, threshold=85):
        """Search for multiple names at once"""
        results = []
        
        for name in names_list:
            # Try exact match first
            uid = self.exact_match(name)
            if uid:
                results.append({
                    'input_name': name,
                    'match_type': 'exact',
                    'uid': uid,
                    'match_score': 100
                })
            elif fuzzy:
                # Try fuzzy match
                fuzzy_matches = self.fuzzy_match(name, threshold)
                if fuzzy_matches:
                    results.append({
                        'input_name': name,
                        'match_type': 'fuzzy',
                        'uid': fuzzy_matches[0]['uid'],
                        'ofac_name': fuzzy_matches[0]['ofac_name'],
                        'match_score': fuzzy_matches[0]['match_score']
                    })
                else:
                    results.append({
                        'input_name': name,
                        'match_type': 'no_match',
                        'uid': None,
                        'match_score': 0
                    })
        
        return pd.DataFrame(results)
    
    def extract_names_from_text(self, text):
        """Extract potential names from unstructured text"""
        # Simple pattern for capitalized names (2-4 words)
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
        matches = re.findall(pattern, text)
        return list(set(matches))  # Remove duplicates
    
    def process_new_source(self, data, name_column=None, location_column=None):
        """
        Process a new data source and cross-reference with OFAC
        
        data: DataFrame or dict
        name_column: column containing names
        location_column: column containing locations
        """
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        
        results = []
        
        for idx, row in data.iterrows():
            result = {'source_row': idx}
            
            # Name matching
            if name_column and name_column in row:
                name = row[name_column]
                uid = self.exact_match(name)
                
                if uid:
                    result['ofac_match'] = 'exact'
                    result['ofac_uid'] = uid
                    result['confidence'] = 'high'
                else:
                    fuzzy = self.fuzzy_match(name, threshold=80)
                    if fuzzy:
                        result['ofac_match'] = 'fuzzy'
                        result['ofac_uid'] = fuzzy[0]['uid']
                        result['match_score'] = fuzzy[0]['match_score']
                        result['confidence'] = 'medium' if fuzzy[0]['match_score'] > 85 else 'low'
                    else:
                        result['ofac_match'] = 'none'
                        result['confidence'] = 'new_entity'
            
            # Location matching
            if location_column and location_column in row:
                location = row[location_column]
                loc_matches = self.search_by_location(country=location)
                if len(loc_matches) > 0:
                    result['location_matches'] = len(loc_matches)
            
            results.append(result)
        
        return pd.DataFrame(results)

def example_usage():
    """Example usage of the integration toolkit"""
    
    print("\n" + "="*70)
    print("DATA INTEGRATION TOOLKIT - EXAMPLE USAGE")
    print("="*70)
    
    # Initialize
    integrator = HezbollahDataIntegrator()
    
    # Example 1: Exact name match
    print("\n1. Exact Name Match:")
    uid = integrator.exact_match("Salman Raouf SALMAN")
    if uid:
        print(f"   ✓ Found exact match: UID {uid}")
    
    # Example 2: Fuzzy matching
    print("\n2. Fuzzy Name Matching:")
    matches = integrator.fuzzy_match("Salman Salman", threshold=80)
    for match in matches[:3]:
        print(f"   - {match['ofac_name']}: {match['match_score']}% match (UID: {match['uid']})")
    
    # Example 3: Location search
    print("\n3. Location Search (Colombia):")
    colombia_results = integrator.search_by_location(country="Colombia")
    print(f"   Found {len(colombia_results)} address records in Colombia")
    
    # Example 4: Batch search
    print("\n4. Batch Name Search:")
    test_names = [
        "Salman Raouf SALMAN",
        "Amer RADA",
        "John Smith",  # Won't match
        "Samer Reda"
    ]
    batch_results = integrator.batch_search_names(test_names)
    print(batch_results.to_string())
    
    # Example 5: Get full profile
    print("\n5. Full Entity Profile:")
    profile = integrator.get_entity_profile('27039')
    print(f"   Entity: {profile['basic_info']['last_name']}")
    print(f"   Aliases: {len(profile['aliases'])}")
    print(f"   Addresses: {len(profile['addresses'])}")
    print(f"   IDs: {len(profile['ids'])}")
    
    print("\n" + "="*70)
    print("INTEGRATION TOOLKIT READY FOR USE")
    print("="*70)
    print("\nTo use with your data:")
    print("1. Load your CSV/Excel: df = pd.read_csv('your_file.csv')")
    print("2. Process it: results = integrator.process_new_source(df, name_column='Name')")
    print("3. Review matches and expand your database")

if __name__ == "__main__":
    example_usage()
