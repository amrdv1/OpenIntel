from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from backend.api.schemas import GraphResponse, GraphNode, GraphLink
from backend.graph.neo4j_client import get_neo4j

router = APIRouter(prefix="/graph", tags=["Graph"])

@router.get("/", response_model=GraphResponse)
async def get_graph(driver: AsyncDriver = Depends(get_neo4j)):
    nodes = []
    links = []
    
    try:
        async with driver.session() as session:
            # Получаем все узлы
            nodes_res = await session.run("MATCH (n) RETURN id(n) AS id, labels(n)[0] AS label, n.value AS value LIMIT 200")
            async for record in nodes_res:
                nodes.append(GraphNode(
                    id=str(record["id"]),
                    label=record["label"],
                    value=record["value"] or "Unknown"
                ))
            
            # Получаем все связи
            links_res = await session.run("MATCH (a)-[r]->(b) RETURN id(a) AS source, id(b) AS target, type(r) AS type LIMIT 500")
            async for record in links_res:
                links.append(GraphLink(
                    source=str(record["source"]),
                    target=str(record["target"]),
                    type=record["type"]
                ))
                
        return GraphResponse(nodes=nodes, links=links)
    except Exception as e:
        print(f"Error fetching graph: {e}")
        return GraphResponse(nodes=[], links=[])
