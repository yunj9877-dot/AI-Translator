import streamlit as st  # 웹 화면 구성 도구 라이브러리
import os  # 시스템 설정 도구 모듈
from langchain_openai import ChatOpenAI  # OpenAI AI 연결 부품 모듈
from langchain_core.prompts import PromptTemplate  # 번역 질문지 양식 생성 모듈
from langchain_core.output_parsers import StrOutputParser  # 답변 텍스트 정리 모듈
from langchain_community.callbacks.manager import get_openai_callback  # 토큰 및 비용 계산기 모듈

# --- [1] 웹페이지 설정 ---
st.set_page_config(page_title="윤정의 AI 번역기", page_icon="🌐")  # 브라우저 타이틀 설정 라이브러리 함수

# --- [2] 세션 상태 초기화 ---
if 'history' not in st.session_state:
    st.session_state.history = []  # 번역 기록 저장 공간 모듈 변수
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0  # 입력창 초기화용 카운터 모듈 변수

# --- [3] 사이드바 설정 ---
with st.sidebar:
    st.title("⚙️ 설정 및 보안")
    
    # 초기화 시 이름(key)을 바꿔 에러를 방지하는 입력창 라이브러리 함수
    openai_api_key = st.text_input(
        "OpenAI API Key", 
        type="password", 
        placeholder="sk-...",
        key=f"api_key_{st.session_state.reset_counter}"
    )
    
    if st.button("API 키 해제 (초기화)"):
        st.session_state.reset_counter += 1  # 카운터 증가 모듈 변수 조작
        st.session_state.history = []  # 저장 기록 삭제 모듈 변수 조작
        st.rerun()  # 화면 새로고침 라이브러리 함수
        
    st.divider()
    langs = ["Korean", "Japanese", "Chinese", "English", "Spanish", "French"]
    language = st.radio('번역 언어 선택:', langs)  # 언어 선택 라디오 버튼 라이브러리 함수

# --- [4] 메인 화면 UI ---
st.header("🌐 윤정의 AI 번역기")
prompt_text = st.text_area('번역할 문장을 입력하세요:', height=120)  # 문장 입력 상자 라이브러리 함수

# --- [5] 번역 실행 로직 ---
if st.button("번역 시작"):
    if not openai_api_key:
        st.error("⚠️ 사이드바에 API Key를 입력해 주세요!")
    elif not prompt_text.strip():
        st.warning("⚠️ 내용을 입력해 주세요.")
    else:
        try:
            with st.spinner('번역 중...'):  # 로딩 애니메이션 표시 라이브러리 함수
                # AI 모델 설정 모듈 클래스
                llm = ChatOpenAI(model_name='gpt-4o-mini', temperature=0.3, openai_api_key=openai_api_key)
                prompt = PromptTemplate.from_template("Translate to {target_lang}: {trans}")
                
                # 질문->AI->정리 연결 파이프라인 모듈 기능
                chain = prompt | llm | StrOutputParser()

                with get_openai_callback() as cb:  # 토큰 및 비용 실시간 감시 모듈 함수
                    response = chain.invoke({"target_lang": language, "trans": prompt_text})
                    
                    st.success(f"✅ {language} 번역 완료")
                    st.info(response)
                    
                    # 작은 글씨로 사용량 출력 라이브러리 함수
                    st.caption(f"📊 사용량: {cb.total_tokens} tokens | 예상 비용: ${cb.total_cost:.5f}")

                    # --- 번역 기록 저장 ---
                    new_record = {
                        "input": (prompt_text[:30] + "..") if len(prompt_text) > 30 else prompt_text, 
                        "output": response, 
                        "lang": language
                    }
                    st.session_state.history.insert(0, new_record)  # 기록 추가 모듈 변수 조작
                    if len(st.session_state.history) > 3:
                        st.session_state.history = st.session_state.history[:3]  # 기록 개수 제한 모듈 변수 조작
                
        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")

# --- [6] 최근 번역 기록 표시 ---
st.divider()
st.subheader("📜 최근 번역 기록 (3개)")

if st.session_state.history:
    for i, record in enumerate(st.session_state.history):
        # 접이식 상자 기록 표시 라이브러리 함수
        with st.expander(f"{i+1}. [{record['lang']}] {record['input']}"):
            st.write(record['output'])
else:
    st.write("기록 없음")