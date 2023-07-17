from databricks import sql
import os
import logging
from pathlib import Path
import argparse
import pandas as pd
from time import sleep
import sys

from codeoceansdk.CodeOcean import CodeOcean
from codeoceansdk.Capsule import Capsule, OriginalCapsuleInfo, UserPermission, EveryonePermission
from codeoceansdk.DataAsset import DataAsset, ComputationSource

logger = logging.getLogger(__name__)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description='Databricks SQL Connector')
    parser.add_argument('--hostname', required=True, help="Connections Details - Hostname", type=str)
    parser.add_argument('--httppath', required=True, help="Connections Details - HTTPPath", type=str)
    parser.add_argument('--catalog', required=True, help="Catalog Name", type=str)
    parser.add_argument('--SQLQuery', required=True, help="Provide your SQL Query", type=str)
    parser.add_argument('--file_name', default='output', help="Output file name.", type=str)
    parser.add_argument('--output_format', default='csv', help="Output format", choices=['csv', 'tsv','parquet','json','excel'], type=str)
    parser.add_argument("--data_asset_name", required=True, help="Data asset name", type=str)
    parser.add_argument("--data_asset_folder", required=True, help="Folder name for data asset", type=str) 
    parser.add_argument("--data_asset_tags", required=True, help="Colon delimited list of tags to use for the data asset", type=str)
    parser.add_argument("--domain", required=True, help="Code Ocean domain", type=str)
    parser.add_argument("--databricks_query", required=True, help="ID of Query Capsule", type=str)
    parser.add_argument("--timeout", required=True, help="Timeout in Seconds", type=int)

    args = parser.parse_args()

    capsule = Capsule(id=args.databricks_query, 
                      domain=args.domain, 
                      api_key=os.environ['API_SECRET'])

    parameters = [args.hostname, 
                  args.httppath, 
                  args.catalog, 
                  args.SQLQuery, 
                  args.file_name, 
                  args.output_format]                  

    countdown = args.timeout
    logger.info(f"Launching query: {args.SQLQuery}")
    computation = capsule.run_capsule_computation(parameters)

    while(countdown > 0 and computation.state != "completed"): 
        computation.get_computation()
        sleep(5) #poll every five seconds
        countdown -= 5

    logger.debug(computation)

    if computation.end_status != "succeeded": 
        logger.error(f"Query failed! State: {computation.state}")
        return 1
    
    if not computation.has_results: 
        logger.error(f'No result file generated!')
        return 1

    data_asset = DataAsset.create_data_asset(name=args.data_asset_name, 
                                            tags=args.data_asset_tags.split(':'), 
                                            data_source=ComputationSource(id=computation.id), 
                                            mount=args.data_asset_folder, 
                                            environment=CodeOcean(api_key=os.environ['API_SECRET'],
                                            domain=args.domain))
    
    countdown = args.timeout
    while (countdown > 0 and data_asset.state == "draft"): 
        data_asset.get_data_asset()
        sleep(5) #poll every five seconds
        countdown -= 5
    
    if data_asset.state != "ready":
        logger.error(f"Data asset creation failed! {data_asset.state}")
        return 1
    
    logger.info(f"Data asset creation successful. Metadata id: {data_asset.id}")

    return 0


if __name__ == '__main__':
    sys.exit(main())