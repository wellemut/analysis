from graphviz import Digraph
import os
from pathlib import Path
from config import MAIN_DATABASE, EXPORT_GRAPHS_DIR
from models.Database import Database, Table, Field
from helpers.sdg_colors import SDG_COLORS

db = Database(MAIN_DATABASE)

# Cleanup directory contents
[f.unlink() for f in Path(EXPORT_GRAPHS_DIR).glob("*") if f.is_file()]

# Create network graph for all SDG organizations
domains = db.view("organization_with_domain").select("domain").values()
connections = db.view("connection").select("source_domain", "target_domain").all()

dot = Digraph(
    comment="SDG Map",
    engine="neato",
    graph_attr={"overlap": "prism", "defaultdist": "50", "outputorder": "edgesfirst"},
)

for domain in domains:
    inbound_connections = sum(1 for c in connections if c["target_domain"] == domain)
    outbound_connections = sum(1 for c in connections if c["source_domain"] == domain)
    dot.node(
        domain,
        fillcolor="white",
        style="filled",
        label=f"<<FONT POINT-SIZE='{10 + 20*inbound_connections/100}'>{domain}</FONT><BR /><FONT POINT-SIZE='8'>In: {inbound_connections} — Out: {outbound_connections}</FONT>>",
        URL=domain,
    )

for connection in connections:
    dot.edge(connection["source_domain"], connection["target_domain"])

dot.render(
    os.path.join(EXPORT_GRAPHS_DIR, f"network-graph"), cleanup=True, format="webp"
)

# Create network graphs for each of the 17 Sustainable Development Goals
sdgs = [f"sdg{i}" for i in range(1, 18)]

for sdg in sdgs:
    domains = (
        db.view("organization_with_domain")
        .select("domain")
        .where(Field(f"{sdg}_score") > 0)
        .values()
    )
    source = Table("domain").as_("source").table
    target = Table("domain").as_("target").table
    connections = (
        db.view("connection")
        .select("source_domain", "target_domain")
        .join(source)
        .on(Table("connection").source_domain_id == source.id)
        .join(target)
        .on(Table("connection").target_domain_id == target.id)
        .where(source.field(f"{sdg}_score") > 0)
        .where(target.field(f"{sdg}_score") > 0)
        .all()
    )

    dot = Digraph(
        comment="SDG Map",
        engine="neato",
        graph_attr={
            "bgcolor": SDG_COLORS[sdg],
            "overlap": "prism",
            "splines": "true",
            "outputorder": "edgesfirst",
        },
    )

    for domain in domains:
        inbound_connections = sum(
            1 for c in connections if c["target_domain"] == domain
        )
        outbound_connections = sum(
            1 for c in connections if c["source_domain"] == domain
        )
        dot.node(
            domain,
            fillcolor="white",
            style="filled",
            label=f"<<FONT POINT-SIZE='{10 + 20*inbound_connections/100}'>{domain}</FONT><BR /><FONT POINT-SIZE='8'>In: {inbound_connections} — Out: {outbound_connections}</FONT>>",
            URL=domain,
        )

    for connection in connections:
        dot.edge(
            connection["source_domain"], connection["target_domain"], color="white"
        )

    dot.render(
        os.path.join(EXPORT_GRAPHS_DIR, f"{sdg}-network-graph"),
        cleanup=True,
        format="webp",
    )
