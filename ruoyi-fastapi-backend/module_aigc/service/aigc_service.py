from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_aigc.dao.aigc_dao import AigcDao
from module_aigc.entity.vo.aigc_vo import AigcMaterialModel, AigcWorkflowModel
from module_aigc.service.aigc_workflow_graph import AIGC_WORKFLOW_GRAPH
from utils.common_util import CamelCaseUtil

ROLLBACK_NODES = ['merge_image', 'gen_prompt', 'gen_img', 'mimic_action', 'gen_video', 'clean_data']


class AigcService:
    """AIGC业务服务，负责参数校验、事务提交和工作流状态流转。"""

    @classmethod
    async def list_materials(cls, db: AsyncSession, material_type: str | None = None) -> list[dict]:
        """查询素材列表，可按素材类型过滤。"""
        return CamelCaseUtil.transform_result(await AigcDao.list_materials(db, material_type))

    @classmethod
    async def add_material(cls, db: AsyncSession, material: AigcMaterialModel) -> dict:
        """新增一个素材库素材。"""
        if not material.material_name or not material.material_type or not material.material_url:
            raise ServiceException(message='素材名称、类型、URL不能为空')
        db_material = await AigcDao.add_material(db, material)
        await db.commit()
        return CamelCaseUtil.transform_result(db_material)

    @classmethod
    async def delete_materials(cls, db: AsyncSession, material_ids: str) -> None:
        """按逗号分隔的ID批量删除素材。"""
        ids = [int(item) for item in material_ids.split(',') if item]
        await AigcDao.delete_materials(db, ids)
        await db.commit()

    @classmethod
    async def list_workflows(cls, db: AsyncSession) -> list[dict]:
        """查询视频生成工作流列表。"""
        return CamelCaseUtil.transform_result(await AigcDao.list_workflows(db))

    @classmethod
    async def get_workflow(cls, db: AsyncSession, workflow_id: int) -> dict:
        """查询单个视频生成工作流详情。"""
        workflow = await AigcDao.get_workflow(db, workflow_id)
        if not workflow:
            raise ServiceException(message='工作流不存在')
        return CamelCaseUtil.transform_result(workflow)

    @classmethod
    async def add_workflow(cls, db: AsyncSession, workflow: AigcWorkflowModel) -> dict:
        """创建一个待执行的视频生成工作流。"""
        if not workflow.workflow_name:
            raise ServiceException(message='工作流名称不能为空')
        workflow.status = 'draft'
        workflow.current_node = 'start'
        workflow.node_snapshots = {}
        workflow.create_time = datetime.now()
        workflow.update_time = datetime.now()
        db_workflow = await AigcDao.add_workflow(db, workflow)
        await db.commit()
        return CamelCaseUtil.transform_result(db_workflow)

    @classmethod
    async def run_workflow(cls, db: AsyncSession, workflow_id: int, user_name: str = '') -> dict:
        """执行LangGraph工作流，并把每个节点的结果持久化到数据库。"""
        workflow = await AigcDao.get_workflow(db, workflow_id)
        if not workflow:
            raise ServiceException(message='工作流不存在')
        state = {
            'image': workflow.image or '',
            'image1': workflow.image1 or '',
            'key': workflow.key or '',
            'video': workflow.video or '',
            'ratio': workflow.ratio or '9:16',
            'node_snapshots': workflow.node_snapshots or {},
        }
        try:
            result = AIGC_WORKFLOW_GRAPH.invoke(state)
            update_data = {
                'workflow_id': workflow.workflow_id,
                'status': 'completed' if result.get('final_video') else 'waiting_api',
                'current_node': result.get('current_node') or 'clean_data',
                'merged_images': result.get('merged_images'),
                'prompt': result.get('prompt'),
                'render_img': result.get('render_img'),
                'action_video': result.get('action_video'),
                'final_video': result.get('final_video'),
                'clean_result': result.get('clean_result'),
                'node_snapshots': result.get('node_snapshots'),
                'error_message': None,
                'update_by': user_name,
                'update_time': datetime.now(),
            }
        except Exception as exc:
            update_data = {
                'workflow_id': workflow.workflow_id,
                'status': 'failed',
                'error_message': str(exc),
                'update_by': user_name,
                'update_time': datetime.now(),
            }
        await AigcDao.update_workflow(db, update_data)
        await db.commit()
        return await cls.get_workflow(db, workflow_id)

    @classmethod
    async def rollback_workflow(cls, db: AsyncSession, workflow_id: int, target_node: str, user_name: str = '') -> dict:
        """回滚到指定节点快照，并清理该节点之后的快照数据。"""
        workflow = await AigcDao.get_workflow(db, workflow_id)
        if not workflow:
            raise ServiceException(message='工作流不存在')
        if target_node not in ROLLBACK_NODES:
            raise ServiceException(message='回滚节点不存在')
        snapshots = workflow.node_snapshots or {}
        snapshot = snapshots.get(target_node)
        if not snapshot:
            raise ServiceException(message='目标节点没有快照，无法回滚')
        target_index = ROLLBACK_NODES.index(target_node)
        kept_snapshots = {node: snapshots[node] for node in ROLLBACK_NODES[: target_index + 1] if node in snapshots}
        update_data = {
            'workflow_id': workflow.workflow_id,
            'status': 'rolled_back',
            'current_node': target_node,
            'merged_images': snapshot.get('merged_images'),
            'prompt': snapshot.get('prompt'),
            'render_img': snapshot.get('render_img'),
            'action_video': snapshot.get('action_video'),
            'final_video': snapshot.get('final_video'),
            'clean_result': snapshot.get('clean_result'),
            'node_snapshots': kept_snapshots,
            'rollback_count': (workflow.rollback_count or 0) + 1,
            'update_by': user_name,
            'update_time': datetime.now(),
        }
        await AigcDao.update_workflow(db, update_data)
        await db.commit()
        return await cls.get_workflow(db, workflow_id)
