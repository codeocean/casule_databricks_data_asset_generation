#!/bin/bash

source ./config.sh

python runBricks.py --hostname "$hostname" \
             --httppath "$httppath" \
             --catalog "$catalog" \
             --SQLQuery "$SQL_query" \
             --file_name "$file_name" \
             --output_format "$output_format" \
             --data_asset_name "$data_asset_name" \
             --data_asset_folder "$folder_name" \
             --data_asset_tags "$tags" \
             --domain "$domain" \
             --databricks_query "$databricks_query" \
             --timeout "$max_execution_time" 
