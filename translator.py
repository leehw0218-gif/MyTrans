"""OpenAI를 사용해 입력 텍스트를 영어·일본어·베트남어로 번역한다."""

import json
import os

import openai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gpt-6-astra"
MAX_ATTEMPTS = 2  # 최초 1회 + 응답 형식 오류 시 재시도 1회

LANGUAGES = {
    "english": "🇺🇸 English",
    "japanese": "🇯🇵 日本語",
    "vietnamese": "🇻🇳 Tiếng Việt",
}

SYSTEM_PROMPT = """You are a professional translator.
Detect the language of the user's text automatically and translate it into English, Japanese, and Vietnamese.
Preserve meaning, tone, and line breaks. Keep numbers, URLs, emojis, and proper nouns intact. Do not add explanations.
If the text is already in one of the target languages, return a naturally polished version of the original for that language.
Respond ONLY in JSON: {"english": "...", "japanese": "...", "vietnamese": "..."}"""


class TranslationError(Exception):
    """사용자에게 그대로 보여줄 수 있는 한국어 메시지를 담는 번역 오류."""


class MissingAPIKeyError(TranslationError):
    pass


def _get_setting(name: str) -> str | None:
    """st.secrets → 환경 변수(.env) 순서로 설정값을 찾는다."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except FileNotFoundError:
        pass
    except Exception:
        # secrets.toml이 없거나 형식이 잘못된 경우 환경 변수로 넘어간다.
        pass
    return os.getenv(name) or None


def get_api_key() -> str | None:
    return _get_setting("OPENAI_API_KEY")


def get_model() -> str:
    return _get_setting("OPENAI_MODEL") or DEFAULT_MODEL


def _parse(content: str | None) -> dict:
    data = json.loads(content or "")
    if not isinstance(data, dict):
        raise ValueError("JSON 객체가 아님")
    missing = [key for key in LANGUAGES if not isinstance(data.get(key), str)]
    if missing:
        raise ValueError(f"누락된 키: {missing}")
    return {key: data[key] for key in LANGUAGES}


def translate(text: str) -> dict:
    """text를 영어·일본어·베트남어로 번역해 {"english", "japanese", "vietnamese"} 형태로 반환한다."""
    api_key = get_api_key()
    if not api_key:
        raise MissingAPIKeyError("OPENAI_API_KEY가 설정되지 않았습니다.")

    client = openai.OpenAI(api_key=api_key)
    model = get_model()

    for _ in range(MAX_ATTEMPTS):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
            )
        except openai.AuthenticationError:
            raise TranslationError("API 키가 올바르지 않습니다. OPENAI_API_KEY를 확인해주세요.") from None
        except openai.PermissionDeniedError:
            raise TranslationError("이 API 키로는 해당 모델을 사용할 권한이 없습니다.") from None
        except openai.NotFoundError:
            raise TranslationError(f"모델 '{model}'을(를) 찾을 수 없습니다. OPENAI_MODEL 설정을 확인해주세요.") from None
        except openai.RateLimitError:
            raise TranslationError("요청 한도 또는 사용량을 초과했습니다. 잠시 후 다시 시도하거나 결제 정보를 확인해주세요.") from None
        except (openai.APIConnectionError, openai.APITimeoutError):
            raise TranslationError("OpenAI 서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요.") from None
        except openai.APIStatusError as e:
            raise TranslationError(f"번역 요청 중 오류가 발생했습니다. (HTTP {e.status_code})") from None

        try:
            return _parse(response.choices[0].message.content)
        except (ValueError, IndexError):
            continue  # json.JSONDecodeError는 ValueError의 하위 클래스

    raise TranslationError("번역 결과를 해석하지 못했습니다. 다시 시도해주세요.")
