#!/bin/bash

fn_names=('ProvoUserLogin' 'ProvoUserRegister' 'PostProvoHousing')
dir_names=('login' 'register' 'add_listing')
# shellcheck disable=SC2164
cd dynamo_lambda_src

for ((i = 0; i < ${#dir_names[@]}; ++i)); do

  # shellcheck disable=SC2164
  cd "${dir_names[$i]}"
  zip -r "${dir_names[$i]}".zip main.py
  aws lambda update-function-code --function-name "${fn_names[$i]}" --zip-file fileb://"${dir_names[$i]}".zip
  cd ../

done


# shellcheck disable=SC2164
cd get_listings
zip -r get_listings.zip main.py dependencies/
aws lambda update-function-code --function-name "GetProvoListings" --zip-file fileb://"get_listings".zip
cd ../
