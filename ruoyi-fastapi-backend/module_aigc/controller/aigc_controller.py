from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_aigc.entity.vo.aigc_vo import AigcMaterialModel, AigcWorkflowModel, WorkflowRollbackModel
from module_aigc.service.aigc_service import AigcService
from utils.response_util import ResponseUtil

aigc_controller = APIRouterPro(prefix='/aigc', order_num=19, tags=['AIGC管理'], dependencies=[PreAuthDependency()])


@aigc_controller.get('/material/list', response_model=DataResponseModel[list[AigcMaterialModel]])
async def list_materials(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    material_type: Annotated[str | None, Query(alias='materialType')] = None,
) -> Response:
    """获取素材库列表。"""
    return ResponseUtil.success(data=await AigcService.list_materials(query_db, material_type))


@aigc_controller.post('/material', response_model=DataResponseModel[AigcMaterialModel])
async def add_material(
    request: Request,
    material: AigcMaterialModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """新增素材库记录。"""
    material.user_id = current_user.user.user_id
    material.create_by = current_user.user.user_name
    material.update_by = current_user.user.user_name
    return ResponseUtil.success(data=await AigcService.add_material(query_db, material))


@aigc_controller.delete('/material/{material_ids}', response_model=ResponseBaseModel)
async def delete_materials(
    request: Request,
    material_ids: Annotated[str, Path()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除一个或多个素材库记录。"""
    await AigcService.delete_materials(query_db, material_ids)
    return ResponseUtil.success(msg='删除成功')


@aigc_controller.get('/workflow/list', response_model=DataResponseModel[list[AigcWorkflowModel]])
async def list_workflows(request: Request, query_db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    """获取视频生成工作流列表。"""
    return ResponseUtil.success(data=await AigcService.list_workflows(query_db))


@aigc_controller.get('/workflow/{workflow_id}', response_model=DataResponseModel[AigcWorkflowModel])
async def get_workflow(
    request: Request,
    workflow_id: Annotated[int, Path()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取视频生成工作流详情。"""
    return ResponseUtil.success(data=await AigcService.get_workflow(query_db, workflow_id))


@aigc_controller.post('/workflow', response_model=DataResponseModel[AigcWorkflowModel])
async def add_workflow(
    request: Request,
    workflow: AigcWorkflowModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """创建视频生成工作流。"""
    workflow.user_id = current_user.user.user_id
    workflow.create_by = current_user.user.user_name
    workflow.update_by = current_user.user.user_name
    return ResponseUtil.success(data=await AigcService.add_workflow(query_db, workflow))


@aigc_controller.post('/workflow/{workflow_id}/run', response_model=DataResponseModel[AigcWorkflowModel])
async def run_workflow(
    request: Request,
    workflow_id: Annotated[int, Path()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """执行视频生成工作流。"""
    return ResponseUtil.success(data=await AigcService.run_workflow(query_db, workflow_id, current_user.user.user_name))


@aigc_controller.post('/workflow/{workflow_id}/rollback', response_model=DataResponseModel[AigcWorkflowModel])
async def rollback_workflow(
    request: Request,
    workflow_id: Annotated[int, Path()],
    rollback: WorkflowRollbackModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """按节点快照回滚视频生成工作流。"""
    return ResponseUtil.success(
        data=await AigcService.rollback_workflow(
            query_db, workflow_id, rollback.target_node, current_user.user.user_name
        )
    )
