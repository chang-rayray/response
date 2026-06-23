import os
import streamlit as st
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(page_title="OpenAI File Search", page_icon="🔍", layout="centered")

st.title("🔍 OpenAI File Search 앱")
st.markdown("Responses API와 `file_search` 도구를 활용하여 Vector Store의 문서에서 정보를 검색합니다.")

# 사이드바에서 API 키 및 Vector Store ID 설정
with st.sidebar:
    st.header("설정")
    # 환경변수에서 키를 가져오거나 사용자 입력을 받음
    default_api_key = os.environ.get("OPENAI_API_KEY", "")
    api_key = st.text_input("OpenAI API Key", value=default_api_key, type="password")
    vector_store_id = st.text_input("Vector Store ID", value="vs_6a3a7443bc2c81918014ba9548ea924e", placeholder="vs_...")

# 사용자 질문 입력
user_query = st.text_input("질문을 입력하세요:", placeholder="예: What is deep research by OpenAI?")

# 검색 버튼
if st.button("검색 실행", type="primary"):
    if not api_key:
        st.error("사이드바에서 OpenAI API Key를 입력해주세요.")
    elif not vector_store_id:
        st.error("사이드바에서 Vector Store ID를 입력해주세요.")
    elif not user_query:
        st.warning("질문을 입력해주세요.")
    else:
        # 클라이언트 초기화
        client = OpenAI(api_key=api_key)
        
        with st.spinner("검색 및 답변 생성 중..."):
            try:
                # Responses API 호출
                response = client.responses.create(
                    model="gpt-4o",
                    input=user_query,
                    tools=[{
                        "type": "file_search",
                        "vector_store_ids": [vector_store_id]
                    }]
                )
                
                # 응답 처리
                for output_item in response.output:
                    if output_item.type == "file_search_call":
                        with st.expander("파일 검색 정보 확인"):
                            st.write(f"**Call ID:** {output_item.id}")
                            st.write(f"**상태:** {output_item.status}")
                            st.write(f"**검색 쿼리:** {output_item.queries}")
                            
                    elif output_item.type == "message":
                        for content_block in output_item.content:
                            if content_block.type == "output_text":
                                st.success("답변 생성 완료!")
                                st.markdown("### 📝 결과")
                                st.write(content_block.text)
                                
                                # 참고 문헌 (Annotations) 처리
                                if hasattr(content_block, 'annotations') and content_block.annotations:
                                    st.markdown("---")
                                    st.markdown("### 📚 참고 문헌")
                                    for annotation in content_block.annotations:
                                        if annotation.type == "file_citation":
                                            file_name = getattr(annotation, 'filename', '알 수 없음')
                                            st.markdown(f"- **파일명**: `{file_name}` (File ID: `{annotation.file_id}`)")
                                            
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
