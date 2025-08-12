from pydantic import BaseModel


class LevelRecord(BaseModel):
    """关卡记录类"""
    fc: bool
    """是否全连"""
    score: int
    """分数"""
    acc: float
    """准确度"""
