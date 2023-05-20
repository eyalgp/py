import pandas as pd
from collections import Counter

InnerPercentAbove = 5

# Read the sample names from the CSV file
samples = pd.read_excel("ANI90_0000020_Family_Counts.xlsx")['Sample'].tolist()

# Initialize a dictionary to store the number of families for each sample
num_families = {}

# Initialize a dictionary to store the family counts for each sample
family_counts = {}

# Loop over each sample and read the corresponding TSV file
for sample in samples:
    tsv_file = f'1450_phylodists/{sample}.contigLin.assembled.tsv'

    # Initialize a list to store the family names for this sample
    family_names = []

    # Open the TSV file and loop over each line
    with open(tsv_file, "r") as tsvfile:
        for line in tsvfile:
            # Check if the line contains a bacteria and has more than 3 semicolons
            if 'Bacteria;' in line and line.count(';') > 3:
                # Extract the family name
                if line.count(';') == 4:
                    family_field = line.strip().split(';')[4].split(',')[0]
                else:
                    family_field = line.strip().split(';')[4].split(';')[0]
                family_name = family_field.split('  ')[-1].strip().replace('"', '')

                # Add the family name to the list if it is not "unclassified"
                if family_name != "unclassified":
                    family_names.append(family_name)

    # Count the number of families and store the result in the num_families dictionary
    num_families[sample] = len(family_names)

    # Count the number of occurrences of each family and store the result in the family_counts dictionary
    family_counts[sample] = Counter(family_names)

# Create a DataFrame to store the results
results = pd.DataFrame({'Sample': samples, 'num_families': [num_families[sample] for sample in samples], 'family_counts': [family_counts[sample] for sample in samples]})

# Add a column to show the percentage of each family in the sample
results['family_percentages'] = results.apply(lambda row: ', '.join([f"{f}: {count / row['num_families'] * 100:.2f}%" for f, count in row['family_counts'].items()]), axis=1)

# Add a column to show families with percentage above 85%
results[f'families_above_{InnerPercentAbove}%'] = results.apply(lambda row: ', '.join([f"{f}: {p}" for f, p in [family_perc.split(': ') for family_perc in row['family_percentages'].split(', ') if float(family_perc.split(': ')[1][:-1]) > InnerPercentAbove]]), axis=1)

results['top_3_families'] = results.apply(lambda row: ', '.join([f"{f}" for f, count in row['family_counts'].most_common(3)]), axis=1)
# Write the results to a new CSV file
results.to_csv(f"output/AbundanceData{InnerPercentAbove}%.csv", index=False)

# Print the results
print(results.top_3_families)


