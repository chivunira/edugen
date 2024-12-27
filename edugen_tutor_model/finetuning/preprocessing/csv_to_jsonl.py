import os
import pandas as pd
import json

# Set the directory containing the CSV files
csv_dataset_file = os.path.join(os.path.dirname(__file__), '../dataset/unprocessed/Augmented_AI_Tutor_Dataset.csv')
output_jsonl_file = os.path.join(os.path.dirname(__file__), '../dataset/processed/dataset.jsonl')


# Convert the combined CSV file into a JSONL file
def csv_to_jsonl(input_file, output_file):
    data = pd.read_csv(input_file)
    with open(output_file, 'w') as jsonl_file:
        for record in data.to_dict(orient='records'):
            jsonl_file.write(json.dumps(record) + '\n')
    print(f'JSONL file saved to {output_file}')


# Call the function with the directory path as the argument
csv_to_jsonl(csv_dataset_file, output_jsonl_file)

