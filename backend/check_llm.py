from openai import OpenAI

from config import load_llm_config

def main() -> None:
    """测试调用大模型接口。"""
    config = load_llm_config()  # 从环境变量中加载大模型配置参数。
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    reponse = client.chat.completions.create(
        model=config.model_name,
        messages=[
            {"role": "user", "content": "请用一句话介绍自己。"},
        ],
    )

    print("大模型返回的内容：")
    print(reponse.choices[0].message.content)  # 打印大模型返回的第一条消息内容。

if __name__ == "__main__":
    main()  # 运行测试函数