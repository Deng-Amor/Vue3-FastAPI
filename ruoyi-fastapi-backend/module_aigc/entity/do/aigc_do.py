from datetime import datetime

from sqlalchemy import BigInteger, CHAR, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class AigcMaterial(Base):
    __tablename__ = 'aigc_material'

    material_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='素材ID')
    material_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='素材名称')
    material_type: Mapped[str] = mapped_column(String(20), nullable=False, comment='素材类型 model/clothes/action/scene')
    material_url: Mapped[str] = mapped_column(String(500), nullable=False, comment='素材URL')
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='封面URL')
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True, comment='标签')
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='备注')
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment='用户ID')
    create_by: Mapped[str | None] = mapped_column(String(64), nullable=True, default='', comment='创建者')
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by: Mapped[str | None] = mapped_column(String(64), nullable=True, default='', comment='更新者')
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=datetime.now, comment='更新时间')


class AigcVideoWorkflow(Base):
    __tablename__ = 'aigc_video_workflow'

    workflow_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='工作流ID')
    workflow_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='工作流名称')
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='draft', comment='状态')
    current_node: Mapped[str] = mapped_column(String(50), nullable=False, default='start', comment='当前节点')
    image: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='服装/商品参考图')
    image1: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='模特参考图')
    key: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='剪映/生成密钥')
    video: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='动作参考视频')
    ratio: Mapped[str | None] = mapped_column(String(20), nullable=True, default='9:16', comment='画面比例')
    merged_images: Mapped[list | None] = mapped_column(JSON, nullable=True, comment='组合图片数组')
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True, comment='生成提示词')
    render_img: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='生图结果')
    action_video: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='动作模仿视频')
    final_video: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='最终视频')
    clean_result: Mapped[list | None] = mapped_column(JSON, nullable=True, comment='后置清理结果')
    node_snapshots: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='节点快照')
    rollback_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='回滚次数')
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True, comment='错误信息')
    del_flag: Mapped[str] = mapped_column(CHAR(1), nullable=False, default='0', comment='删除标志')
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment='用户ID')
    create_by: Mapped[str | None] = mapped_column(String(64), nullable=True, default='', comment='创建者')
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_by: Mapped[str | None] = mapped_column(String(64), nullable=True, default='', comment='更新者')
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=datetime.now, comment='更新时间')

