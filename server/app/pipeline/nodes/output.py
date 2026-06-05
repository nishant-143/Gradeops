from app.pipeline.state import GradeState


def output_node(state: GradeState) -> GradeState:
    # DB persistence happens in PipelineService to keep node pure and testable.
    return state
