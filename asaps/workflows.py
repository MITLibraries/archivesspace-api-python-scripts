import csv

from asaps import models, records


def export_metadata(client, resource, file_identifier, repo_id):
    """Export ArchivesSpace metadata as dicts for each archival object."""
    resource_uri = f"/repositories/{repo_id}/resources/{resource}"
    arch_obj_list = client.get_arch_objs_for_resource(resource_uri)
    for uri in arch_obj_list:
        rec_obj = client.get_record(uri)
        report_dict = {
            "uri": rec_obj["uri"],
            "title": rec_obj["display_string"],
            "file_identifier": rec_obj.get(file_identifier),
        }
        yield report_dict


def create_new_dig_objs(client, metadata_csv, repo_id):
    """Creates new digital objects based on a CSV."""
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            uri = row["uri"]
            arch_obj = client.get_record(uri)
            new_dig_obj = records.create_dig_obj(
                arch_obj["display_string"], row["link"]
            )
            dig_obj_endpoint = models.create_endpoint("digital_object", repo_id)
            dig_obj_resp = client.post_new_record(new_dig_obj, dig_obj_endpoint)
            arch_obj = records.link_dig_obj(arch_obj, dig_obj_resp["uri"])
            client.save_record(arch_obj, "False")
