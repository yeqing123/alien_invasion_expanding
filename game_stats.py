import json
from pathlib import Path

class GameStats:
    """跟踪游戏的统计信息"""

    def __init__(self, ai_game):
        """初始化统计信息"""
        self.settings = ai_game.settings
        # 最高得分不应该被重置
        self.high_score = self.get_saved_high_score()
        # 初始化有关信息
        self.reset_stats()

    def reset_stats(self):
        """重置游戏的状态信息"""
        self.ship_left = self.settings.ship_limit
        # 重置游戏进展水平
        self.level = 1
        # 重置得分
        self.score = 0
        # 重置游戏等级
        self.grade = 1

    def get_saved_high_score(self):
        """从文件中读取历史最高得分"""
        path = Path('high_score.json')
        try:
            contents = path.read_text()
            high_score = json.loads(contents)
        except FileNotFoundError:
            return 0
        else:
            return high_score