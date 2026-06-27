from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_aigc.entity.do.aigc_do import AigcMaterial, AigcVideoWorkflow
from module_aigc.entity.vo.aigc_vo import AigcMaterialModel, AigcWorkflowModel


class AigcDao:
    """AIGC数据库访问层，只负责查询和写入，不处理业务规则。"""

    @classmethod
    async def list_materials(cls, db: AsyncSession, material_type: str | None = None) -> list[AigcMaterial]:
        """查询素材列表，可选按类型过滤。"""
        query = select(AigcMaterial)
        if material_type:
            query = query.where(AigcMaterial.material_type == material_type)
        return (await db.execute(query.order_by(AigcMaterial.material_id.desc()))).scalars().all()

    @classmethod
    async def add_material(cls, db: AsyncSession, material: AigcMaterialModel) -> AigcMaterial:
        """写入一条素材记录。"""
        db_material = AigcMaterial(**material.model_dump(exclude_unset=True))
        db.add(db_material)
        await db.flush()
        return db_material

    @classmethod
    async def delete_materials(cls, db: AsyncSession, material_ids: list[int]) -> None:
        """按ID列表删除素材记录。"""
        await db.execute(delete(AigcMaterial).where(AigcMaterial.material_id.in_(material_ids)))

    @classmethod
    async def list_workflows(cls, db: AsyncSession) -> list[AigcVideoWorkflow]:
        """查询未删除的视频生成工作流列表。"""
        query = select(AigcVideoWorkflow).where(AigcVideoWorkflow.del_flag == '0').order_by(
            AigcVideoWorkflow.workflow_id.desc()
        )
        return (await db.execute(query)).scalars().all()

    @classmethod
    async def get_workflow(cls, db: AsyncSession, workflow_id: int) -> AigcVideoWorkflow | None:
        """按ID查询未删除的视频生成工作流。"""
        query = select(AigcVideoWorkflow).where(
            AigcVideoWorkflow.workflow_id == workflow_id, AigcVideoWorkflow.del_flag == '0'
        )
        return (await db.execute(query)).scalars().first()

    @classmethod
    async def add_workflow(cls, db: AsyncSession, workflow: AigcWorkflowModel) -> AigcVideoWorkflow:
        """写入一条视频生成工作流记录。"""
        db_workflow = AigcVideoWorkflow(**workflow.model_dump(exclude_unset=True))
        db.add(db_workflow)
        await db.flush()
        return db_workflow

    @classmethod
    async def update_workflow(cls, db: AsyncSession, workflow: dict) -> None:
        """按主键更新视频生成工作流字段。"""
        await db.execute(update(AigcVideoWorkflow), [workflow])
