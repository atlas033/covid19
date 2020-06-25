 #!/bin/bash

declare -a arr=(
"switzerland"
"france"
"germany"
)

# OTHER (TOP 10 by Population)

# "russia"
# "germany"
# "turkey"
# "france"
# "united kingdom" @test link
# "italy"
# "spain"
# "ukraine"
# "poland" @test link
# "romania @test link

# "switzerland"
# "sweden"

base="./data/reparam_2R/"

# model="country.reparam_2R.sir_int.tnrm"
# model="country.reparam_2R.seir_int.tnrm"
model="country.reparam_2R.seiir_int.tnrm"


# model="country.reparam.sir_int.nbin"
# model="country.reparam.sir_int_nogamma.nbin"
# model="country.reparam.seir_int.nbin"
# model="country.reparam.seir_int_nogamma.nbin"
# model="country.reparam.seir_int_nogamma_noZ.nbin"
# model="country.reparam.seiir_int.nbin" 
# model="country.reparam.seiir_int_nogamma.nbin" 
# model="country.reparam.seiir_int_nogamma_noZ.nbin" 

# model="country.reparam.sir_int.tnrm"
# model="country.reparam.sir_int_nogamma.tnrm"
# model="country.reparam.seir_int.tnrm"
# model="country.reparam.seir_int_nogamma.tnrm"
# model="country.reparam.seir_int_nogamma_noZ.tnrm"
# model="country.reparam.seiir_int.tnrm"
# model="country.reparam.seiir_int_nogamma.tnrm"
model="country.reparam.seiir_int_nogamma_noZ.tnrm"

# model="country.reparam.sir_intexp.tnrm"
# model="country.reparam.sir_intrem.tnrm"
# model="country.reparam.seir_intexp.tnrm"
# model="country.reparam.seir_intrem.tnrm"
# model="country.reparam.seiir_intexp.tnrm"
# model="country.reparam.seiir_intrem.tnrm"


mkdir ${base} -p

for c in "${arr[@]}"
do
   outfile="${base}/knested_${c}_${model}.out"
   time PYTHONPATH=../..:../../build:$PYTHONPATH python sample_knested.py --silentPlot -ns 1500 -cm ${model} -c "$c" -df $base | tee ${outfile}

   folder="$base/$c/$model"
   python3 -m korali.plotter --dir "$folder/_korali_samples"  --output "$folder/figures/samples.png"
done
