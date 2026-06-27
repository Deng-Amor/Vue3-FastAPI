from typing import TypedDict

from langgraph.graph import END, StateGraph


class WorkflowState(TypedDict, total=False):
    image: str
    image1: str
    key: str
    video: str
    ratio: str
    merged_images: list[str]
    prompt: str
    render_img: str
    action_video: str
    final_video: str
    clean_result: list[str]
    current_node: str
    node_snapshots: dict


def snapshot(state: WorkflowState, node: str) -> WorkflowState:
    snapshots = dict(state.get('node_snapshots') or {})
    snapshots[node] = {
        'image': state.get('image'),
        'image1': state.get('image1'),
        'video': state.get('video'),
        'ratio': state.get('ratio'),
        'merged_images': state.get('merged_images'),
        'prompt': state.get('prompt'),
        'render_img': state.get('render_img'),
        'action_video': state.get('action_video'),
        'final_video': state.get('final_video'),
        'clean_result': state.get('clean_result'),
    }
    return {**state, 'current_node': node, 'node_snapshots': snapshots}


def merge_image(state: WorkflowState) -> WorkflowState:
    merged = [item for item in (state.get('image'), state.get('image1')) if item]
    return snapshot({**state, 'merged_images': merged}, 'merge_image')


def generate_prompt(state: WorkflowState) -> WorkflowState:
    prompt = f"""生成一段抖音女装带货短视频，竖屏{state.get('ratio') or '9:16'}。
图1是服装/商品参考图，必须严格还原衣服颜色、版型、领口、肩带、腰线、裙摆、褶皱、装饰和面料质感。
图2是模特参考图，保持脸型、发型、身材比例自然一致。
参考动作视频模仿简单手势舞、站位、节奏、轻微摆胯和转身展示动作。
固定手机机位，中景到大腿构图，模特面对镜头微笑，衣服清晰可见。
不要车内、不要多人、不要坐着、不要衣服变形、不要肢体变形、不要多手多脚、不要脸崩。"""
    return snapshot({**state, 'prompt': prompt}, 'gen_prompt')


def generate_image(state: WorkflowState) -> WorkflowState:
    # ponytail: external image API adapter goes here when keys/endpoints are ready.
    return snapshot({**state, 'render_img': state.get('image') or ''}, 'gen_img')


def mimic_action(state: WorkflowState) -> WorkflowState:
    # ponytail: external action-transfer adapter goes here; keep the source video for traceability.
    return snapshot({**state, 'action_video': state.get('video') or ''}, 'mimic_action')


def generate_video(state: WorkflowState) -> WorkflowState:
    # ponytail: Seedance 2.0 task creation/polling belongs here.
    return snapshot({**state, 'final_video': '', 'current_node': 'gen_video'}, 'gen_video')


def clean_empty(state: WorkflowState) -> WorkflowState:
    empty_fields = [key for key in ('render_img', 'action_video', 'final_video') if not state.get(key)]
    return snapshot({**state, 'clean_result': empty_fields}, 'clean_data')


def build_workflow_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node('merge_image', merge_image)
    graph.add_node('gen_prompt', generate_prompt)
    graph.add_node('gen_img', generate_image)
    graph.add_node('mimic_action', mimic_action)
    graph.add_node('gen_video', generate_video)
    graph.add_node('clean_data', clean_empty)
    graph.add_edge('merge_image', 'gen_prompt')
    graph.add_edge('gen_prompt', 'gen_img')
    graph.add_edge('gen_img', 'mimic_action')
    graph.add_edge('mimic_action', 'gen_video')
    graph.add_edge('gen_video', 'clean_data')
    graph.add_edge('clean_data', END)
    graph.set_entry_point('merge_image')
    return graph.compile()


AIGC_WORKFLOW_GRAPH = build_workflow_graph()

