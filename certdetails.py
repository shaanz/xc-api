import requests
import json 
import csv 

#User defined variables 
#auth_token = 'APIToken APITOKEN'
#tenant_name = 'TENANT-NAME'
cert_exp_file = "certlist.csv"


#DEfine Global Variables 
list = ""

url_ns= 'https://' + tenant_name +'.console.ves.volterra.io/api/web/namespaces'
url_lb_ns = 'https://' + tenant_name +'.console.ves.volterra.io/api/config/namespaces/'

#add authorization headers to API Calls
headers = {
        'Authorization' : auth_token,
        'Content-Type': 'application/json'  # adjust content type as needed
    }

#function to get all namespaces 
def get_all_namespaces(url_ns, auth_token):
    try:
        response = requests.get(url_ns, headers=headers)
        if response.status_code == 200:
            # API call successful, return response content
            return response.json()
        else:
            # API call failed, print error message
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        # Exception occurred during API call
        print(f"Exception: {e}")
        return None
    
#function to get LB details in a namespace 
def get_lb(url_lb_ns, auth_token,ns):
    try:
        url_lb_ns1 = url_lb_ns+ ns +'/http_loadbalancers'
        response = requests.get(url_lb_ns1, headers=headers)
        if response.status_code == 200:
            # API call successful, return response content
            return response.json()
        else:
            # API call failed, print error message
            return None
    except requests.exceptions.RequestException as e:
        # Exception occurred during API call
        print(f"Exception: {e}")
        return None

# function to get certificate details of a lb 
def get_cert_expiry(url_lb_ns, auth_token,lb_name,ns):
   
    try:
        #lb_url = url_lb +"/"+ lb_name
        lb_url = url_lb_ns+ ns +'/http_loadbalancers'+"/"+ lb_name
        response = requests.get(lb_url, headers=headers)
        response_data = response.json()
        if response.status_code == 200:
            # API call successful, return response content
            spec = response_data['spec']
            auto_cert_info = spec['auto_cert_info']
            cert_expiry= auto_cert_info['auto_cert_expiry']
            return cert_expiry
        else:
            # API call failed, print error message
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        # Exception occurred during API call
        print(f"Exception: {e}")
        return None
    
#function to write the list to a file 
def write_to_file(list):
    try:
        with open(cert_exp_file, "w") as file:
            file.write(list)
    except Exception as e:
        print('Error writing to file',e)

# Code to invoke config 
try:    
    namespaces = get_all_namespaces(url_ns,auth_token)
    if namespaces:
        ns_list = namespaces['items']
        for ns in ns_list:
            nsid = ns['name']
            print (" Pulling Details For Namespace: " + nsid)
            lb_data = get_lb(url_lb_ns, auth_token,nsid)
            if lb_data:
                items = lb_data['items']
                if not items :
                    # print("No LB in namespace")
                    continue

                for item in items:
                    lb_name = item['name']
                    list = list + lb_name + ","
                    print("\n Getting details for LB:", lb_name)
                    cert_expiry = get_cert_expiry(url_lb_ns,auth_token,lb_name,nsid)
                    if (cert_expiry!=None):
                        list = list + cert_expiry + "\n\r"
                    else: 
                        list = list + " \n\r"
            else:
                print("No LB in namespace")
    print(list)    
    write_to_file(list)
               
except Exception as e:
    print("Cert Details Export Failed:", e)
