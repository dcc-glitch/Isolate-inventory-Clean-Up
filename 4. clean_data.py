import pandas as pd
# Isolate Inventory  Shwetha_PWLDRD cleanup ONLY------
# Load the specific tab from csv file
file_path = "Isolates Inventory.xlsx"
df = pd.read_excel(file_path, sheet_name="Shwetha_PWLDRD")

# Clean the data: Drop empty IDs and deduplicate
df_cleaned = df.dropna(subset=['Real Isolate ID'])
df_dedup = df_cleaned.drop_duplicates(subset=['Real Isolate ID'], keep='first')

# Export to computer
output_file = "Shwetha_PWLDRD_cleaned.csv"
df_dedup.to_csv(output_file, index=False)

print(f"Success! Cleaned data saved to {output_file} in your Downloads folder.")
#---------------------------------------------------------------------------------

# 1. Targeting  specific tabs
file_path = "Isolates Inventory.xlsx"
tabs_to_test = ['mCAFEs_RCC_isolations', 'm-CAFEs', 'm-CAFEs SynCom isolates'] #sample data sets for now

print(f"Loading data from: {tabs_to_test}...")
# safely loads only the tabs we want
sheets_dict = pd.read_excel(file_path, sheet_name=tabs_to_test)

combined_data = []

# 2. Loop through and clean each tab
for tab_name, df in sheets_dict.items():
    print(f"Processing: {tab_name}")
    
    # --- Standardize ID Column ---
    id_aliases = ['Real Isolate ID', 'AMD strain number']
    for alias in id_aliases:
        if alias in df.columns:
            df = df.rename(columns={alias: 'Master_ID'})
            break  # Stops looking once it finds a match
            
    # --- Standardize Taxonomy Column ---
    taxonomy_aliases = ['SILVA classification', 'SILVA classification-genus', 
                        'Microorganism', 'Phylogenetic Class', 'NCBI Closest Relative', 'Class']
    for alias in taxonomy_aliases:
        if alias in df.columns:
            df = df.rename(columns={alias: 'Master_Taxonomy'})
            break
            
    # --- Standardize Environment / Source Column ---
    env_aliases = ['Source', 'Isolation Conditions']
    for alias in env_aliases:
        if alias in df.columns:
            df = df.rename(columns={alias: 'Master_Environment'})
            break
    
    # --- Clean and Store ---
    if 'Master_ID' in df.columns:
        # Drop rows where the ID is blank and add the tracking column
        df_cleaned = df.dropna(subset=['Master_ID']).copy()
        df_cleaned['Original_Tab'] = tab_name 
        
        # Add to our holding list
        combined_data.append(df_cleaned)
    else:
        # A helpful warning just in case a tab doesn't have a matching ID column
        print(f"  -> WARNING: No recognizable ID column found in {tab_name}. Skipping.")

# 3. Combine and Deduplicate
if combined_data:
    # Stack them all together
    master_df = pd.concat(combined_data, ignore_index=True)
    
    original_count = len(master_df)
    
    # Remove duplicates based on the Master_ID
    master_df = master_df.drop_duplicates(subset=['Master_ID'], keep='first')
    final_count = len(master_df)
    
    # 4. Export
    output_file = 'mCAFEs_Combined_Test.csv'
    master_df.to_csv(output_file, index=False)
    
    print("\n--- Success! ---")#finaloutput 
    print(f"Combined rows before deduplication: {original_count}")
    print(f"Final deduplicated rows: {final_count}")
    print(f"Duplicates removed: {original_count - final_count}")
    print(f"Saved to: {output_file} in your Downloads folder.")
else:
    print("No data was combined. Check your column names!")


