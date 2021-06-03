#!/bin/bash

fn_names=('PostProvoHousing' 'GetProvoListings' 'ProvoUserLogin' 'ProvoUserRegister' 'ProvoUserLogout' 'WatchProvoHousing' 'UpdateProvoListing')
dir_names=('add_listing' 'get_listings' 'login' 'register' 'logout' 'watch' 'update_listing')

for ((i = 0; i < ${#dir_names[@]}; ++i)); do

  # shellcheck disable=SC2164
  cd "${dir_names[$i]}"
  zip -r "${dir_names[$i]}".zip dependencies/ main.py
  aws lambda update-function-code --function-name "${fn_names[$i]}" --zip-file fileb://"${dir_names[$i]}".zip
  cd ../

done
