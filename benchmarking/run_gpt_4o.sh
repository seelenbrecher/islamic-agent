
#!/bin/bash

# Specify the directory containing the JSON files
json_dir="./benchmarking/islam-qa-dataset/"  # Replace with the actual path

# Specify the program you want to execute
program_to_execute="benchmarking/gpt_4o_baseline.py" # Replace with the actual program name or path

# Iterate through all files in the specified directory
# for file in "$json_dir"/*; do
#   # Check if the current item is a regular file and ends with ".json"
#   if [[ -f "$file" && "$file" == *.json ]]; then
#     filename=$(basename "$file")
#     echo "Processing file: $filename"
#     # Execute the program with the current JSON file as an argument
#     python "$program_to_execute" --in_file "$file" --out_file "benchmarking/output_gpt_4o/""$filename"
#     # You can add more commands here if needed for each file
#   fi
# done

# echo "Finished processing all JSON files."

for file in "$json_dir"/*; do
  # Check if the current item is a regular file and ends with ".json"
  if [[ -f "$file" && "$file" == *.json ]]; then
    filename=$(basename "$file")
    echo "Processing file: $filename"
    # Execute the program with the current JSON file as an argument
    python "benchmarking/evaluate.py" --in_file "benchmarking/output_gpt_4o/""$filename"
    # You can add more commands here if needed for each file
  fi
done

echo "Finished processing all JSON files."