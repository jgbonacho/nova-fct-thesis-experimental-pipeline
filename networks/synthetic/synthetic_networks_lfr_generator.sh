#!/usr/bin/env bash

# Clone and build the LFR Benchmark generator (see https://github.com/eXascaleInfolab/LFR-Benchmark_UndirWeightOvp).
echo "[INFO] Cloning LFR Benchmark generator"
git clone "https://github.com/eXascaleInfolab/LFR-Benchmark_UndirWeightOvp.git"
echo "[INFO] Building LFR Benchmark generator"
cd LFR-Benchmark_UndirWeightOvp
make
cd ..

# Set the name of the network family.
network_family_name="example_network_family"

# Define the parameters for the graphs.
list_d_avg=(20)
list_d_max=(50)
list_c_min=(20)
list_c_max=(100)
list_t1=(2.0)
list_t2=(1.0)

list_n=(100)
list_mu=(0.1)
list_on_percentages=(10)
list_om=(2)

# Set the number of instances per network.
t=1

# Override defaults parameters from command-line args.
for arg in "$@"; do
  eval "$arg"
done

# Create the output directory.
out_dir="./${network_family_name}"
mkdir -p "$out_dir"
cd "$out_dir"

#network_family_filename="${network_family_name}.json"
#jq -n --arg name "$network_family_name" '{name: $name, networks: []}' > "$network_family_filename"

# Loop over the parameter combinations and run the generator.
for d_avg in "${list_d_avg[@]}"; do
  for d_max in "${list_d_max[@]}"; do
    for c_min in "${list_c_min[@]}"; do
      for c_max in "${list_c_max[@]}"; do
        for t1 in "${list_t1[@]}"; do
          for t2 in "${list_t2[@]}"; do
            for n in "${list_n[@]}"; do
              for mu in "${list_mu[@]}"; do
                for on_percentage in "${list_on_percentages[@]}"; do
                  on=$(( n * on_percentage / 100 ))
                  for om in "${list_om[@]}"; do
                    for instance in $(seq 1 "$t"); do
                      network_name="n${n}mu${mu}on${on}om${om}inst${instance}"
                      #description="d_avg=${d_avg};d_max=${d_max};c_min=${c_min};c_max=${c_max};t1=${t1};t2=${t2};n=${n};mu=${mu};on=${on};om=${om}"

                      #if [ "$on" -eq 0 ]; then
                      #  overlapping_ground_truth=false
                      #else
                      #  overlapping_ground_truth=true
                      #fi

                      echo "[INFO] Generating LFR benchmark graph: ${network_name}"
                      if ! ../LFR-Benchmark_UndirWeightOvp/lfrbench_udwov \
                          -N "$n" -k "$d_avg" -maxk "$d_max" -mut "$mu" -t1 "$t1" -t2 "$t2" -minc "$c_min" -maxc "$c_max" \
                          -on "$on" -om "$om" \
                          -name "$network_name" \
                          -muw "$mu"  # Required parameter, but not relevant for the experiments.
                      then
                        echo "[INFO] Continuing..."
                        #jq \
                        #  --arg nn "$network_name" \
                        #  --arg d "$description" \
                        #  --argjson i "$instance" \
                        #  --argjson ogt "$overlapping_ground_truth" \
                        #  '.networks += [{
                        #    description: $d,
                        #    instance: $i,
                        #    name: $nn,
                        #    overlapping_ground_truth: $ogt
                        #  }]' \
                        #  "$network_family_filename" > "${network_family_filename}.new"
                        #mv "${network_family_filename}.new" "$network_family_filename"
                      fi
                    done
                  done
                done
              done
            done
          done
        done
      done
    done
  done
done

# Remove the LFR Benchmark generator.
echo "[INFO] Cleaning up LFR Benchmark generator"
rm -rf ../LFR-Benchmark_UndirWeightOvp

echo "[INFO] Done"
