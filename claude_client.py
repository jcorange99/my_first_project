import json
import random
import time
from typing import Any

import anthropic

MODEL = "claude-opus-4-7"

SYSTEM_PROMPT = """你是一个产品需求拆解助手。

你的任务是把用户输入的一段混乱需求、沟通记录或产品想法，整理成结构化结果。

请严格输出以下内容：
1. summary：一句话总结这段需求的核心目标
2. core_requirements：3-6条核心需求
3. risks：2-5条潜在风险或实施难点
4. questions_to_confirm：2-5条还需要和客户或团队确认的问题
5. next_steps：2-5条建议下一步动作

要求：
- 内容要具体、简洁、可执行
- 不要编造不存在的背景事实
- 如果输入信息不足，也要明确指出不确定点
- 输出必须是合法 JSON 对象，不要输出 markdown 代码块，不要输出解释文字"""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "core_requirements": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "questions_to_confirm": {"type": "array", "items": {"type": "string"}},
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "summary",
        "core_requirements",
        "risks",
        "questions_to_confirm",
        "next_steps",
    ],
    "additionalProperties": False,
}


class ClaudeClientError(Exception):
    pass


def usage_to_dict(response: Any) -> dict[str, int | None]:
    usage = response.usage
    return {
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "cache_creation_input_tokens": getattr(usage, "cache_creation_input_tokens", None),
        "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", None),
    }


def retry_delay_seconds(attempt: int, retry_after_header: str | None = None) -> float:
    if retry_after_header:
        try:
            return max(float(retry_after_header), 0.0)
        except ValueError:
            pass
    return min((2 ** (attempt - 1)) + random.random(), 20.0)


def analyze_requirement(text: str, max_attempts: int = 3) -> tuple[dict[str, Any], dict[str, int | None]]:
    client = anthropic.Anthropic(max_retries=0)
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4000,
                thinking={"type": "adaptive"},
                output_config={
                    "effort": "high",
                    "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA},
                },
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral", "ttl": "1h"},
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"请拆解下面这段需求文本：\n\n{text.strip()}"
                            }
                        ],
                    }
                ],
            )

            if response.stop_reason == "refusal":
                raise ClaudeClientError("模型拒绝了这次请求，请换一段更偏产品或业务的文本再试。")
            if response.stop_reason == "max_tokens":
                raise ClaudeClientError("输出被截断了，请缩短输入内容后重试。")

            content_text = next((block.text for block in response.content if block.type == "text"), "")
            if not content_text.strip():
                raise ClaudeClientError("模型返回了空结果。")

            data = json.loads(content_text)
            return data, usage_to_dict(response)
        except anthropic.AuthenticationError as error:
            raise ClaudeClientError(f"API Key 无效：{error}") from error
        except anthropic.PermissionDeniedError as error:
            raise ClaudeClientError(f"当前 API Key 没有权限：{error}") from error
        except anthropic.NotFoundError as error:
            raise ClaudeClientError(f"模型或接口不可用：{error}") from error
        except anthropic.BadRequestError as error:
            raise ClaudeClientError(f"请求格式有误：{error}") from error
        except anthropic.RateLimitError as error:
            last_error = error
            if attempt == max_attempts:
                break
            time.sleep(retry_delay_seconds(attempt, error.response.headers.get("retry-after", "")))
        except anthropic.APIConnectionError as error:
            last_error = error
            if attempt == max_attempts:
                break
            time.sleep(retry_delay_seconds(attempt))
        except anthropic.APIStatusError as error:
            last_error = error
            if error.status_code >= 500 or error.status_code == 529:
                if attempt == max_attempts:
                    break
                time.sleep(retry_delay_seconds(attempt))
                continue
            raise ClaudeClientError(f"API 状态异常：{error}") from error
        except json.JSONDecodeError as error:
            last_error = error
            if attempt == max_attempts:
                break
            time.sleep(retry_delay_seconds(attempt))
        except ClaudeClientError:
            raise

    raise ClaudeClientError(f"请求失败，请稍后重试。最后一次错误：{last_error}")
