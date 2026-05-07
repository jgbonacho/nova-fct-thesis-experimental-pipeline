#!/usr/bin/env bash

# Clone and build the LFR Benchmark generator (see https://github.com/eXascaleInfolab/LFR-Benchmark_UndirWeightOvp).
echo "[INFO] Cloning LFR Benchmark generator"
git clone "https://github.com/eXascaleInfolab/LFR-Benchmark_UndirWeightOvp.git"
echo "[INFO] Building LFR Benchmark generator"
cd LFR-Benchmark_UndirWeightOvp
make
cd ..

# Define the names, parameters and instances per network.
network_family_name=""
base_network_name=""

d_avg=20
d_max=50
t1=2.0
t2=1.0
mu=0.4

c_min=0
c_max=0
n=0
on_percentage=0
om=0

t=0

# Override defaults parameters from command-line args.
for arg in "$@"; do
  eval "$arg"
done

# Create the output directory.
out_dir="./${network_family_name}"
mkdir -p "$out_dir"
cd "$out_dir"

# network_family_filename="${network_family_name}.json"
# if [ ! -f "$network_family_filename" ]; then
#   jq -n --arg name "$network_family_name" \
#     '{name: $name, networks: []}' > "$network_family_filename"
# fi

# Generate the networks.
on=$(( n * on_percentage / 100 ))

for instance in $(seq 1 "$t"); do
  instance_network_name="${base_network_name}_inst${instance}"

  # description="d_avg=${d_avg};d_max=${d_max};c_min=${c_min};c_max=${c_max};t1=${t1};t2=${t2};n=${n};mu=${mu};on=${on};om=${om}"

  # if [ "$on" -eq 0 ]; then
  #   overlapping_ground_truth=false
  # else
  #   overlapping_ground_truth=true
  # fi

  echo "[INFO] Generating LFR benchmark graph: ${instance_network_name}"
  if ! ../LFR-Benchmark_UndirWeightOvp/lfrbench_udwov \
      -N "$n" -k "$d_avg" -maxk "$d_max" -mut "$mu" -t1 "$t1" -t2 "$t2" -minc "$c_min" -maxc "$c_max" \
      -on "$on" -om "$om" \
      -name "$instance_network_name" \
      -muw "$mu"  # Required parameter, but not relevant for the experiments.
  then
    echo "[INFO] Continuing..."
    # jq \
    #   --arg nn "$instance_network_name" \
    #   --arg d "$description" \
    #   --argjson i "$instance" \
    #   --argjson ogt "$overlapping_ground_truth" \
    #   '.networks += [{
    #     description: $d,
    #     instance: $i,
    #     name: $nn,
    #     overlapping_ground_truth: $ogt
    #   }]' \
    #   "$network_family_filename" > "${network_family_filename}.new"
    # mv "${network_family_filename}.new" "$network_family_filename"
  fi
done

# Remove the LFR Benchmark generator.
echo "[INFO] Cleaning up LFR Benchmark generator"
rm -rf ../LFR-Benchmark_UndirWeightOvp

echo "[INFO] Done"
