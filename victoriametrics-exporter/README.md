# Kubernetes Resource YAML Exporter

This Python script exports Kubernetes resources from all namespaces into clean YAML files that can be reused, versioned, backed up, or reapplied to another cluster.

The current implementation exports VictoriaMetrics scrape resources:

* `VMPodScrape`
* `VMServiceScrape`

However, the same logic can be adapted to basically any Kubernetes resource, including Deployments, Services, ConfigMaps, Secrets, Ingresses, CRDs, or other custom resources.

---

## What the Script Does

The script:

1. Fetches all namespaces from the current Kubernetes cluster.
2. Checks each namespace for existing `vmpodscrapes` and `vmservicescrapes`.
3. Exports each resource as a YAML file.
4. Removes cluster-generated fields that should not usually be reused.
5. Saves the cleaned YAML files into namespace-based folders.

This is useful for backing up Kubernetes resources or converting live cluster objects into reusable manifests.

---

## Requirements

The following tools are required in your running shell:

```bash
kubectl
```

Python dependencies:

```bash
pip install pyyaml
```

You must also have access to a Kubernetes cluster through your current `kubectl` context.

Check your current context with:

```bash
kubectl config current-context
```

---

## Project Structure

Expected output structure:

```bash
VictoriaMetrics_Scrapes_Exporter/
├── Pod/
│   └── <namespace>/
│       └── <vmpodscrape-name>.yaml
└── Service/
    └── <namespace>/
        └── <vmservicescrape-name>.yaml
```

Example:

```bash
VictoriaMetrics_Scrapes_Exporter/
├── Pod/
│   └── monitoring/
│       └── node-exporter.yaml
└── Service/
    └── monitoring/
        └── victoria-metrics.yaml
```

---

## How to Run

Run the script from your terminal:

```bash
python3 exporter.py
```

The script will:

* Scan all namespaces.
* Export existing `VMPodScrape` resources.
* Export existing `VMServiceScrape` resources.
* Save the cleaned YAML files locally.

---

## How It Works

### Fetching namespaces

The script first fetches all Kubernetes namespaces:

```bash
kubectl get namespaces --output=custom-columns=NAME:.metadata.name --no-headers
```

It then loops over each namespace and checks whether the target resources exist there.

---

### Exporting resources

For each discovered resource, the script runs a command similar to:

```bash
kubectl get vmpodscrape <resource-name> -n <namespace> -o yaml
```

or:

```bash
kubectl get vmservicescrape <resource-name> -n <namespace> -o yaml
```

The YAML output is loaded into Python, cleaned, and written into a local file.

---

## YAML Cleanup

Kubernetes automatically adds runtime metadata to live resources. These fields are usually not needed when saving manifests for reuse.

The script removes fields such as:

```yaml
status
metadata.creationTimestamp
metadata.generation
metadata.annotations
metadata.resourceVersion
metadata.uid
```

This makes the exported YAML cleaner and more suitable for reapplying with:

```bash
kubectl apply -f <file>.yaml
```

---

## Adapting This Script for Any Kubernetes Resource

Although this script currently exports VictoriaMetrics scrape resources, the same pattern can be reused for basically any Kubernetes resource.

For example, to export Deployments instead of `VMPodScrapes`, you would replace:

```bash
kubectl get vmpodscrapes
```

with:

```bash
kubectl get deployments
```

And replace:

```bash
kubectl get vmpodscrape <name>
```

with:

```bash
kubectl get deployment <name>
```

This approach can be used for resources such as:

```bash
deployments
services
configmaps
secrets
ingresses
statefulsets
daemonsets
cronjobs
serviceaccounts
roles
rolebindings
customresourcedefinitions
```

It can also be used for custom resources, as long as they are available through `kubectl get`.

---

## Example Use Cases

This script can be useful for:

* Backing up Kubernetes resources.
* Exporting CRDs from a live cluster.
* Migrating resources between clusters.
* Creating GitOps-ready YAML files from existing resources.
* Auditing Kubernetes resources across namespaces.
* Saving VictoriaMetrics scrape configurations.
* Building reusable infrastructure manifests.

---

## Important Notes

The script uses the currently active `kubectl` context. Make sure you are connected to the correct cluster before running it.

Check the active context:

```bash
kubectl config current-context
```

If needed, switch context:

```bash
kubectl config use-context <context-name>
```

The user running the script must have permissions to list namespaces and read the target resources in each namespace.

---

## Possible Improvements

Future improvements could include:

* Adding command-line arguments for resource type and output path.
* Supporting multiple resource types dynamically.
* Adding error handling for missing permissions.
* Using `subprocess` instead of `os.popen`.
* Skipping folders that already exist.
* Adding support for cluster-scoped resources.
* Adding logging instead of simple `print()` statements.

---

## Summary

This script exports Kubernetes resources from all namespaces and converts them into cleaner YAML files that can be reused or stored in Git.

While it currently focuses on VictoriaMetrics scrape resources, the logic is generic and can be adapted to almost any Kubernetes resource.
