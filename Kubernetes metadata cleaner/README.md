# YAML Kubernetes Metadata Cleaner

This Python module provides a reusable utility for cleaning Kubernetes YAML objects by removing runtime-generated metadata fields.

It is useful when exporting Kubernetes resources from a live cluster and preparing them to be reused, backed up, committed to Git, or reapplied to another cluster.

---

## What This Module Does

Kubernetes automatically adds metadata and runtime fields to resources after they are created.

These fields are usually not needed, and sometimes should not be included, when saving Kubernetes manifests for reuse.

This module removes common Kubernetes-generated fields such as:

```yaml
status
metadata.annotations
metadata.creationTimestamp
metadata.generation
metadata.resourceVersion
metadata.uid
metadata.finalizers
metadata.deletionGracePeriodSeconds
metadata.deletionTimestamp
spec.template.metadata.creationTimestamp
spec.template.metadata.annotations
```

After cleaning the object, the module returns the cleaned YAML as a string.

---

## Requirements

Python dependency:

```bash
pip install pyyaml
```

---

## How to Use

Import the `yaml_filter` class into another Python script:

```python
import yaml_filter
```

Then pass a Kubernetes resource object to `delete_fields()`:

```python
clean_yaml = yaml_filter.delete_fields(resource_data)
```

Example:

```python
import yaml
import yaml_filter

with open("deployment.yaml", "r") as file:
    data = yaml.safe_load(file)

cleaned_yaml = yaml_filter.delete_fields(data)

with open("cleaned-deployment.yaml", "w") as file:
    file.write(cleaned_yaml)
```

---

## Example Input

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: default
  creationTimestamp: "2026-01-01T10:00:00Z"
  resourceVersion: "123456"
  uid: "abc-123"
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: "..."
spec:
  replicas: 2
status:
  availableReplicas: 2
```

---

## Example Output

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: default
spec:
  replicas: 2
```

---

## Why This Is Useful

When running commands like:

```bash
kubectl get deployment my-app -o yaml
```

Kubernetes returns the full live state of the object, including metadata that belongs to the cluster itself.

If you want to reuse that YAML later, these fields should usually be removed first.

This utility helps convert live Kubernetes YAML into cleaner, reusable manifests.

---

## Can Be Used With Any Kubernetes Resource

Although this was created for cleaning Kubernetes manifests, it can be used with basically any Kubernetes resource, including:

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
custom resources
```

It is especially useful when combined with scripts that export resources using `kubectl`.

---

## Customizing Deleted Fields

The list of deleted fields is defined inside the class:

```python
fields_to_delete = [
    ["status"],
    ["metadata", "annotations"],
    ["metadata", "creationTimestamp"],
    ["metadata", "generation"],
    ["metadata", "resourceVersion"],
    ["metadata", "uid"],
    ["metadata", "finalizers"],
    ["metadata", "deletionGracePeriodSeconds"],
    ["metadata", "deletionTimestamp"],
    ["spec", "template", "metadata", "creationTimestamp"],
    ["spec", "template", "metadata", "annotations"]
]
```

Each item represents a path inside the YAML structure.

For example:

```python
["metadata", "uid"]
```

removes:

```yaml
metadata:
  uid: ...
```

And:

```python
["spec", "template", "metadata", "annotations"]
```

removes:

```yaml
spec:
  template:
    metadata:
      annotations: ...
```

You can add or remove paths depending on the resource type you are working with.

---

## Example Integration With Kubectl Exporter

This module can be used inside a larger Kubernetes export script.

Example flow:

```python
import os
import yaml
from yaml_filter import yaml_filter

yaml_output = os.popen("kubectl get deployment my-app -n default -o yaml").read()
resource_data = yaml.safe_load(yaml_output)

cleaned_yaml = yaml_filter.delete_fields(resource_data)

with open("my-app.yaml", "w") as file:
    file.write(cleaned_yaml)
```

---

## Possible Improvements

Future improvements could include:

* Renaming the class to `YamlFilter` to follow Python naming conventions.
* Adding `@staticmethod` above `delete_fields()`.
* Using logging instead of `print()`.
* Returning the cleaned dictionary instead of only returning YAML text.
* Supporting command-line usage.
* Adding unit tests.
* Adding resource-specific cleanup profiles.
* Adding support for cleaning multiple YAML documents in one file.

---

## Summary

This module provides a simple reusable way to clean Kubernetes YAML files by removing cluster-generated metadata.

It is useful for backup scripts, GitOps workflows, Kubernetes migrations, and exporting live resources into clean manifests.
