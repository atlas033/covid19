 #!/bin/bash

declare -a countries=(
"china"
"switzerland"
"france"
"germany"
"italy"
"russia"
"us"
"sweden"
"brazil"
"india"
)

base="./data/test3i0/"

#model="country.cz_int.nbin"
#model="country.reparam.sird_dint.tstudent"
#model="country.reparam.sird_dint.tstudent_alt"
#model="country.reparam.sird_dint.poi"
#model="country.reparam.sird_dint.geo"
#model="country.reparam.sird_dint.tnrm"
#model="country.reparam.sird_dint.nbin"
#model="country.reparam.seird_dint.nbin"
#model="country.reparam.seird_int.nbin"
#model="country.reparam.seiird_dint.nbin"
#model="country.reparam.seiird_int.nbin"
#model="country.reparam.seiird2_int.nbin"
model="country.reparam.seiird2_dint.nbin"

mkdir ${base} -p

for c in "${countries[@]}"
do
    folder="$base/$c/$model"
    mkdir ${folder} -p

    outfile="${folder}/knested.out"
    time PYTHONPATH=../..:../../build:$PYTHONPATH python sample_knested.py \
        --silentPlot -ns 1500 -cm ${model} -c "$c" -ui -ud -df $base 2>&1 | tee ${outfile}

    python3 -m korali.plotter --dir "$folder/_korali_samples"  --output "$folder/figures/samples.png"
done
