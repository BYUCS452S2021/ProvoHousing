#!/bin/bash

fn_names=('PostProvoHousing' 'GetProvoListings' 'ProvoUserLogin' 'ProvoUserRegister')
dir_names=('add_listing' 'get_listings' 'login' 'register')
# shellcheck disable=SC2164
cd dynamo_lambda_src

for ((i = 0; i < ${#dir_names[@]}; ++i)); do

  # shellcheck disable=SC2164
  cd "${dir_names[$i]}"
  zip -r "${dir_names[$i]}".zip main.py
  aws lambda update-function-code --function-name "${fn_names[$i]}" --zip-file fileb://"${dir_names[$i]}".zip
  cd ../

done
