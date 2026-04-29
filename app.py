import streamlit as st

from claude_client import ClaudeClientError, analyze_requirement

st.set_page_config(page_title="需求拆解助手", page_icon="🧩", layout="centered")

st.title("需求拆解助手")
st.caption("把混乱的客户需求、会议记录或产品想法，快速整理成结构化输出。")

with st.sidebar:
    st.subheader("使用方式")
    st.write("1. 粘贴一段需求描述")
    st.write("2. 点击“开始拆解”")
    st.write("3. 查看核心需求、风险点和下一步建议")
    st.info("请先在环境变量中配置 ANTHROPIC_API_KEY")

sample_text = """客户想做一个内部知识库系统，给销售和客服一起用。希望支持权限控制、全文搜索、FAQ自动整理，还希望后面接入企业微信。现在最大的问题是资料分散，大家经常找不到最新版本。客户希望先做一个能用的版本，两个月内上线。"""

text = st.text_area(
    "请输入需求文本",
    value=sample_text,
    height=220,
    placeholder="比如：一段客户沟通记录、项目需求草稿、会议纪要……",
)

if st.button("开始拆解", type="primary", use_container_width=True):
    if not text.strip():
        st.warning("请先输入内容。")
    else:
        with st.spinner("Claude 正在拆解需求..."):
            try:
                result, usage = analyze_requirement(text)
            except ClaudeClientError as error:
                st.error(str(error))
            else:
                st.success("拆解完成")

                st.subheader("一句话总结")
                st.write(result.get("summary", ""))

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("核心需求")
                    for item in result.get("core_requirements", []):
                        st.write(f"- {item}")
                with col2:
                    st.subheader("潜在风险")
                    for item in result.get("risks", []):
                        st.write(f"- {item}")

                st.subheader("待确认问题")
                for item in result.get("questions_to_confirm", []):
                    st.write(f"- {item}")

                st.subheader("建议下一步")
                for item in result.get("next_steps", []):
                    st.write(f"- {item}")

                with st.expander("查看 token 使用情况"):
                    st.json(usage)
