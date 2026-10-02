from ddgs import DDGS
from ddgs.exceptions import DDGSException

def search_web(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """搜索网页，并整理搜索结果。"""
    # DDGS 在没有搜索结果时会抛出异常；将这种情况作为空结果返回，
    # 避免一个任务没有结果就让整个研究请求失败。
    try:
        results = DDGS().text(query, max_results=max_results)
    except DDGSException:
        return []

    return [
        {
            "title": item.get("title", ""),
            "url": item.get("href", ""),
            "snippet": item.get("body", ""),
        }
        for item in results
    ]
