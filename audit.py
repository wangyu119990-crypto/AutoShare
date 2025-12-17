# audit.py - 内容安全审查模块

class ContentAuditor:
    """内容安全审查器，用于检查小红书发布内容的合规性"""

    # 违规词库 - 小红书禁止使用的绝对化表述
    FORBIDDEN_WORDS = [
        "最", "第一", "唯一", "吊打", "秒杀", "别再", "强迫",
        "智商税", "垃圾", "史上", "前所未有", "颠覆", "革命性",
        "完爆", "完胜", "无敌", "天下第一", "最佳", "顶级",
        "绝对", "必然", "肯定", "一定", "必须", "只能",
        "千万不要", "切记", "牢记", "记住"
    ]

    @staticmethod
    def audit_content(content):
        """
        审查内容是否包含违规词汇

        Args:
            content (str): 需要审查的文本内容

        Returns:
            tuple: (is_safe: bool, error_message: str)
                   is_safe=True 表示内容安全，is_safe=False 表示发现违规内容
        """
        if not content or not isinstance(content, str):
            return True, ""

        found_forbidden_words = []

        for word in ContentAuditor.FORBIDDEN_WORDS:
            if word in content:
                found_forbidden_words.append(word)

        if found_forbidden_words:
            error_msg = f"🚫 发现违规词汇: {', '.join(found_forbidden_words)}\n"
            error_msg += "小红书禁止使用绝对化表述，请修改后再发布。"
            return False, error_msg

        return True, ""

    @staticmethod
    def audit_data_content():
        """
        审查 data.py 中的所有内容

        Returns:
            tuple: (is_safe: bool, error_message: str)
        """
        try:
            import data

            # 审查封面摘要
            summary_safe, summary_error = ContentAuditor.audit_content(data.cover_data.get("summary", ""))
            if not summary_safe:
                return False, f"封面摘要{summary_error}"

            # 审查文章标题
            title_safe, title_error = ContentAuditor.audit_content(data.article_title)
            if not title_safe:
                return False, f"文章标题{title_error}"

            # 审查简单榜单文本
            list_safe, list_error = ContentAuditor.audit_content(data.simple_list_text)
            if not list_safe:
                return False, f"榜单文本{list_error}"

            # 审查详细文章内容
            content_safe, content_error = ContentAuditor.audit_content(data.article_content_formatted)
            if not content_safe:
                return False, f"文章内容{content_error}"

            return True, "✅ 内容审查通过，所有内容符合小红书发布规范"

        except Exception as e:
            return False, f"❌ 审查过程中发生错误: {str(e)}"

def perform_content_audit():
    """
    执行完整的内容审查流程

    Raises:
        SystemExit: 如果发现违规内容，程序将退出
    """
    print("🔍 正在进行内容安全审查...")

    auditor = ContentAuditor()
    is_safe, message = auditor.audit_data_content()

    if is_safe:
        print(message)
        return True
    else:
        print(message)
        print("🛑 为保护账号安全，程序已停止。请修改违规内容后重试。")
        raise SystemExit(1)

if __name__ == "__main__":
    # 独立运行时的测试
    perform_content_audit()
