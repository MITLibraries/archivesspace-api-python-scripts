import csv

from asaps import models, records


def export_metadata(client, resource, file_identifier, repository_id):
    """Export ArchivesSpace metadata as dicts for each archival object."""
    resource_uri = f"/repositories/{repository_id}/resources/{resource}"
    archival_object_list = client.get_archival_objects_for_resource(resource_uri)
    for uri in archival_object_list:
        record_object = client.get_record(uri)
        report_dict = {
            "uri": record_object["uri"],
            "title": record_object["display_string"],
            "file_identifier": record_object.get(file_identifier),
        }
        yield report_dict


def create_new_digital_objects(client, metadata_csv, repository_id):
    """Creates new digital objects based on a CSV."""
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            uri = row["uri"]
            archival_object = client.get_record(uri)
            new_digital_object = records.create_digital_object(
                archival_object["display_string"], row["link"]
            )
            digital_object_endpoint = models.create_endpoint(
                "digital_object", repository_id
            )
            digital_object_resp = client.post_new_record(
                new_digital_object, digital_object_endpoint
            )
            archival_object = records.link_digital_object(
                archival_object, digital_object_resp["uri"]
            )
            client.save_record(archival_object, True)
