#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class PlotGen:
    def __init__(self, num=5):
        self.num = num
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ref_path = os.path.join(base_dir, 'references/processed/lovewar.json')
        with open(ref_path, 'r', encoding='utf-8') as f:
            self.references = json.load(f)
    
    def generate(self):
        import random
        import string
        
        # 랜덤 시드 문자열 생성 (매번 다른 응답 유도)
        seed = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # 랜덤 변형 요소들
        variations = [
            f"[시드: {seed}]",
            f"(변형코드: {random.randint(1000, 9999)})",
            f"#버전{random.randint(1, 100)}",
            f"※ 고유번호: {random.randint(100000, 999999)}",
            f"∞ 변화값: {random.random():.6f}"
        ]
        
        # 랜덤하게 1-2개 선택
        selected_variations = random.sample(variations, random.randint(1, 2))
        variation_text = ' '.join(selected_variations)
        
        # 레퍼런스에서 랜덤하게 30개 선택
        num_refs = min(30, len(self.references))
        selected_references = random.sample(self.references, num_refs)
        
        prompt = f"""첨부된 JSON 파일을 참고하여 새로운 이야기 {self.num}개를 4~5줄 분량으로 제목과 함께 생성해주세요.

{variation_text}

아래의 정확한 JSON 형식으로만 응답하세요. 다른 설명이나 텍스트는 포함하지 마세요:
{{
    "stories": [
        {{
            "title": "제목을 여기에",
            "plot": "줄거리를 여기에. 줄바꿈이 필요하면 \\n을 사용하세요."
        }}
    ]
}}

주의사항:
- 반드시 유효한 JSON 형식으로만 응답
- 주석(// 또는 /* */) 사용 금지
- 마지막 항목 뒤에 쉼표(,) 금지
- 문자열 내의 따옴표는 \\"로 이스케이프
- 총 {self.num}개의 스토리 생성"""
        
        return {
            "prompt": prompt,
            "references": selected_references  # 30개만 전달
        }


if __name__ == "__main__":
    gen = PlotGen(num=5)
    result = gen.generate()
    print(result["prompt"])
    print(f"\n레퍼런스 개수: {len(result['references'])}")