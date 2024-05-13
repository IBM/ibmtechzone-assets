import pandas as pd
import yaml
# Define metadata
metadata = {
    'created_by': 'Diptanshu Gautam',
    'domain': 'text to SQL'
}
# Convert DataFrame to list of dictionaries
seed_examples = df.to_dict(orient='records')
# Combine metadata and seed_examples into a single dictionary
yaml_data = {
    **metadata,
    'seed_examples': seed_examples
}
# Write YAML data to a file
with open('data.yaml', 'w') as yaml_file:
    yaml.dump(yaml_data, yaml_file, default_flow_style=False)