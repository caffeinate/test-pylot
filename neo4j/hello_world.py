"""
Working with a Neo4j graph database.

Example code started as https://neo4j.com/docs/api/python-driver/current/

Created on 13 Mar 2024

@author: si
"""
import logging

from neo4j import GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError


class HelloNeo4j:
    """
    Add a few connected nodes to a Neo4J database.

    The nodes are given the Node label 'Number'
    """

    def __init__(self, uri, user, password, database=None):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def log(self, msg, level="INFO"):
        print(msg)

    def add_numbered_nodes(self):
        "Add 'Number' nodes in a chain"

        some_numbers = ["One", "Two", "Three", "Four"]
        query_params = {}
        query = ""
        for idx, node_name in enumerate(some_numbers):
            query += f"CREATE (n{idx}:Number {{ name: $node_name_{idx} }}) "
            query_params[f"node_name_{idx}"] = node_name

            if idx > 0:
                query += f"CREATE (n{idx-1})-[:plus_one]->(n{idx}) "

        query += "RETURN n0.name"
        self.log(f"Running: {query}")

        try:
            record = self.driver.execute_query(
                query,
                **query_params,
                database_=self.database,
                result_transformer_=lambda r: r.single(strict=True),
            )
            return record["n0.name"]
        # Capture any errors along with the query and data for traceability
        except (DriverError, Neo4jError) as exception:
            logging.error("%s raised an error: \n%s", query, exception)
            raise


if __name__ == "__main__":
    import os
    import yaml

    # Don't forget export PULUMI_STACK=$(pulumi stack --show-name)
    stack_name = os.environ["PULUMI_STACK"]

    # Get the password used by ansible to configure the docker container + DNS info
    with open(f"neo4j_{stack_name}_conf.yml") as f:
        config = yaml.safe_load(f)

    neo4j_host = config["bolt_dns_name"]
    uri = f"bolt+s://{neo4j_host}:443"

    user = "neo4j"
    password = config["neo4j_password"]

    # Neo4J community addition only allows one database
    database = "neo4j"
    app = HelloNeo4j(uri, user, password, database)
    try:
        app.add_numbered_nodes()
    finally:
        app.close()
