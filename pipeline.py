from langgraph.graph import StateGraph, END
from loguru import logger

from agents.state import PipelineState
from agents.research_agent import research_agent
from agents.expansion_agent import expansion_agent
from agents.cleaning_agent import cleaning_agent
from agents.intent_agent import intent_agent
from agents.clustering_agent import clustering_agent
from agents.prioritization_agent import prioritization_agent
from agents.mapping_agent import mapping_agent
from agents.output_agent import output_agent


def build_pipeline() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("research",       research_agent)
    graph.add_node("expansion",      expansion_agent)
    graph.add_node("cleaning",       cleaning_agent)
    graph.add_node("intent",         intent_agent)
    graph.add_node("clustering",     clustering_agent)
    graph.add_node("prioritization", prioritization_agent)
    graph.add_node("mapping",        mapping_agent)
    graph.add_node("output",         output_agent)

    graph.set_entry_point("research")
    graph.add_edge("research",       "expansion")
    graph.add_edge("expansion",      "cleaning")
    graph.add_edge("cleaning",       "intent")
    graph.add_edge("intent",         "clustering")
    graph.add_edge("clustering",     "prioritization")
    graph.add_edge("prioritization", "mapping")
    graph.add_edge("mapping",        "output")
    graph.add_edge("output",         END)

    return graph.compile()


def run_pipeline(input_data: dict) -> PipelineState:
    initial_state: PipelineState = {
        "site_url":             input_data.get("site_url", ""),
        "business_description": input_data.get("business_description", ""),
        "seed_keywords":        input_data.get("seed_keywords", []),
        "geo":                  input_data.get("geo", "Москва"),
        "language":             input_data.get("language", "ru"),
        "target_pages":         input_data.get("target_pages", []),
        "competitors":          input_data.get("competitors", []),
        "commercial_priority":  input_data.get("commercial_priority", {}),

        "raw_keywords":        [],
        "cleaned_keywords":    [],
        "classified_keywords": [],

        "clusters":     [],
        "gap_analysis": [],
        "output_table": [],

        "errors":       [],
        "logs":         [],
        "current_step": "init",
    }

    logger.info(f"pipeline started: {initial_state['site_url']}")
    logger.info(f"seeds: {initial_state['seed_keywords']}")

    pipeline = build_pipeline()
    final_state = pipeline.invoke(initial_state)

    if final_state.get("errors"):
        logger.warning(f"errors during run: {final_state['errors']}")

    return final_state


if __name__ == "__main__":
    example_input = {
        "site_url": "example-mebel.ru",
        "business_description": "интернет-магазин мебели, продаём диваны, кресла, столы",
        "seed_keywords": ["купить диван", "угловой диван", "диван кровать"],
        "geo": "Москва",
        "language": "ru",
        "target_pages": [
            "/catalog/divany/",
            "/catalog/uglovye-divany/",
            "/catalog/divany-krovati/",
        ],
        "competitors": ["divan.ru", "hoff.ru"],
        "commercial_priority": {"диваны": 5, "кресла": 3, "столы": 2},
    }

    result = run_pipeline(example_input)
    print(f"\nПайплайн завершён. Кластеров: {len(result['clusters'])}")
