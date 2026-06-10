#!/usr/bin/env python
import yaml

# Define fields to delete
class yaml_filter:
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

    def delete_fields(data, fields_to_delete=None):
        if fields_to_delete is None:
            fields_to_delete = yaml_filter.fields_to_delete
        for field_path in fields_to_delete:
            try:
                # Navigate through the nested structure
                current_level = data
                for key in field_path[:-1]:  # Traverse to the second-to-last key
                    current_level = current_level.get(key, {})
                    
                # Delete the last key in the path if it exists
                current_level.pop(field_path[-1], None)
            
            except Exception as e:
                print(f"Error deleting field {field_path}: {e}")
        return yaml.dump(data)

