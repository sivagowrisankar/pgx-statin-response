import pandas as pd
import numpy as np
import random
import os
from datetime import date, timedelta

# --- Phenotype Assignment Functions (Used for simulation logic) ---

def assign_slco1b1_phenotype(genotype):
    """Maps SLCO1B1 genotype to a functional phenotype."""
    if genotype == 'TT':
        return 'Poor Function'
    elif genotype == 'CT':
        return 'Decreased Function'
    else: # CC
        return 'Normal Function'

def assign_cyp2c9_phenotype(genotype):
    """Maps CYP2C9 genotype to a metabolizer phenotype."""
    poor_metabolizers = ['*2/*2', '*2/*3', '*3/*3']
    intermediate_metabolizers = ['*1/*2', '*1/*3']
    if genotype in poor_metabolizers:
        return 'Poor Metabolizer'
    elif genotype in intermediate_metabolizers:
        return 'Intermediate Metabolizer'
    else: # *1/*1
        return 'Normal Metabolizer'

def assign_abcg2_phenotype(genotype):
    """Maps ABCG2 genotype to a functional phenotype."""
    if genotype == 'AA':
        return 'Poor Function'
    elif genotype == 'CA':
        return 'Decreased Function'
    else: # CC
        return 'Normal Function'

def assign_cyp3a4_phenotype(genotype):
    """Maps CYP3A4 genotype to a metabolizer phenotype."""
    if genotype == '*1/*22':
        return 'Intermediate Metabolizer'
    else: # *1/*1
        return 'Normal Metabolizer'

def assign_cyp3a5_phenotype(genotype):
    """Maps CYP3A5 genotype to a metabolizer phenotype based on expressor status."""
    if genotype == '*3/*3':
        return 'Poor Metabolizer' # Non-expressor
    elif genotype == '*1/*3':
        return 'Intermediate Metabolizer' # Expressor
    else: # *1/*1
        return 'Normal Metabolizer' # Expressor

def generate_synthetic_data_files(num_patients=150):
    """
    Generates and structures synthetic data into clinical, labs, and meds DataFrames.

    Args:
        num_patients (int): The number of patients to generate.

    Returns:
        tuple: A tuple containing three pandas DataFrames: 
               (clinical_df, labs_df, meds_df).
    """
    clinical_data = []
    labs_data = []
    meds_data = []

    # --- Genotype Frequencies (for simulation) ---
    slco1b1_genotypes = ['CC'] * 70 + ['CT'] * 25 + ['TT'] * 5
    cyp2c9_genotypes = ['*1/*1'] * 75 + ['*1/*2'] * 12 + ['*1/*3'] * 8 + ['*2/*2', '*2/*3', '*3/*3'] * 5
    abcg2_genotypes = ['CC'] * 70 + ['CA'] * 25 + ['AA'] * 5
    cyp3a4_genotypes = ['*1/*1'] * 90 + ['*1/*22'] * 10
    cyp3a5_genotypes = ['*3/*3'] * 85 + ['*1/*3'] * 14 + ['*1/*1'] * 1

    for i in range(num_patients):
        patient_id = f"PAT_{1000 + i}"
        age = np.random.randint(45, 76)
        sex = random.choice(['M', 'F'])
        bmi = round(np.random.normal(28.5, 4.5), 1)
        
        # --- Append Clinical Data ---
        clinical_data.append({'id': patient_id, 'age': age, 'sex': sex, 'bmi': bmi})

        # --- Simulate PGx-based LDL Response ---
        # (This logic is kept to make the lab values realistic)
        slco1b1_pheno = assign_slco1b1_phenotype(random.choice(slco1b1_genotypes))
        cyp2c9_pheno = assign_cyp2c9_phenotype(random.choice(cyp2c9_genotypes))
        abcg2_pheno = assign_abcg2_phenotype(random.choice(abcg2_genotypes))
        cyp3a4_pheno = assign_cyp3a4_phenotype(random.choice(cyp3a4_genotypes))
        cyp3a5_pheno = assign_cyp3a5_phenotype(random.choice(cyp3a5_genotypes))

        baseline_ldl = round(np.random.normal(160, 30))
        base_reduction = np.random.normal(0.40, 0.05)
        
        if slco1b1_pheno == 'Poor Function': base_reduction -= 0.15 
        elif slco1b1_pheno == 'Decreased Function': base_reduction -= 0.07
        if cyp2c9_pheno == 'Poor Metabolizer': base_reduction += 0.12
        elif cyp2c9_pheno == 'Intermediate Metabolizer': base_reduction += 0.06
        if abcg2_pheno == 'Poor Function': base_reduction += 0.08
        elif abcg2_pheno == 'Decreased Function': base_reduction += 0.04
        if cyp3a4_pheno == 'Intermediate Metabolizer': base_reduction += 0.05
        if cyp3a5_pheno == 'Normal Metabolizer': base_reduction -= 0.07
        elif cyp3a5_pheno == 'Intermediate Metabolizer': base_reduction -= 0.04

        percent_ldl_reduction = np.clip(base_reduction, 0.05, 0.65)
        on_statin_ldl = round(baseline_ldl * (1 - percent_ldl_reduction))

        # --- Fabricate Dates for Timeline ---
        start_date = date(2023, random.randint(1, 6), random.randint(1, 28))
        med_date = start_date + timedelta(days=random.randint(7, 21))
        follow_up_date = med_date + timedelta(days=random.randint(60, 120))

        # --- Append Labs Data ---
        labs_data.append({'id': patient_id, 'date': start_date, 'ldl': int(baseline_ldl)})
        labs_data.append({'id': patient_id, 'date': follow_up_date, 'ldl': int(on_statin_ldl)})

        # --- Append Meds Data ---
        drug = random.choice(['atorvastatin', 'rosuvastatin', 'simvastatin'])
        dose = random.choice(['10mg', '20mg', '40mg'])
        meds_data.append({'id': patient_id, 'date': med_date, 'drug': drug, 'dose': dose})
    
    # --- Create DataFrames ---
    clinical_df = pd.DataFrame(clinical_data)
    labs_df = pd.DataFrame(labs_data)
    meds_df = pd.DataFrame(meds_data)

    return clinical_df, labs_df, meds_df

if __name__ == '__main__':
    # Define file paths
    output_dir = os.path.join('..', 'processed_data')
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"Directory '{output_dir}' is ready.")

    # Generate the data
    clinical_df, labs_df, meds_df = generate_synthetic_data_files(num_patients=150)

    # Define output file paths
    clinical_file = os.path.join(output_dir, 'clinical_demo.csv')
    labs_file = os.path.join(output_dir, 'labs_demo.csv')
    meds_file = os.path.join(output_dir, 'meds_demo.csv')

    # Save to CSV files
    clinical_df.to_csv(clinical_file, index=False)
    print(f"\nSuccessfully generated clinical data for {len(clinical_df)} patients.")
    print(f"File saved as '{clinical_file}'")
    print("First 5 rows:")
    print(clinical_df.head())
    
    labs_df.to_csv(labs_file, index=False)
    print(f"\nSuccessfully generated lab data with {len(labs_df)} entries.")
    print(f"File saved as '{labs_file}'")
    print("First 5 rows:")
    print(labs_df.head())

    meds_df.to_csv(meds_file, index=False)
    print(f"\nSuccessfully generated medication data for {len(meds_df)} patients.")
    print(f"File saved as '{meds_file}'")
    print("First 5 rows:")
    print(meds_df.head())
