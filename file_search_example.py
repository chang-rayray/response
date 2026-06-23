import os
import getpass
from openai import OpenAI

def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = getpass.getpass("OpenAI API Key가 설정되지 않았습니다. API Key를 입력해주세요: ")
    return api_key

def file_search_response_api_query(user_query, vector_store_id, api_key):
    client = OpenAI(api_key=api_key)
    print(f"\n질문: {user_query}")
    print(f"Responses API를 호출 중 (file_search 활성화, Vector Store ID: {vector_store_id})...")
    
    # Responses API를 사용한 텍스트 생성 예제 (파일 검색 도구 포함)
    response = client.responses.create(
        model="gpt-4o", # 또는 gpt-4o-mini 등 지원되는 모델
        input=user_query,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id]
        }]
    )
    
    print("\n--- [전체 응답 객체 확인] ---")
    print(response)
    print("\n--- [답변 결과] ---")
    
    # 응답 구조(output 리스트)를 순회하며 출력합니다.
    for output_item in response.output:
        if output_item.type == "file_search_call":
            print(f"[파일 검색 호출 됨] ID: {output_item.id}, Status: {output_item.status}")
            print(f"검색 쿼리: {output_item.queries}")
            
        elif output_item.type == "message":
            for content_block in output_item.content:
                if content_block.type == "output_text":
                    print("\n[생성된 텍스트]:")
                    print(content_block.text)
                    
                    # File Search 결과의 출처(Annotations)가 있다면 출력합니다.
                    if hasattr(content_block, 'annotations') and content_block.annotations:
                        print("\n[참고 문헌 (Annotations)]:")
                        for annotation in content_block.annotations:
                            if annotation.type == "file_citation":
                                print(f"- File ID: {annotation.file_id}, Filename: {getattr(annotation, 'filename', 'N/A')}")
                                
if __name__ == "__main__":
    # 보안을 위해 하드코딩된 키 대신 환경 변수 사용을 권장합니다.
    api_key = os.environ.get("OPENAI_API_KEY", "")
    VECTOR_STORE_ID = "vs_6a3a7443bc2c81918014ba9548ea924e"
    
    if not api_key:
        import getpass
        api_key = getpass.getpass("OpenAI API Key가 설정되지 않았습니다. API Key를 입력해주세요: ")
        
    # 터미널에서 직접 질문을 입력받습니다.
    query = input("\n질문을 입력하세요 (예: What is deep research by OpenAI?): ")
    if not query.strip():
        query = "What is deep research by OpenAI?"
        
    try:
        file_search_response_api_query(query, VECTOR_STORE_ID, api_key)
    except Exception as e:
        print("에러 발생:", e)
