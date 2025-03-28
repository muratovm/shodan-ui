import xml.etree.ElementTree as ET
import json
import pandas as pd
import requests
import time
import urllib3
import gzip
urllib3.disable_warnings()

from parser import *

def sumarize_technologies(file_name):
    tech = []
    json_object = json.load(open(file_name))
    for log in json_object:
        if 'http' in log and "components" in log['http']:
            for technology in log['http']['components']:
                data = log['http']['components'][technology]
                tech_results = {}
                tech_results['technology'] = technology
                tech_results['categories'] = ",".join(data.get('categories'), [])
                tech.append(tech_results)
    tech_df = pd.DataFrame(tech, columns=["technology", "categories"])
    return tech_df

def sumarize_vulnerabilities(file_name):
    vulns = []
    json_object = json.load(open(file_name))
    for log in json_object:
        if 'vulns' in log:
            for cve_id in log['vulns']:
                data = log['vulns'][cve_id]
                vuln_results = {}
                vuln_results['CVE'] = cve_id
                vuln_results['IP'] = data.get("ip_str")
                vuln_results['Product'] = data.get("product")
                vuln_results['CVSS'] = data.get("cvss")
                vuln_results['EPSS'] = data.get("ranking_epss")
                vuln_results['Verified'] = data.get("verified")
                vulns.append(vuln_results)
    vulns_df = pd.DataFrame(vulns, columns=["CVE", "IP", "Product", "CVSS", "EPSS", "Verified"])
    return vulns_df

def summarize_domains(file_name):
    heartbleed_ips = []
    with open(file_name, "r") as file:
        json_object = json.load(file)
        for log in json_object:
            if 'http' in log and "heartbleed" in log['http']:
                data = log['http']['heartbleed']
                heartbleed_ips.append(data)