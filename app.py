import streamlit as st

from translator import LANGUAGES, TranslationError, get_api_key, get_model, translate

MAX_CHARS = 5000
HISTORY_LIMIT = 10
CARD_HEIGHT = 300
LONG_TEXT_CHARS = 1000  # 실측: 500자 약 17초, 5,000자 약 130초

st.set_page_config(page_title="다국어 번역기", page_icon="🌐", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
    .block-container { padding-top: 2.5rem; max-width: 1200px; }
    .char-count { text-align: right; font-size: 0.85rem; opacity: 0.65; margin-top: -0.5rem; }
    .char-count.over { color: #E5484D; opacity: 1; font-weight: 700; }
    /* 결과 카드: 폭이 좁으면(태블릿 + 사이드바) 3열을 유지하지 않고 다음 줄로 넘긴다 */
    .st-key-results [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
    .st-key-results [data-testid="stColumn"] { flex: 1 1 240px; min-width: 240px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.session_state.setdefault("history", [])


def clear_history():
    st.session_state["history"] = []


# ---------- 사이드바 ----------
with st.sidebar:
    st.header("📖 사용 방법")
    st.markdown(
        "1. 번역할 내용을 입력합니다.\n"
        "2. **번역하기** 버튼을 누릅니다.\n"
        "3. 결과 카드 오른쪽 위 아이콘으로 복사합니다.\n\n"
        f"입력 언어는 자동으로 감지되며, 최대 {MAX_CHARS:,}자까지 번역할 수 있습니다."
    )
    st.divider()
    st.markdown(f"**사용 모델** `{get_model()}`")
    st.divider()

    history = st.session_state["history"]
    st.subheader(f"🕘 최근 번역 기록 ({len(history)})")
    if history:
        for item in history:
            source = item["source"].strip().replace("\n", " ")
            title = source if len(source) <= 24 else source[:24] + "…"
            with st.expander(title):
                for key, label in LANGUAGES.items():
                    st.caption(label)
                    st.text(item[key])
        st.button("기록 지우기", icon="🗑️", on_click=clear_history, width="stretch")
    else:
        st.caption("아직 번역 기록이 없습니다.")

# ---------- 본문 ----------
st.title("🌐 다국어 번역기")
st.caption("입력한 글을 영어 · 일본어 · 베트남어로 한 번에 번역합니다")

if not get_api_key():
    st.error(
        "OPENAI_API_KEY가 설정되지 않았습니다. "
        "로컬에서는 .env 파일에, 배포 환경에서는 Streamlit Secrets에 API 키를 등록해주세요."
    )
    st.stop()

text = st.text_area(
    "번역할 내용",
    placeholder="번역할 내용을 입력하세요...",
    height=200,
    label_visibility="collapsed",
)
char_count = len(text)
over_class = " over" if char_count > MAX_CHARS else ""
st.markdown(
    f'<div class="char-count{over_class}">{char_count:,} / {MAX_CHARS:,}자</div>',
    unsafe_allow_html=True,
)

with st.container(horizontal_alignment="center"):
    clicked = st.button("번역하기", type="primary", icon="✨", width=220)

if clicked:
    if not text.strip():
        st.warning("번역할 내용을 입력해주세요.")
    elif char_count > MAX_CHARS:
        st.error(f"입력은 최대 {MAX_CHARS:,}자까지 가능합니다. (현재 {char_count:,}자)")
    else:
        try:
            spinner_text = "번역 중입니다..."
            if char_count > LONG_TEXT_CHARS:
                spinner_text += " 글이 길어 1~2분 정도 걸릴 수 있어요. 창을 닫거나 버튼을 다시 누르지 말아주세요."
            with st.spinner(spinner_text, show_time=True):
                result = translate(text)
        except TranslationError as e:
            st.error(str(e))
        else:
            st.session_state["result"] = result
            st.session_state["history"].insert(0, {"source": text, **result})
            del st.session_state["history"][HISTORY_LIMIT:]
            st.rerun()  # 사이드바 기록을 즉시 갱신

st.write("")
result = st.session_state.get("result")
columns = st.container(key="results").columns(len(LANGUAGES), gap="medium")
for column, (key, label) in zip(columns, LANGUAGES.items()):
    with column:
        with st.container(border=True, height=CARD_HEIGHT):
            st.markdown(f"#### {label}")
            if result:
                st.code(result[key], language=None, wrap_lines=True)
            else:
                st.caption("번역 결과가 여기에 표시됩니다.")
