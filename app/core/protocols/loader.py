import json
from pathlib import Path

from app.core.models.protocol import Step, Edge, DAG, Protocol

TEMPLATE_DIR = Path(__file__).parent / "templates"

def load_protocol(name: str) -> Protocol:
    
    path = TEMPLATE_DIR / f"{name}_template.json"

    with path.open() as f:
        data = json.load(f)

    step_dict = {}
    edge_list = []

    for item in data["steps"]:
        step_dict[item["id"]] = Step(id = item["id"], name = item["name"], description = item["description"])

    for item in data["edges"]:
        edge_list.append(Edge(source = item["from"], target = item["to"], days = item["days"]))

    dag = DAG(steps = step_dict, edges = edge_list)
    protocol = Protocol(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        dag=dag
    )

    return protocol
        
        