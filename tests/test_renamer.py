"""
测试重命名引擎模块
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from smartrenamer.core.models import MediaFile, MediaType, RenameRule
from smartrenamer.core.renamer import (
    Renamer,
    重命名器,
    RenameRuleManager,
    重命名规则管理器,
    RenameHistory,
    重命名历史记录,
    create_predefined_rule,
    创建预定义规则,
    PREDEFINED_TEMPLATES,
    预定义模板,
    填充,
    清理文件名,
    截断,
    大写首字母,
)


class Test自定义过滤器:
    """测试自定义 Jinja2 过滤器"""
    
    def test_填充过滤器(self):
        """测试填充过滤器"""
        assert 填充(1, 2) == "01"
        assert 填充(5, 3) == "005"
        assert 填充(10, 2) == "10"
        assert 填充(123, 5) == "00123"
    
    def test_清理文件名过滤器(self):
        """测试清理文件名过滤器"""
        # 测试非法字符
        assert 清理文件名("file<>name") == "filename"
        assert 清理文件名('file:name"test') == "filenametest"
        assert 清理文件名("file/path\\name") == "filepathname"
        assert 清理文件名("file|name?*") == "filename"
        
        # 测试空格处理
        assert 清理文件名("  file  name  ") == "file name"
        assert 清理文件名("file    name") == "file name"
    
    def test_截断过滤器(self):
        """测试截断过滤器"""
        assert 截断("很长的标题名称", 5) == "很长..."
        assert 截断("短标题", 10) == "短标题"
        assert 截断("exactly10!", 10) == "exactly10!"
        assert 截断("超长文本内容测试试", 8, "..") == "超长文本内容.."
    
    def test_大写首字母过滤器(self):
        """测试大写首字母过滤器"""
        assert 大写首字母("the matrix") == "The Matrix"
        assert 大写首字母("breaking bad") == "Breaking Bad"
        assert 大写首字母("ALREADY CAPS") == "Already Caps"


class Test预定义模板:
    """测试预定义模板"""
    
    def test_预定义模板存在(self):
        """测试预定义模板是否存在"""
        assert "电影-简洁" in 预定义模板
        assert "电影-标准" in 预定义模板
        assert "电影-完整" in 预定义模板
        assert "电视剧-标准" in 预定义模板
        assert "电视剧-带剧集名" in 预定义模板
        assert "电视剧-完整" in 预定义模板
        assert "电视剧-分季目录" in 预定义模板
    
    def test_创建预定义规则_电影(self):
        """测试创建电影预定义规则"""
        规则 = 创建预定义规则("电影-简洁")
        
        assert 规则 is not None
        assert 规则.name == "电影-简洁"
        assert 规则.media_type == MediaType.MOVIE
        assert 规则.template is not None
    
    def test_创建预定义规则_电视剧(self):
        """测试创建电视剧预定义规则"""
        规则 = 创建预定义规则("电视剧-标准")
        
        assert 规则 is not None
        assert 规则.name == "电视剧-标准"
        assert 规则.media_type == MediaType.TV_SHOW
        assert 规则.template is not None
    
    def test_创建预定义规则_不存在(self):
        """测试创建不存在的预定义规则"""
        规则 = 创建预定义规则("不存在的模板")
        assert 规则 is None
    
    def test_英文别名(self):
        """测试英文别名"""
        规则 = create_predefined_rule("电影-简洁")
        assert 规则 is not None
        assert PREDEFINED_TEMPLATES == 预定义模板


class Test重命名规则管理器:
    """测试重命名规则管理器"""
    
    def test_创建规则管理器(self):
        """测试创建规则管理器"""
        管理器 = 重命名规则管理器()
        assert 管理器 is not None
        assert len(管理器.获取所有规则()) == 0
    
    def test_验证模板_有效(self):
        """测试验证有效模板"""
        管理器 = 重命名规则管理器()
        
        有效, 错误 = 管理器.验证模板("{{ title }} ({{ year }})")
        assert 有效
        assert 错误 is None
    
    def test_验证模板_无效(self):
        """测试验证无效模板"""
        管理器 = 重命名规则管理器()
        
        # 语法错误
        有效, 错误 = 管理器.验证模板("{{ title } ({{ year }})")
        assert not 有效
        assert 错误 is not None
    
    def test_添加规则(self):
        """测试添加规则"""
        管理器 = 重命名规则管理器()
        
        规则 = RenameRule(
            name="测试规则",
            description="测试描述",
            template="{{ title }} ({{ year }})",
            media_type=MediaType.MOVIE,
        )
        
        assert 管理器.添加规则(规则)
        assert len(管理器.获取所有规则()) == 1
        assert 管理器.获取规则("测试规则") == 规则
    
    def test_添加规则_无效模板(self):
        """测试添加无效模板的规则"""
        管理器 = 重命名规则管理器()
        
        规则 = RenameRule(
            name="无效规则",
            description="无效模板",
            template="{{ title } ({{ year }})",  # 语法错误
            media_type=MediaType.MOVIE,
        )
        
        with pytest.raises(ValueError):
            管理器.添加规则(规则)
    
    def test_移除规则(self):
        """测试移除规则"""
        管理器 = 重命名规则管理器()
        
        规则 = RenameRule(
            name="测试规则",
            description="测试描述",
            template="{{ title }}",
            media_type=MediaType.MOVIE,
        )
        
        管理器.添加规则(规则)
        assert len(管理器.获取所有规则()) == 1
        
        assert 管理器.移除规则("测试规则")
        assert len(管理器.获取所有规则()) == 0
        
        # 移除不存在的规则
        assert not 管理器.移除规则("不存在的规则")
    
    def test_保存和加载规则(self, tmp_path):
        """测试保存和加载规则"""
        管理器 = 重命名规则管理器()
        
        # 添加几个规则
        规则1 = RenameRule(
            name="规则1",
            description="描述1",
            template="{{ title }}",
            media_type=MediaType.MOVIE,
        )
        规则2 = RenameRule(
            name="规则2",
            description="描述2",
            template="{{ title }} S{{ season|pad(2) }}E{{ episode|pad(2) }}",
            media_type=MediaType.TV_SHOW,
        )
        
        管理器.添加规则(规则1)
        管理器.添加规则(规则2)
        
        # 保存到文件
        文件路径 = tmp_path / "rules.json"
        assert 管理器.保存到文件(文件路径)
        assert 文件路径.exists()
        
        # 加载到新管理器
        新管理器 = 重命名规则管理器()
        assert 新管理器.从文件加载(文件路径)
        
        所有规则 = 新管理器.获取所有规则()
        assert len(所有规则) == 2
        assert 所有规则[0].name == "规则1"
        assert 所有规则[1].name == "规则2"
    
    def test_英文别名方法(self):
        """测试英文别名方法"""
        manager = RenameRuleManager()
        
        rule = RenameRule(
            name="Test Rule",
            description="Test",
            template="{{ title }}",
            media_type=MediaType.MOVIE,
        )
        
        assert manager.add_rule(rule)
        assert manager.get_rule("Test Rule") == rule
        assert len(manager.get_all_rules()) == 1
        assert manager.remove_rule("Test Rule")


class Test重命名器:
    """测试重命名器"""
    
    def test_创建重命名器(self):
        """测试创建重命名器"""
        重命名器实例 = 重命名器(预览模式=True)
        assert 重命名器实例 is not None
        assert 重命名器实例.预览模式 is True
    
    def test_生成新文件名_电影(self):
        """测试生成电影新文件名"""
        重命名器实例 = 重命名器()
        
        媒体文件 = MediaFile(
            path=Path("/test/movie.mkv"),
            original_name="movie.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="黑客帝国",
            year=1999,
            resolution="1080p",
        )
        
        规则 = RenameRule(
            name="电影规则",
            description="测试",
            template="{{ title }} ({{ year }}) {{ resolution }}",
            media_type=MediaType.MOVIE,
        )
        
        成功, 新名称, 错误 = 重命名器实例.生成新文件名(媒体文件, 规则)
        
        assert 成功
        assert 错误 is None
        assert "黑客帝国" in 新名称
        assert "1999" in 新名称
        assert "1080p" in 新名称
        assert 新名称.endswith(".mkv")
    
    def test_生成新文件名_电视剧(self):
        """测试生成电视剧新文件名"""
        重命名器实例 = 重命名器()
        
        媒体文件 = MediaFile(
            path=Path("/test/show.mkv"),
            original_name="show.mkv",
            extension=".mkv",
            media_type=MediaType.TV_SHOW,
            title="绝命毒师",
            year=2008,
            season_number=1,
            episode_number=1,
            episode_title="试播集",
            resolution="1080p",
        )
        
        规则 = RenameRule(
            name="电视剧规则",
            description="测试",
            template="{{ title }} S{{ season|填充(2) }}E{{ episode|填充(2) }} {{ episode_title }}",
            media_type=MediaType.TV_SHOW,
        )
        
        成功, 新名称, 错误 = 重命名器实例.生成新文件名(媒体文件, 规则)
        
        assert 成功
        assert 错误 is None
        assert "绝命毒师" in 新名称
        assert "S01E01" in 新名称
        assert "试播集" in 新名称
    
    def test_生成新文件名_使用过滤器(self):
        """测试生成文件名时使用自定义过滤器"""
        重命名器实例 = 重命名器()
        
        媒体文件 = MediaFile(
            path=Path("/test/movie.mkv"),
            original_name="movie.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="The Matrix: Reloaded",
            year=2003,
        )
        
        规则 = RenameRule(
            name="过滤器测试",
            description="测试",
            template="{{ title|清理文件名|replace(' ', '.') }}.{{ year }}",
            media_type=MediaType.MOVIE,
        )
        
        成功, 新名称, 错误 = 重命名器实例.生成新文件名(媒体文件, 规则)
        
        assert 成功
        assert "The.Matrix.Reloaded" in 新名称
        assert ":" not in 新名称  # 冒号应该被清理掉
    
    def test_预览模式_重命名文件(self, tmp_path):
        """测试预览模式重命名文件"""
        # 创建测试文件
        测试文件 = tmp_path / "test.mkv"
        测试文件.write_text("test")
        
        重命名器实例 = 重命名器(预览模式=True)
        
        媒体文件 = MediaFile(
            path=测试文件,
            original_name="test.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="测试电影",
            year=2024,
        )
        
        规则 = RenameRule(
            name="测试规则",
            description="测试",
            template="{{ title }} ({{ year }})",
            media_type=MediaType.MOVIE,
        )
        
        成功, 错误 = 重命名器实例.重命名文件(媒体文件, 规则)
        
        assert 成功
        assert 错误 is None
        assert 媒体文件.new_name is not None
        assert 媒体文件.rename_status == "preview"
        
        # 原文件应该还在
        assert 测试文件.exists()
    
    def test_实际重命名文件(self, tmp_path):
        """测试实际重命名文件"""
        # 创建测试文件
        原文件 = tmp_path / "original.mkv"
        原文件.write_text("test content")
        
        重命名器实例 = 重命名器(预览模式=False, 创建备份=True)
        
        媒体文件 = MediaFile(
            path=原文件,
            original_name="original.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="新电影",
            year=2024,
        )
        
        规则 = RenameRule(
            name="测试规则",
            description="测试",
            template="{{ title }} ({{ year }})",
            media_type=MediaType.MOVIE,
        )
        
        成功, 错误 = 重命名器实例.重命名文件(媒体文件, 规则)
        
        assert 成功
        assert 错误 is None
        assert 媒体文件.rename_status == "success"
        
        # 原文件应该不存在了
        assert not 原文件.exists()
        
        # 新文件应该存在
        新文件 = 媒体文件.path
        assert 新文件.exists()
        assert "新电影" in 新文件.name
        assert "2024" in 新文件.name
        
        # 应该有历史记录
        历史 = 重命名器实例.获取历史记录()
        assert len(历史) == 1
        assert 历史[0].成功
    
    def test_重命名文件_文件名冲突(self, tmp_path):
        """测试重命名时文件名冲突的处理"""
        # 创建原文件
        原文件 = tmp_path / "original.mkv"
        原文件.write_text("original")
        
        # 创建目标文件（冲突）
        目标文件 = tmp_path / "新电影 (2024).mkv"
        目标文件.write_text("existing")
        
        重命名器实例 = 重命名器(预览模式=False)
        
        媒体文件 = MediaFile(
            path=原文件,
            original_name="original.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="新电影",
            year=2024,
        )
        
        规则 = RenameRule(
            name="测试规则",
            description="测试",
            template="{{ title }} ({{ year }})",
            media_type=MediaType.MOVIE,
        )
        
        成功, 错误 = 重命名器实例.重命名文件(媒体文件, 规则)
        
        assert 成功
        
        # 应该创建了带数字后缀的新文件
        assert not 原文件.exists()
        assert 目标文件.exists()  # 原有文件不应被覆盖
        
        新文件 = 媒体文件.path
        assert 新文件.exists()
        assert "_1" in 新文件.name  # 应该有数字后缀
    
    def test_批量重命名(self, tmp_path):
        """测试批量重命名"""
        # 创建多个测试文件
        文件1 = tmp_path / "file1.mkv"
        文件2 = tmp_path / "file2.mkv"
        文件3 = tmp_path / "file3.mkv"
        
        文件1.write_text("test1")
        文件2.write_text("test2")
        文件3.write_text("test3")
        
        重命名器实例 = 重命名器(预览模式=False)
        
        媒体文件列表 = [
            MediaFile(
                path=文件1,
                original_name="file1.mkv",
                extension=".mkv",
                media_type=MediaType.MOVIE,
                title="电影1",
                year=2021,
            ),
            MediaFile(
                path=文件2,
                original_name="file2.mkv",
                extension=".mkv",
                media_type=MediaType.MOVIE,
                title="电影2",
                year=2022,
            ),
            MediaFile(
                path=文件3,
                original_name="file3.mkv",
                extension=".mkv",
                media_type=MediaType.TV_SHOW,  # 类型不匹配，应该被跳过
                title="电视剧3",
                year=2023,
            ),
        ]
        
        规则 = RenameRule(
            name="测试规则",
            description="测试",
            template="{{ title }} ({{ year }})",
            media_type=MediaType.MOVIE,
        )
        
        结果 = 重命名器实例.批量重命名(媒体文件列表, 规则)
        
        assert 结果["总数"] == 3
        assert 结果["成功"] == 2
        assert 结果["失败"] == 0
        assert 结果["跳过"] == 1
        assert len(结果["详情"]) == 3
    
    def test_撤销重命名(self, tmp_path):
        """测试撤销重命名"""
        # 创建测试文件
        原文件 = tmp_path / "original.mkv"
        原文件.write_text("test")
        
        重命名器实例 = 重命名器(预览模式=False, 创建备份=True)
        
        媒体文件 = MediaFile(
            path=原文件,
            original_name="original.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="电影",
            year=2024,
        )
        
        规则 = RenameRule(
            name="测试规则",
            description="测试",
            template="{{ title }}",
            media_type=MediaType.MOVIE,
        )
        
        # 执行重命名
        成功, _ = 重命名器实例.重命名文件(媒体文件, 规则)
        assert 成功
        
        新文件 = 媒体文件.path
        assert 新文件.exists()
        assert not 原文件.exists()
        
        # 撤销重命名
        成功, 错误 = 重命名器实例.撤销重命名()
        assert 成功
        assert 错误 is None
        
        # 原文件应该恢复
        assert 原文件.exists()
        assert not 新文件.exists()
        
        # 历史记录应该被清空
        assert len(重命名器实例.获取历史记录()) == 0
    
    def test_保存和加载历史记录(self, tmp_path):
        """测试保存和加载历史记录"""
        重命名器实例 = 重命名器()
        
        # 添加一些历史记录
        历史1 = RenameHistory(
            原始路径=Path("/test/old1.mkv"),
            新路径=Path("/test/new1.mkv"),
            成功=True,
        )
        历史2 = RenameHistory(
            原始路径=Path("/test/old2.mkv"),
            新路径=Path("/test/new2.mkv"),
            成功=False,
            错误信息="测试错误",
        )
        
        重命名器实例._历史记录.append(历史1)
        重命名器实例._历史记录.append(历史2)
        
        # 保存到文件
        历史文件 = tmp_path / "history.json"
        assert 重命名器实例.保存历史到文件(历史文件)
        assert 历史文件.exists()
        
        # 加载到新实例
        新重命名器 = 重命名器()
        assert 新重命名器.从文件加载历史(历史文件)
        
        历史记录 = 新重命名器.获取历史记录()
        assert len(历史记录) == 2
        assert 历史记录[0].成功
        assert not 历史记录[1].成功
        assert 历史记录[1].错误信息 == "测试错误"
    
    def test_清空历史记录(self):
        """测试清空历史记录"""
        重命名器实例 = 重命名器()
        
        历史 = RenameHistory(
            原始路径=Path("/test/old.mkv"),
            新路径=Path("/test/new.mkv"),
        )
        重命名器实例._历史记录.append(历史)
        
        assert len(重命名器实例.获取历史记录()) == 1
        
        重命名器实例.清空历史记录()
        assert len(重命名器实例.获取历史记录()) == 0
    
    def test_英文别名方法(self, tmp_path):
        """测试英文别名方法"""
        test_file = tmp_path / "test.mkv"
        test_file.write_text("test")
        
        renamer = Renamer(预览模式=True)
        
        media_file = MediaFile(
            path=test_file,
            original_name="test.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="Test Movie",
            year=2024,
        )
        
        rule = RenameRule(
            name="Test",
            description="Test",
            template="{{ title }}",
            media_type=MediaType.MOVIE,
        )
        
        success, new_name, error = renamer.generate_new_filename(media_file, rule)
        assert success
        
        success, error = renamer.rename_file(media_file, rule)
        assert success


class Test带目录重命名:
    """测试带目录的重命名"""
    
    def test_电视剧分季目录重命名(self, tmp_path):
        """测试电视剧按季分目录重命名"""
        # 创建测试文件
        原文件 = tmp_path / "show.mkv"
        原文件.write_text("test")
        
        重命名器实例 = 重命名器(预览模式=False)
        
        媒体文件 = MediaFile(
            path=原文件,
            original_name="show.mkv",
            extension=".mkv",
            media_type=MediaType.TV_SHOW,
            title="绝命毒师",
            season_number=1,
            episode_number=1,
        )
        
        规则 = RenameRule(
            name="分季目录",
            description="测试",
            template="{{ title }}/Season {{ season|填充(2) }}/{{ title }} S{{ season|填充(2) }}E{{ episode|填充(2) }}",
            media_type=MediaType.TV_SHOW,
        )
        
        成功, 错误 = 重命名器实例.重命名文件(媒体文件, 规则)
        
        assert 成功
        assert 错误 is None
        
        # 检查新文件路径
        新文件 = 媒体文件.path
        assert 新文件.exists()
        assert "绝命毒师" in 新文件.parts
        assert "Season 01" in 新文件.parts
        assert "S01E01" in 新文件.name
