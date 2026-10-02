# 🌐 다국어 번역기

입력한 글을 영어 · 일본어 · 베트남어로 번역하는 Streamlit 앱입니다. (OpenAI `gpt-6-astra` 사용)

## 설치

```bash
pip install -r requirements.txt
```

`.env.example`을 복사해 `.env`를 만들고 API 키를 입력합니다.

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-6-astra
```

## 로컬 실행

```bash
streamlit run app.py
```

브라우저에서 http://localhost:8501 을 엽니다.

## 배포 (Streamlit Community Cloud)

1. 프로젝트를 GitHub 저장소에 푸시합니다.
   - `.env`가 커밋되지 않았는지 꼭 확인하세요 (`.gitignore`에 포함되어 있습니다).
2. https://share.streamlit.io 에 GitHub 계정으로 로그인한 뒤 **Create app**을 누릅니다.
3. 저장소와 브랜치를 선택하고, **Main file path**에 `app.py`를 입력합니다.
4. **Advanced settings → Secrets**에 아래 내용을 입력합니다. (`.streamlit/secrets.toml.example` 참고)
   ```toml
   OPENAI_API_KEY = "sk-..."
   OPENAI_MODEL = "gpt-6-astra"
   ```
5. **Deploy**를 누릅니다. 배포 후 Secrets는 앱 메뉴의 **Settings → Secrets**에서 수정할 수 있습니다.

앱은 설정값을 Streamlit Secrets → 환경 변수(`.env`) 순서로 찾으므로, 배포 환경에서는 `.env` 없이 Secrets만으로 동작합니다.

## 참고

- 번역 시간은 글 길이에 비례합니다. 짧은 문장은 3~4초, 500자는 약 17초, 5,000자는 2분 이상 걸릴 수 있습니다.
- `.streamlit/config.toml`의 `font`에는 글꼴 URL을 하나만 지정할 수 있습니다. 일본어 글꼴(Noto Sans JP)은 `app.py`의 CSS에서 불러옵니다.
