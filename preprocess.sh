pip install --no-cache-dir -r requirements.txt

# Get arguments from command line
input_video="$1"
temp_dir="$2"
interval="$3"
output_dir="$4"

#strip away quotes, itill cause EOF error
input_video="${input_video//\"/}"
temp_dir="${temp_dir//\"/}"
output_dir="${output_dir//\"/}"

python makeup7.py --all="$input_video,$temp_dir,$interval,$output_dir"