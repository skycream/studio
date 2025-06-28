import json
import os

def process_lovewar_reference():
    """러브워 레퍼런스 데이터 정제"""
    
    # 원본 파일 읽기
    with open('references/raw/lovewar_raw.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 정제된 데이터 생성
    processed_data = []
    
    for item in raw_data:
        processed_item = {
            "title": item.get("title", ""),
            "plot": item.get("plot", ""),
            "tags": []  # 추후 태그 추가 가능
        }
        
        # 제목에서 태그 추출 (예시)
        if "의처증" in processed_item["title"]:
            processed_item["tags"].append("의처증")
        if "불륜" in processed_item["plot"] or "외도" in processed_item["plot"]:
            processed_item["tags"].append("불륜")
        if "시어머니" in processed_item["plot"] or "시댁" in processed_item["plot"]:
            processed_item["tags"].append("고부갈등")
        if "이혼" in processed_item["plot"]:
            processed_item["tags"].append("이혼")
        
        processed_data.append(processed_item)
    
    # 정제된 데이터 저장
    with open('references/processed/lovewar.json', 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"처리 완료: {len(processed_data)}개의 레퍼런스")
    print(f"저장 위치: references/processed/lovewar.json")

if __name__ == "__main__":
    process_lovewar_reference()