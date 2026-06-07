#The following tools are required in your running shell:
#Kubectl


import os
import yaml

#VARIABLES:
PATH_POD = "./VictoriaMetrics_Scrapes_Exporter/Pod"
PATH_SERVICE = "./VictoriaMetrics_Scrapes_Exporter/Service"
KUBECTL_ARGS ="--output=custom-columns=NAME:.metadata.name --no-headers"
#Fetching namespaces
def get_namespaces():
    NAMESPACES = os.popen(f"kubectl get namespaces {KUBECTL_ARGS}").read()
    NAMESPACES_LIST = NAMESPACES.strip().split('\n')
    return NAMESPACES_LIST


#Converting to K8S
def YAML_2_K8S(file):
    if 'status' in file:
        del file['status']
    else:
        pass
    if 'creationTimestamp' in file['metadata']:
                    del file['metadata']['creationTimestamp']
    else:
        pass
    if 'generation' in file['metadata']:
        del file['metadata']['generation']
    

    if 'annotations' in file['metadata']:
        del file['metadata']['annotations']

    else:
        pass
    if 'resourceVersion' in file['metadata']:
        del file['metadata']['resourceVersion']
    else:
        pass
    if 'uid' in file['metadata']:
        del file['metadata']['uid']
    else:
        pass
    if 'spec' in file and 'template' in file['spec'].get('template', {}).get('metadata', {}):
        del file['spec']['template']['metadata']['annotations'] 
    else:
        pass
    if 'spec' in file and 'template' in file['spec'].get('template', {}).get('metadata', {}):
        del file['spec']['template']['metadata']['creationTimestamp']  
    else:
        pass

#Fetching Podscrapes
def get_podscrapes():

    #Checks whether the directories in the paths above exist or not
    if not os.path.isdir(PATH_POD):
        os.makedirs(PATH_POD)

    for namespace in get_namespaces():
        #Checks whether the current namespace has any objects in it or not
        Namespace_check = os.popen(f"kubectl get vmpodscrapes -n {namespace} {KUBECTL_ARGS}").readlines()  
        #Skips the namespaces in which there aren't any objects and executes the scraping procedure
        if Namespace_check:
            print(Namespace_check) 
            PODSCRAPES = os.popen(f"kubectl get vmpodscrapes -n {namespace} {KUBECTL_ARGS}").read()
            podscrapes_list = PODSCRAPES.strip().split('\n')
            #DIR = f"{PATH_POD}/{namespace}"
            #os.mkdir(DIR)
            os.makedirs(f"{PATH_POD}/{namespace}")
            for vmpodscrape in podscrapes_list:
                
                print(f"the current scrpae is: {vmpodscrape}")
                FILE = f"{PATH_POD}/{namespace}/{vmpodscrape}.yaml"
                #os.system(f"kubectl get vmpodscrape {vmpodscrape} -n {namespace} {KUBECTL_ARGS} -o yaml > {FILE}")
                yaml_file = os.popen(f"kubectl get vmpodscrape {vmpodscrape} -n {namespace} {KUBECTL_ARGS} -o yaml").read()
                yaml_to_k8s= yaml.load(yaml_file)
                YAML_2_K8S(yaml_to_k8s)  
                with open(FILE, 'w') as new_yaml:
                    yaml.dump(yaml_to_k8s, new_yaml, default_flow_style=False)         
                print(f"vmpodscrape:{vmpodscrape}, Namespace:{namespace} in {FILE}")


#Fetching service scrapes
def get_servicesscrapes():

    #Checks whether the directories in the paths above exist or not
    if not os.path.isdir(PATH_SERVICE):
        os.makedirs(PATH_SERVICE)

    for namespace in get_namespaces():
        #Checks whether the current namespace has any objects in it or not
        Namespace_check = os.popen(f"kubectl get vmservicescrapes -n {namespace} {KUBECTL_ARGS}").readlines()  
        #Skips the namespaces in which there aren't any objects and executes the scraping procedure
        if Namespace_check:
            print(Namespace_check) 
            SERVICESCRAPES = os.popen(f"kubectl get vmservicescrapes -n {namespace} {KUBECTL_ARGS}").read()
            Servicescrapes_list = SERVICESCRAPES.strip().split('\n')
            #DIR = f"{PATH_POD}/{namespace}"
            #os.mkdir(DIR)
            os.makedirs(f"{PATH_SERVICE}/{namespace}")
            for vmservicescrape in Servicescrapes_list:
            
                FILE = f"{PATH_SERVICE}/{namespace}/{vmservicescrape}.yaml"
                #os.system(f"kubectl get vmservicescrape {vmservicescrape} -n {namespace} {KUBECTL_ARGS} -o yaml > {FILE}")
                yaml_file = os.popen(f"kubectl get vmservicescrape {vmservicescrape} -n {namespace} {KUBECTL_ARGS} -o yaml").read()
                yaml_to_k8s= yaml.load(yaml_file)
                YAML_2_K8S(yaml_to_k8s)  
                with open(FILE, 'w') as new_yaml:
                    yaml.dump(yaml_to_k8s, new_yaml, default_flow_style=False)    
                print(f"vmservicesscrape:{vmservicescrape}, Namespace:{namespace} in {FILE}")



def main():
    
    get_podscrapes()
    print("PODS DONE!")
    get_servicesscrapes()
    print("SERVICES DONE!")


if __name__ == "__main__":
   main()