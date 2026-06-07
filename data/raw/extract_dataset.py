import itertools

input_file = r'd:\Projects\Research\serverless-research\data\raw\mock_dataset_all.csv'
output_file = r'd:\Projects\Research\serverless-research\data\raw\mock_dataset_100k_110k.csv'

with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8', newline='') as f_out:
    # Read and write the header
    header = f_in.readline()
    f_out.write(header)
    
    # We want data rows 100000 to 110000 (inclusive)
    # Since we already read 1 line (the header), the next line is index 0 in the remaining lines.
    # Data row 1 is index 0.
    # Data row 100000 is index 99999.
    # Data row 110000 is index 109999.
    # islice stops at `stop`, so we use 110000 to include 109999.
    for line in itertools.islice(f_in, 99999, 110000):
        f_out.write(line)

print("Extraction complete. Saved to", output_file)
