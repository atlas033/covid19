 #!/bin/bash

msg="1 ppm, informed priors, init"
pushd ..

source countries.sh

name=`whoami`
base="/scratch/${name}/covid19/intervention/data/g9"

declare -a models=(
#"country.reparam.seirud_int.poi"
"country.reparam.seirud_int.geo"
#"country.reparam.seirud_int.nbin"
#"country.reparam.seirud_int.tnrm"
#"country.reparam.seirud_int.tstudent_alt"
)

mkdir ${base} -p

for model in "${models[@]}"
do
    for c in "${countries[@]}"
    do
        folder=$base/$c/$model
        mkdir -p "${folder}"

        outfile=${folder}/knested.out
        time PYTHONPATH=../..:../../build:$PYTHONPATH python sample_knested.py \
            --silentPlot -ns 1500 -dlz 0.1 -cm ${model} -c "$c" -ui -ud -uip -uint -bs 8 -nt 8 -df $base -m "${msg}" \
            2>&1 | tee "${outfile}"

        python3 -m korali.plotter --dir "$folder/_korali_samples"  --output "$folder/figures/samples.png"
        
        #rm -r "$folder/_korali_propagation"

        done
done

popd
