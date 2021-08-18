import csv
import datetime
import json
import logging
import os
import time

import click
import structlog
from asnake.client import ASnakeClient

from asaps import models, records, workflows

logger = structlog.get_logger()


NOTE_TYPES = [
    "abstract",
    "accessrestrict",
    "acqinfo",
    "altformavail",
    "appraisal",
    "arrangement",
    "bibliography",
    "bioghist",
    "custodhist",
    "prefercite",
    "processinfo",
    "relatedmaterial",
    "scopecontent",
    "userestrict",
]
OBJECT_FIELD_DICT = {
    "dates": ["begin", "end", "expression", "label", "date_type"],
    "extents": [
        "portion",
        "number",
        "extent_type",
        "container_summary",
        "physical_details",
        "dimensions",
    ],
}

skipped_resources = []


@click.group()
@click.option("--url", required=True, envvar="ARCHIVESSPACE_URL")
@click.option(
    "-u", "--username", required=True, help="The username for authentication."
)
@click.option(
    "-p",
    "--password",
    required=True,
    envvar="DOCKER_PASS",
    help="The password for authentication.",
)
@click.pass_context
def main(ctx, url, username, password):
    ctx.obj = {}
    if os.path.isdir("logs") is False:
        os.mkdir("logs")
    dt = datetime.datetime.utcnow().isoformat(timespec="seconds")
    log_suffix = f"{dt}.log"
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    logging.basicConfig(
        format="%(message)s",
        handlers=[logging.FileHandler(f"logs/log-{log_suffix}", "w")],
        level=logging.INFO,
    )
    logger.info("Application start")

    client = ASnakeClient(baseurl=url, username=username, password=password)
    as_ops = models.AsOperations(client)
    start_time = time.time()
    ctx.obj["as_ops"] = as_ops
    ctx.obj["start_time"] = start_time
    ctx.obj["log_suffix"] = log_suffix


@main.command()
@click.pass_context
@click.option(
    "-d",
    "--modify_records",
    is_flag=True,
    help="Modify records rather than performing a dry run",
)
@click.option(
    "-m",
    "--metadata_csv",
    required=True,
    help="The metadata CSV file to use.",
)
@click.option("-f", "--field", required=True, help="The field to edit.")
def deletefield(ctx, modify_records, metadata_csv, field):
    """Deletes the specified field from records that are specified in a CSV
    file."""
    as_ops = ctx.obj["as_ops"]
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            uri = row["uri"]
            record_object = as_ops.get_record(uri)
            if field in NOTE_TYPES:
                for note in (
                    n for n in record_object["notes"] if n.get("type") == field
                ):
                    record_object["notes"].remove(note)
            else:
                record_object.pop(field, None)
            if record_object.modified is True:
                as_ops.save_record(record_object, modify_records)
    models.elapsed_time(ctx.obj["start_time"], "Total runtime:")
    models.create_csv_from_log(f"update_record_{field}", ctx.obj["log_suffix"])


@main.command()
@click.pass_context
@click.option(
    "-s",
    "--search",
    required=True,
    help="The string to search for.",
)
@click.option(
    "-d",
    "--modify_records",
    is_flag=True,
    help="Modify records rather than performing a dry run",
)
@click.option(
    "-i",
    "--repository_id",
    required=True,
    help="The ID of the repository to use.",
)
@click.option(
    "-t",
    "--record_type",
    required=True,
    type=click.Choice(["accession", "archival_object", "digital_object", "resource"]),
    help="The record type to use.",
)
@click.option("-f", "--field", help="The field to edit.")
@click.option(
    "-r",
    "--replacement_value",
    required=True,
    help="The replacement value to be inserted.",
)
def find(
    ctx, modify_records, repository_id, record_type, field, search, replacement_value
):
    """Finds and replaces the specified string in the specified field in all
    records of the specified type of records"""
    as_ops = ctx.obj["as_ops"]
    skipped_archival_objects = []
    if record_type == "archival_object":
        for uri in skipped_resources:
            archival_object_list = as_ops.get_archival_objects_for_resource(uri)
            skipped_archival_objects.append(archival_object_list)
    skipped_uris = skipped_resources + skipped_archival_objects
    for uri in as_ops.search(search, repository_id, record_type, field):
        if uri not in skipped_uris:
            record_object = as_ops.get_record(uri)
            if field in NOTE_TYPES:
                notes = models.filter_note_type(record_object, field)
                for note in notes:
                    for subnote in note.get("subnotes", []):
                        if "content" in subnote:
                            update = subnote["content"].replace(
                                search, replacement_value
                            )
                            subnote["content"] = update
                        elif "definedlist" in subnote:
                            update = subnote["definedlist"].replace(
                                search, replacement_value
                            )
                            subnote["definedlist"] = update
            else:
                update = record_object.get(field, "").replace(search, replacement_value)
                record_object[field] = update
            if record_object.modified is True:
                as_ops.save_record(record_object, modify_records)
        else:
            logger.info(f"{uri} skipped")
    models.elapsed_time(ctx.obj["start_time"], "Total runtime:")
    models.create_csv_from_log(f"{record_type}-{field}-find", ctx.obj["log_suffix"])


@main.command()
@click.pass_context
@click.option("-r", "--resource", required=True, help="The resource number")
@click.option(
    "-i",
    "--file_identifier",
    required=True,
    help="The field for file matching.",
)
@click.option(
    "-e",
    "--repository_id",
    required=True,
    help="The ID of the repository to use.",
)
def metadata(ctx, resource, file_identifier, repository_id):
    """Exports metadata from a resource's archival objects that will be matched
    to files in preparation for ingesting the files into a repository."""
    as_ops = ctx.obj["as_ops"]
    report_dicts = workflows.export_metadata(
        as_ops, resource, file_identifier, repository_id
    )
    for report_dict in report_dicts:
        logger.info(**report_dict)
    models.elapsed_time(ctx.obj["start_time"], "Total runtime:")
    models.create_csv_from_log(resource, ctx.obj["log_suffix"], False)


@main.command()
@click.pass_context
@click.option(
    "-m",
    "--metadata_csv",
    required=True,
    help="The metadata CSV file to use.",
)
@click.option(
    "-o",
    "--output_path",
    required=True,
    default="",
    help="The path of the output files, include " "/ at the end of the path",
)
@click.option(
    "-p",
    "--match_point",
    required=True,
    help="The match point to be used in the new record report.",
)
def newagents(ctx, metadata_csv, output_path, match_point):
    """Creates new agent records based on a CSV file."""
    as_ops = ctx.obj["as_ops"]
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        new_record_data = {}
        for row in reader:
            agent_type = row["agent_type"]
            if agent_type == "people":
                agent_record = records.create_agent_pers(
                    agent_type,
                    row["primary_name"],
                    row["sort_name"],
                    row["rest_of_name"],
                    row["fuller_form"],
                    row["title"],
                    row["prefix"],
                    row["suffix"],
                    row["dates"],
                    row["expression"],
                    row["begin"],
                    row["end"],
                    row["authority_id"],
                    row["certainty"],
                    row["label"],
                )
            if agent_type == "corporate_entities":
                agent_record = records.create_agent_corp(
                    agent_type,
                    row["primary_name"],
                    row["sort_name"],
                    row["subord_name_1"],
                    row["subord_name_2"],
                    row["number"],
                    row["dates"],
                    row["qualifier"],
                    row["authority_id"],
                )
            agent_endpoint = models.create_endpoint(agent_type)
            agent_resp = as_ops.post_new_record(agent_record, agent_endpoint)
            new_record_data[row[match_point]] = agent_resp["uri"]
        models.create_new_record_report(new_record_data, f"{output_path}newagents")
    models.elapsed_time(ctx.obj["start_time"], "Total runtime:")
    models.create_csv_from_log("agents", ctx.obj["log_suffix"])


@main.command()
@click.pass_context
@click.option(
    "-m",
    "--metadata_csv",
    required=True,
    help="The metadata CSV file to use.",
)
@click.option(
    "-a",
    "--agent_file",
    required=True,
    help="The CSV mapping agent strings to URIs.",
)
@click.option(
    "-i",
    "--repository_id",
    required=True,
    help="The ID of the repository to use.",
)
def newarchobjs(ctx, metadata_csv, agent_file, repository_id):
    """Creates new archival object records based on a CSV file."""
    as_ops = ctx.obj["as_ops"]

    agent_uri_dict = {}
    with open(agent_file) as agentfile:
        reader = csv.DictReader(agentfile)
        for row in reader:
            agent_uri_dict[row["match_point"]] = row["uri"]
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            agent_links = []
            agent_links = models.string_to_uri(
                agent_links, row["publisher"], agent_uri_dict, "creator", "pbl"
            )
            for author in json.loads(row["authors"]):
                agent_links = models.string_to_uri(
                    agent_links, author, agent_uri_dict, "creator", ""
                )
            new_digital_object = records.create_digital_object(
                row["title"], row["link"]
            )
            digital_object_endpoint = models.create_endpoint(
                "digital_object", repository_id
            )
            digital_object_resp = as_ops.post_new_record(
                new_digital_object, digital_object_endpoint
            )
            note = records.create_note(
                "scopecontent", "Scope and Contents", row["abstract"]
            )
            archival_object = records.create_archival_object(
                row["title"],
                "file",
                agent_links,
                [note],
                row["parent_uri"],
                row["resource"],
                row["begin"],
                row["end"],
                row["expression"],
                row["certainty"],
                row["label"],
            )
            archival_object = records.link_digital_object(
                archival_object, digital_object_resp["uri"]
            )
            archival_object = records.link_top_container(
                archival_object,
                row["top_container_1"],
                row["child_type"],
                row["child_indicator"],
            )
            archival_object = records.link_top_container(
                archival_object, row["top_container_2"], "", ""
            )
            archival_object_endpoint = models.create_endpoint(
                "archival_object", repository_id
            )
            as_ops.post_new_record(archival_object, archival_object_endpoint)
    models.elapsed_time(ctx.obj["start_time"], "Total runtime:")
    models.create_csv_from_log("archival_object", ctx.obj["log_suffix"])


@main.command()
@click.pass_context
@click.option(
    "-m",
    "--metadata_csv",
    required=True,
    help="The metadata CSV file to use.",
)
@click.option(
    "-i",
    "--repository_id",
    required=True,
    help="The ID of the repository to use.",
)
def newdigobjs(ctx, metadata_csv, repository_id):
    """Creates new digital object records based on a CSV file."""
    as_ops = ctx.obj["as_ops"]
    workflows.create_new_digital_objects(as_ops, metadata_csv, repository_id)
    models.elapsed_time(ctx.obj["start_time"], "Total runtime:")
    models.create_csv_from_log("new_digital_object", ctx.obj["log_suffix"])


@main.command()
@click.option(
    "-i",
    "--repository_id",
    required=True,
    help="The ID of the repository to use.",
)
@click.option("-t", "--record_type", required=True, help="The record type to use.")
@click.option("-f", "--field", required=True, help="The field to extract.")
@click.pass_context
def report(ctx, repository_id, record_type, field):
    """Exports a report containing minimal metadata and a specified field from
    all records of the specified type."""
    as_ops = ctx.obj["as_ops"]

    endpoint = models.create_endpoint(record_type, repository_id)
    ids = as_ops.get_all_records(endpoint)
    for id in ids:
        uri = f"{endpoint}/{id}"
        record_object = as_ops.get_record(uri)
        collection_id = models.concat_id(record_object)
        report_dict = {
            "uri": record_object["uri"],
            "title": record_object["title"],
            "id": collection_id,
        }
        if field in NOTE_TYPES:
            report_dicts = models.extract_note_field(field, record_object, report_dict)
            for report_dict in report_dicts:
                logger.info(**report_dict)
        elif field in OBJECT_FIELD_DICT:
            report_dicts = models.extract_obj_field(
                field, record_object, OBJECT_FIELD_DICT, report_dict
            )
            for report_dict in report_dicts:
                logger.info(**report_dict)
        else:
            report_dict[field] = record_object.get(field, "")
            logger.info(**report_dict)
    models.elapsed_time(ctx.obj["start_time"], "Total runtime:")
    models.create_csv_from_log(f"{record_type}-{field}-values", ctx.obj["log_suffix"])


@main.command()
@click.pass_context
@click.option(
    "-d",
    "--modify_records",
    is_flag=True,
    help="Modify records rather than performing a dry run",
)
@click.option(
    "-m",
    "--metadata_csv",
    required=True,
    help="The metadata CSV file to use.",
)
def updatedigobj(ctx, modify_records, metadata_csv):
    """Updates the link in digital objects listed in a CSV file."""
    as_ops = ctx.obj["as_ops"]
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            digital_object_uri = row["digital_object_uri"]
            link = row["link"]
            digital_object = as_ops.get_record(digital_object_uri)
            updated_digital_object = records.update_digital_object_link(
                digital_object, link
            )
            if updated_digital_object.modified is True:
                as_ops.save_record(updated_digital_object, modify_records)
    models.elapsed_time(ctx.obj["start_time"], "Total runtime:")
    models.create_csv_from_log("digital_object", ctx.obj["log_suffix"])


@main.command()
@click.pass_context
@click.option(
    "-d",
    "--modify_records",
    is_flag=True,
    help="Modify records rather than performing a dry run",
)
@click.option(
    "-m",
    "--metadata_csv",
    required=True,
    help="The metadata CSV file to use.",
)
@click.option("-f", "--field", help="The field to edit.")
@click.option(
    "-r",
    "--replacement_value_column",
    required=True,
    help="The replacement value to be inserted.",
)
def updaterecords(ctx, modify_records, metadata_csv, field, replacement_value_column):
    """Updates records with values listed in a CSV file."""
    as_ops = ctx.obj["as_ops"]
    with open(metadata_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            uri = row["uri"]
            replacement_value = row[replacement_value_column]
            record_object = as_ops.get_record(uri)
            if field in NOTE_TYPES:
                notes = models.filter_note_type(record_object, field)
                note_found = False
                for note in notes:
                    for subnote in note.get("subnotes", []):
                        subnote["content"] = replacement_value
                        note_found = True
                if note_found is not True:
                    note = {}
                    note["jsonmodel_type"] = "note_multipart"
                    note["type"] = field
                    note["publish"] = True
                    note["subnotes"] = [
                        {
                            "jsonmodel_type": "note_text",
                            "content": replacement_value,
                            "publish": True,
                        }
                    ]
                    record_object["notes"].append(note)
            else:
                record_object[field] = replacement_value
            if record_object.modified is True:
                as_ops.save_record(record_object, modify_records)
    models.elapsed_time(ctx.obj["start_time"], "Total runtime:")
    models.create_csv_from_log(f"update_record_{field}", ctx.obj["log_suffix"])
