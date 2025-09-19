import pandas as pd
import numpy as np
import random

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

def generate_synthetic_data(num_patients=150):
    """
    Generates a synthetic dataset for statin pharmacogenomics.

    Args:
        num_patients (int): The number of patients to generate.

    Returns:
        pandas.DataFrame: A DataFrame with synthetic patient data.
    """
    data = []
    
    # Define genotype frequencies (approximations for a general population)
    slco1b1_genotypes = ['CC'] * 70 + ['CT'] * 25 + ['TT'] * 5
    cyp2c9_genotypes = ['*1/*1'] * 75 + ['*1/*2'] * 12 + ['*1/*3'] * 8 + ['*2/*2', '*2/*3', '*3/*3'] * 5
    abcg2_genotypes = ['CC'] * 70 + ['CA'] * 25 + ['AA'] * 5
    cyp3a4_genotypes = ['*1/*1'] * 90 + ['*1/*22'] * 10
    cyp3a5_genotypes = ['*3/*3'] * 85 + ['*1/*3'] * 14 + ['*1/*1'] * 1 # Most are non-expressors

    for i in range(num_patients):
        patient_id = f"PAT_{1000 + i}"
        age = np.random.randint(45, 76)
        sex = random.choice(['M', 'F'])
        bmi = round(np.random.normal(28.5, 4.5), 1)

        # --- Generate Genotypes and Phenotypes ---
        slco1b1_gt = random.choice(slco1b1_genotypes)
        cyp2c9_gt = random.choice(cyp2c9_genotypes)
        abcg2_gt = random.choice(abcg2_genotypes)
        cyp3a4_gt = random.choice(cyp3a4_genotypes)
        cyp3a5_gt = random.choice(cyp3a5_genotypes)

        slco1b1_pheno = assign_slco1b1_phenotype(slco1b1_gt)
        cyp2c9_pheno = assign_cyp2c9_phenotype(cyp2c9_gt)
        abcg2_pheno = assign_abcg2_phenotype(abcg2_gt)
        cyp3a4_pheno = assign_cyp3a4_phenotype(cyp3a4_gt)
        cyp3a5_pheno = assign_cyp3a5_phenotype(cyp3a5_gt)

        # --- Simulate LDL levels based on genotypes ---
        # Start with a baseline LDL
        baseline_ldl = round(np.random.normal(160, 30))
        
        # Simulate Statin Response (% LDL reduction)
        # Base response is around 40% reduction
        base_reduction = np.random.normal(0.40, 0.05)
        
        # Modify reduction based on PGx phenotypes
        # SLCO1B1 Poor Function -> less effective response (less reduction)
        if slco1b1_pheno == 'Poor Function':
            base_reduction -= 0.15 
        elif slco1b1_pheno == 'Decreased Function':
            base_reduction -= 0.07

        # CYP2C9 Poor Metabolizer -> more drug exposure, greater response (more reduction)
        if cyp2c9_pheno == 'Poor Metabolizer':
            base_reduction += 0.12
        elif cyp2c9_pheno == 'Intermediate Metabolizer':
            base_reduction += 0.06
            
        # ABCG2 Poor Function -> increased statin exposure -> greater response
        if abcg2_pheno == 'Poor Function':
            base_reduction += 0.08
        elif abcg2_pheno == 'Decreased Function':
            base_reduction += 0.04
        
        # CYP3A4 Intermediate Metabolizer -> increased statin exposure -> greater response
        if cyp3a4_pheno == 'Intermediate Metabolizer':
            base_reduction += 0.05

        # CYP3A5 Expressors (*1 allele) -> faster metabolism -> less response
        if cyp3a5_pheno == 'Normal Metabolizer':
            base_reduction -= 0.07
        elif cyp3a5_pheno == 'Intermediate Metabolizer':
            base_reduction -= 0.04

        # Ensure reduction is within a plausible range (e.g., 5% to 65%)
        percent_ldl_reduction = np.clip(base_reduction, 0.05, 0.65)
        
        # Calculate on-statin LDL
        on_statin_ldl = round(baseline_ldl * (1 - percent_ldl_reduction))
        
        data.append({
            'PatientID': patient_id,
            'Age': age,
            'Sex': sex,
            'BMI': bmi,
            'SLCO1B1_Genotype': slco1b1_gt,
            'SLCO1B1_Phenotype': slco1b1_pheno,
            'CYP2C9_Genotype': cyp2c9_gt,
            'CYP2C9_Phenotype': cyp2c9_pheno,
            'ABCG2_Genotype': abcg2_gt,
            'ABCG2_Phenotype': abcg2_pheno,
            'CYP3A4_Genotype': cyp3a4_gt,
            'CYP3A4_Phenotype': cyp3a4_pheno,
            'CYP3A5_Genotype': cyp3a5_gt,
            'CYP3A5_Phenotype': cyp3a5_pheno,
            'Baseline_LDL': int(baseline_ldl),
            'On_Statin_LDL': on_statin_ldl,
            'Percent_LDL_Reduction': round(percent_ldl_reduction * 100, 1)
        })

    df = pd.DataFrame(data)
    
    # Reorder columns for better readability
    column_order = [
        'PatientID', 'Age', 'Sex', 'BMI', 
        'Baseline_LDL', 'On_Statin_LDL', 'Percent_LDL_Reduction',
        'SLCO1B1_Genotype', 'SLCO1B1_Phenotype', 
        'CYP2C9_Genotype', 'CYP2C9_Phenotype', 
        'ABCG2_Genotype', 'ABCG2_Phenotype',
        'CYP3A4_Genotype', 'CYP3A4_Phenotype',
        'CYP3A5_Genotype', 'CYP3A5_Phenotype'
    ]
    
    return df[column_order]

if __name__ == '__main__':
    # Generate the data
    statin_data = generate_synthetic_data(num_patients=150)
    
    # Save to a CSV file
    output_filename = '../processed_data/synthetic_statin_data.csv'
    statin_data.to_csv(output_filename, index=False)
    
    print(f"Successfully generated synthetic data for {len(statin_data)} patients.")
    print(f"File saved as '{output_filename}'")
    print("\nFirst 5 rows of the generated data:")
    print(statin_data.head())

