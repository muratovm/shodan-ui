from shodan import Shodan
import pandas as pd
import re
import json
import yaml
import logging


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Default level (change to DEBUG for more verbosity)
    format="%(asctime)-8s | %(levelname)-8s | %(filename)-20s:%(lineno)-5d | %(funcName)-40s | %(message)s",
    datefmt="%H:%M:%S",  # Show only hours, minutes, and seconds
)

# Setup the API
class ShodanAPI:
    def __init__(self):
        #set the api key
        if not self.get_key_from_config():
            self.api_key = input('Enter your Shodan API key: ')
            self.save_api_key()
        logging.info(f"Using API key: {self.api_key[:4]}... ")
        self.api = Shodan(self.api_key)
        logging.info("Shodan API initialized")

    def get_key_from_config(self):
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            if config and 'api_key' in config:
                self.api_key = config['api_key']
                logging.debug('API key loaded from config.yaml')
                return True
            else:
                logging.debug('API key not found in config.yaml')
        return False


    def save_api_key(self):
        with open('config.yaml', 'w') as f:
            f.write(f'api_key: {self.api_key}')
            logging.debug('API key saved to config.yaml')
    
    def search(self, query):
        try:
            # Search Shodan
            results = self.api.search(query)
            total = results['total']
            results = results['matches']
            logging.debug(f'Pulled in {len(results)} results')
            return results, total
        except Exception as e:
            return e
        
    def search_and_save_query_results(self, query, columns_to_select=None, batch_size=100) -> list:
        # If no columns are specified, select all columns
        valid_file_name = re.sub(r'[^\w\-_.]','_', query)
        logging.debug(f"File name: {valid_file_name}")
        try:
            offset = 0
            search_results, total = self.search(query)
            if type(search_results) != list:
                logging.error(search_results)
                return None
            remaining = total - len(search_results)
            logging.debug(f'Total results: {total}')
            logging.debug(f'Remaining results: {remaining}')

            while remaining > 0:
                additional_results, total = self.search(query)
                #append results
                search_results += additional_results

                num_results = len(search_results)
                remaining = remaining - num_results
                logging.debug(f'Remaining results: {remaining}')
                offset += num_results

            data = []

            #filter columns
            if columns_to_select:
                for result in search_results:
                    #filter single dict result
                    filtered_result = {k: result[k] for k in columns_to_select if k in result}
                    data.append(filtered_result)
            else:
                data = search_results

            #save data as json file
            with open(f'data/{valid_file_name}.json', 'w') as f:
                json.dump(data, f, indent=4)
                logging.debug(f'Query results saved to data/{valid_file_name}.json')
        except Exception as e:
            logging.error(f'Error saving query results: {e}')
            return None
        
        return data

    def convert_json_to_dataframe(self, json_file) -> pd.DataFrame:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                logging.debug(f'Converted {json_file} to DataFrame')
                return df
        except Exception as e:
            logging.error(f'Error converting {json_file} to DataFrame: {e}')
            return None

if __name__ == "__main__":
    shodan_api = ShodanAPI()

    query = "org:'Clearpool'"
    #columns_to_select = ['ip_str', 'port', 'org', 'data', 'vulns']

    shodan_api.search_and_save_query_results(query)