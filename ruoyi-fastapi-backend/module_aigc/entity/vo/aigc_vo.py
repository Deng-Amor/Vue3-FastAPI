from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class AigcMaterialModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    material_id: int | None = Field(default=None, description='素材ID')
    material_name: str | None = Field(default=None, description='素材名称')
    material_type: Literal['model', 'clothes', 'action', 'scene'] | None = Field(default=None, description='素材类型')
    material_url: str | None = Field(default=None, description='素材URL')
    cover_url: str | None = Field(default=None, description='封面URL')
    tags: list[str] | None = Field(default=None, description='标签')
    remark: str | None = Field(default=None, description='备注')
    user_id: int | None = Field(default=None, description='用户ID')
    create_by: str | None = Field(default=None, description='创建者')
    create_time: datetime | None = Field(default=None, description='创建时间')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')


class AigcWorkflowModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    workflow_id: int | None = Field(default=None, description='工作流ID')
    workflow_name: str | None = Field(default=None, description='工作流名称')
    status: str | None = Field(default=None, description='状态')
    current_node: str | None = Field(default=None, description='当前节点')
    image: str | None = Field(default=None, description='服装/商品参考图')
    image1: str | None = Field(default=None, description='模特参考图')
    key: str | None = Field(default=None, description='剪映/生成密钥')
    video: str | None = Field(default=None, description='动作参考视频')
    ratio: str | None = Field(default='9:16', description='画面比例')
    merged_images: list[str] | None = Field(default=None, description='组合图片数组')
    prompt: str | None = Field(default=None, description='生成提示词')
    render_img: str | None = Field(default=None, description='生图结果')
    action_video: str | None = Field(default=None, description='动作模仿视频')
    final_video: str | None = Field(default=None, description='最终视频')
    clean_result: list[str] | None = Field(default=None, description='后置清理结果')
    node_snapshots: dict | None = Field(default=None, description='节点快照')
    rollback_count: int | None = Field(default=0, description='回滚次数')
    error_message: str | None = Field(default=None, description='错误信息')
    user_id: int | None = Field(default=None, description='用户ID')
    create_by: str | None = Field(default=None, description='创建者')
    create_time: datetime | None = Field(default=None, description='创建时间')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')


class WorkflowRollbackModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    target_node: str = Field(description='回滚目标节点')

