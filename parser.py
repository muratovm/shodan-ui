import json
import pandas as pd
import re
import gzip
import json
import logging
import tkinter
from tkinter import filedialog
tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Default level (change to DEBUG for more verbosity)
    format="%(asctime)-8s | %(levelname)-8s | %(filename)-20s:%(lineno)-5d | %(funcName)-40s | %(message)s",
    datefmt="%H:%M:%S",  # Show only hours, minutes, and seconds
)

def parse_gzip_file():
    #pick file name from explorer
    file_name = filedialog.askopenfilename()

    #check file extension ends with gz
    if not file_name.endswith('.gz'):
        raise ValueError('File is not a .gz file')
    
    #parse file
    with gzip.open(file_name, 'rb') as f:
        result = [json.loads(line.decode('utf-8')) for line in f.readlines()]
        new_file_name = file_name[:-3]
        new_file_name = f"{new_file_name}.json"
        with open(new_file_name, 'w') as f:
            json.dump(result, f, indent=4)
    logging.info(f'File {file_name} has been successfully parsed and saved as {new_file_name}')
    return new_file_name

def flatten_json(input_json, parent_key='', sep='.'):
    items = {}
    # iterate over the input_json items
    for key, value in input_json.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict) and not key.startswith('CVE'):
            items.update(flatten_json(value, new_key, sep=sep))
        else:
            items[new_key] = value
    return items

# function to get the keys of a json file
def get_json_keys(input_json, parent_key='', sep='.'):
    keys = []
    for key, value in input_json.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            keys.extend(get_json_keys(value, new_key, sep=sep))
        else:
            keys.append(new_key)
    return keys

def json_to_dataframe(json_file):
    # read the json file
    with open(json_file, 'r') as f:
        data = json.load(f)
    return pd.DataFrame([flatten_json(x) for x in data])

def json_list_to_dataframe(json_list):
    #iterate over the json_list and flatten each json
    return pd.DataFrame([flatten_json(json_data) for json_data in json_list])

def search_and_save_query_results(api, query, columns_to_select, batch_size=100):
    data_df = pd.DataFrame()

    valid_file_name = re.sub(r'[^\w\-_.]','_', query)
    output_file = f'{valid_file_name}.csv'

    try:
        offset = 0
        search_results = api.search(query, limit = batch_size, offset = offset)
        results_df = json_list_to_dataframe(search_results)
        existing_columns = [col for col in columns_to_select if col in results_df.columns]
        vuln_columns = [col for col in results_df.columns if col.startswith('vulns')]
        existing_columns.extend(vuln_columns)
        save_df = results_df[existing_columns]
        data_df = pd.concat([data_df, save_df])

        num_results = len(search_results["matches"])
        total = search_results["total"]
        remaining = total - num_results
        offset
        print(f'Remaining results: {remaining}')

        while remaining > 0:
            search_results = api.search(query, limit = batch_size, offset = offset)
            num_results = len(search_results["matches"])
            remaining = total - num_results
            print(f'Remaining results: {remaining}')
            offset += num_results

            results_df = json_list_to_dataframe(search_results["matches"])
            existing_columns = [col for col in columns_to_select if col in results_df.columns]
            vuln_columns = [col for col in results_df.columns if col.startswith('vulns')]
            existing_columns.extend(vuln_columns)
            save_df = results_df[existing_columns]
            data_df = pd.concat([data_df, save_df])

    except KeyboardInterrupt:
        data_df.to_csv(output_file, index=False)
        print(f'Query results saved to {output_file}')
    
    except Exception as e:
        data_df.to_csv(output_file, index=False)
        print(f'Error: {e}')

    vuln_columns = [col for col in data_df.columns if col.startswith('vulns')]
    data_df["vuln_count"] = data_df[vuln_columns].notna().sum(axis=1)

    data_df.to_csv(output_file, mode="w", header=True, index=False)
    return data_df

def convert_json_to_graph(file_name):
    file = open(file_name, 'r')
    data = json.load(file)
    file.close()

    graph = {"nodes": [], "links": []}
    node_set = set()
    link_set = set()

    for element in data:
        #add ip_str to nodes if not already in the set
        if "ip_str" in element and element["ip_str"] not in node_set:
            graph["nodes"].append({"id": element["ip_str"], "group": 1})
            node_set.add(element["ip_str"])
        #add hostname to nodes if not already in the set
        if "hostnames" in element:
            for hostname in element["hostnames"]:
                if hostname not in node_set:
                    graph["nodes"].append({"id": hostname, "group": 2})
                    node_set.add(hostname)
                #add ip_str to hostname links if not already in the set
                if (element["ip_str"], hostname) not in link_set:
                    graph["links"].append({"source": element["ip_str"], "target": hostname, "value": 1})
                    link_set.add((element["ip_str"], hostname))
        
        #add vulnerability to nodes if not already in the set
        if "vulns" in element:
            for vuln in element["vulns"]:
                if vuln not in node_set:
                    graph["nodes"].append({"id": vuln, "group": 3, "severity": element["vulns"][vuln]["cvss"]})
                    node_set.add(vuln)
                #add ip_str to vulnerability links if not already in the set
                if (element["ip_str"], vuln) not in link_set:
                    graph["links"].append({"source": element["ip_str"], "target": vuln, "value": 1})
                    link_set.add((element["ip_str"], vuln))

        #add asn to nodes if not already in the set
        if "asn" in element:
            if element["asn"] not in node_set:
                graph["nodes"].append({"id": element["asn"], "group": 4})
                node_set.add(element["asn"])
            #add ip_str to asn links if not already in the set
            if (element["ip_str"], element["asn"]) not in link_set:
                graph["links"].append({"source": element["ip_str"], "target": element["asn"], "value": 1})
                link_set.add((element["ip_str"], element["asn"]))
    
        #add product to nodes if not already in the set
        if "product" in element: 
            if element["product"] not in node_set:
                graph["nodes"].append({"id": element["product"], "group": 5})
                node_set.add(element["product"])
            #add ip_str to product links if not already in the set
            if ("ip_str", element["product"]) not in link_set:
                graph["links"].append({"source": element["ip_str"], "target": element["product"], "value": 1})
                link_set.add((element["ip_str"], element["product"]))

    #save graph to json file
    with open('graphs/graph.json', 'w') as f:
        json.dump(graph, f, indent = 4)
    return "graph.json"
    

if __name__ == '__main__':

    while True:
        #ask if gz to json or json to graph
        print('1. Parse gz file to json')
        print('2. Convert json to graph')
        print('3. Covert gz and to graph')
        print('4. Exit')
        choice = input('Enter choice: ')

        if choice == '1':
            parsed_file = parse_gzip_file()
            logging.debug("Parsed gz file into json")

        elif choice == '2':
            parsed_file = filedialog.askopenfilename()
            convert_json_to_graph(parsed_file)
            logging.debug("Graph created")

        elif choice == '3':
            parsed_file = parse_gzip_file()
            convert_json_to_graph(parsed_file)
            logging.debug("Converted gz file to graph")
        elif choice == '4':
            exit()