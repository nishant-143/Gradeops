from langgraph.graph import END, StateGraph

from app.pipeline.nodes.confidence import confidence_node
from app.pipeline.nodes.grader import grader_node
from app.pipeline.nodes.justifier import justifier_node
from app.pipeline.nodes.output import output_node
from app.pipeline.nodes.plagiarism import plagiarism_node
from app.pipeline.nodes.preprocessor import preprocessor_node
from app.pipeline.state import GradeState


def build_graph():
    graph = StateGraph(GradeState)
    graph.add_node("preprocess", preprocessor_node)
    graph.add_node("grade", grader_node)
    graph.add_node("confidence", confidence_node)
    graph.add_node("justify", justifier_node)
    graph.add_node("plagiarism", plagiarism_node)
    graph.add_node("output", output_node)

    graph.set_entry_point("preprocess")
    graph.add_edge("preprocess", "grade")
    graph.add_edge("grade", "confidence")
    graph.add_conditional_edges(
        "confidence",
        lambda s: "grade" if s.get("needs_reeval") else "justify",
    )
    graph.add_edge("justify", "plagiarism")
    graph.add_edge("plagiarism", "output")
    graph.add_edge("output", END)
    return graph.compile()
