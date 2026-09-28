from dataclasses import dataclass

@dataclass
class Step:
    id: str
    name: str
    description: str = ""
@dataclass
class Edge:
    source: str
    target: str
    days: int

@dataclass
class DAG:
    steps: dict[str, Step]
    edges: list[Edge]

@dataclass
class Protocol:
    id: str
    name: str
    description: str
    dag: DAG