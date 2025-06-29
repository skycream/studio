#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class CharacterDetailGen:
    def __init__(self):
        # 섹션 타입 정의
        self.section_types = [
            'relationship',      # 관계 다이나믹스
            'background',        # 개인 배경/트라우마
            'shared_event',      # 공유된 핵심 사건
            'daily_life',        # 일상의 디테일
            'secrets'           # 비밀과 욕망
        ]
        
        # 섹션별 한국어 이름
        self.section_names = {
            'relationship': '관계 다이나믹스',
            'background': '개인 배경과 트라우마',
            'shared_event': '공유된 핵심 사건',
            'daily_life': '일상의 디테일',
            'secrets': '비밀과 욕망'
        }
    
    def generate_section(self, section_type, plot_data, characters_data, previous_selections=None):
        """
        특정 섹션에 대한 3가지 옵션 생성
        
        section_type: 생성할 섹션 타입
        plot_data: 1단계에서 선택된 줄거리
        characters_data: 2단계에서 확정된 캐릭터 정보
        previous_selections: 이전 섹션에서 선택한 내용들
        """
        
        # 기본 정보 구성
        plot_text = plot_data.get('plot', '')
        title = plot_data.get('title', '')
        
        # 캐릭터 정보 정리
        character_info = ""
        for char in characters_data:
            character_info += f"\n- {char['name']} ({char['gender']}, {char['age']}세, {char['job']}, {char['mbti']})"
            character_info += f"\n  특징: {char['trait']}"
            character_info += f"\n  성격: {char['personality_analysis']}\n"
        
        # 이전 선택사항 정리
        previous_info = ""
        if previous_selections:
            for section, selection in previous_selections.items():
                section_name = self.section_names.get(section, section)
                previous_info += f"\n【{section_name}】\n{json.dumps(selection, ensure_ascii=False, indent=2)}\n"
        
        # 섹션별 프롬프트 생성
        if section_type == 'relationship':
            prompt = self._generate_relationship_prompt(plot_text, title, character_info, characters_data)
        elif section_type == 'background':
            prompt = self._generate_background_prompt(plot_text, title, character_info, characters_data, previous_info)
        elif section_type == 'shared_event':
            prompt = self._generate_shared_event_prompt(plot_text, title, character_info, characters_data, previous_info)
        elif section_type == 'daily_life':
            prompt = self._generate_daily_life_prompt(plot_text, title, character_info, characters_data, previous_info)
        elif section_type == 'secrets':
            prompt = self._generate_secrets_prompt(plot_text, title, character_info, characters_data, previous_info)
        else:
            raise ValueError(f"Unknown section type: {section_type}")
        
        return {
            "prompt": prompt,
            "references": [],
            "section_type": section_type
        }
    
    def _generate_relationship_prompt(self, plot_text, title, character_info, characters_data):
        """관계 다이나믹스 프롬프트"""
        
        # 인물 쌍 생성
        character_pairs = []
        char_names = [char['name'] for char in characters_data]
        for i in range(len(char_names)):
            for j in range(i+1, len(char_names)):
                character_pairs.append(f"{char_names[i]}-{char_names[j]}")
        
        prompt = f"""선택된 줄거리와 캐릭터를 바탕으로 인물 간 관계를 상세히 설정해주세요.

【줄거리】
제목: {title}
내용: {plot_text}

【등장인물】
{character_info}

【작업 지시사항】
각 인물 쌍({', '.join(character_pairs)})의 관계에 대해 3가지 다른 해석을 제시하세요.

각 옵션은 다음 요소를 포함해야 합니다:
1. 관계의 본질 (표면적 관계와 실제 관계)
2. 감정 온도 (현재의 감정 상태)
3. 권력 구조 (누가 우위에 있는가)
4. 갈등 패턴 (어떻게 싸우고 화해하는가)
5. 소통 방식 (대화, 침묵, 간접 표현 등)

JSON 형식으로 응답:
{{
    "options": [
        {{
            "option_number": 1,
            "title": "관계 유형 (예: 공생적 의존)",
            "description": "이 관계의 핵심을 한 문장으로",
            "relationships": [
                {{
                    "pair": "인물1-인물2",
                    "surface_relationship": "표면적 관계",
                    "real_relationship": "실제 관계",
                    "emotional_temperature": "감정 상태",
                    "power_structure": "권력 구조",
                    "conflict_pattern": "갈등 패턴",
                    "communication_style": "소통 방식"
                }}
            ]
        }},
        {{옵션2}},
        {{옵션3}}
    ]
}}"""
        
        return prompt
    
    def _generate_background_prompt(self, plot_text, title, character_info, characters_data, previous_info):
        """개인 배경/트라우마 프롬프트"""
        
        prompt = f"""선택된 정보를 바탕으로 각 인물의 개인적 배경과 트라우마를 설정해주세요.

【줄거리】
제목: {title}
내용: {plot_text}

【등장인물】
{character_info}

【이전 선택사항】
{previous_info}

【작업 지시사항】
각 인물의 과거사에 대해 3가지 다른 버전을 제시하세요.

각 옵션은 다음 요소를 포함해야 합니다:
1. 핵심 트라우마/상처
2. 형성 시기와 계기
3. 현재 행동에 미치는 영향
4. 방어기제
5. 숨겨진 욕구

이전에 선택한 관계 설정과 일관성을 유지하되, 각 옵션은 서로 다른 심리적 깊이를 제공해야 합니다.

JSON 형식으로 응답:
{{
    "options": [
        {{
            "option_number": 1,
            "title": "배경 유형 (예: 어린 시절의 결핍)",
            "description": "이 배경 설정의 핵심",
            "character_backgrounds": [
                {{
                    "name": "인물 이름",
                    "core_trauma": "핵심 트라우마",
                    "formation_period": "형성 시기",
                    "triggering_event": "계기가 된 사건",
                    "current_impact": "현재 영향",
                    "defense_mechanism": "방어기제",
                    "hidden_desire": "숨겨진 욕구"
                }}
            ]
        }},
        {{옵션2}},
        {{옵션3}}
    ]
}}"""
        
        return prompt
    
    def _generate_shared_event_prompt(self, plot_text, title, character_info, characters_data, previous_info):
        """공유된 핵심 사건 프롬프트"""
        
        prompt = f"""선택된 정보를 바탕으로 인물들이 공유하는 핵심 사건들을 설정해주세요.

【줄거리】
제목: {title}
내용: {plot_text}

【등장인물】
{character_info}

【이전 선택사항】
{previous_info}

【작업 지시사항】
인물들의 관계를 형성하거나 변화시킨 핵심 사건들에 대해 3가지 다른 버전을 제시하세요.

각 옵션은 다음 요소를 포함해야 합니다:
1. 2-3개의 핵심 공유 사건
2. 사건의 시기와 상황
3. 각 인물의 해석과 기억
4. 관계에 미친 영향
5. 현재까지 이어지는 여파

이전 선택사항(관계, 개인 배경)과 연결되면서도 새로운 깊이를 더해야 합니다.

JSON 형식으로 응답:
{{
    "options": [
        {{
            "option_number": 1,
            "title": "사건 유형 (예: 배신과 용서의 순환)",
            "description": "이 사건들의 핵심 주제",
            "shared_events": [
                {{
                    "event_name": "사건 이름",
                    "timing": "발생 시기",
                    "situation": "상황 설명",
                    "participants": ["참여 인물들"],
                    "interpretations": {{
                        "인물1": "인물1의 해석",
                        "인물2": "인물2의 해석"
                    }},
                    "impact": "관계에 미친 영향",
                    "current_echo": "현재까지의 여파"
                }}
            ]
        }},
        {{옵션2}},
        {{옵션3}}
    ]
}}"""
        
        return prompt
    
    def _generate_daily_life_prompt(self, plot_text, title, character_info, characters_data, previous_info):
        """일상의 디테일 프롬프트"""
        
        prompt = f"""선택된 정보를 바탕으로 인물들의 일상생활 디테일을 설정해주세요.

【줄거리】
제목: {title}
내용: {plot_text}

【등장인물】
{character_info}

【이전 선택사항】
{previous_info}

【작업 지시사항】
인물들의 일상 패턴과 생활 디테일에 대해 3가지 다른 버전을 제시하세요.

각 옵션은 다음 요소를 포함해야 합니다:
1. 하루 일과 (아침, 점심, 저녁, 밤)
2. 공간 사용 패턴 (집안에서의 영역)
3. 돈 관리와 소비 패턴
4. 스트레스 해소 방법
5. 반복되는 습관과 의례

이전 선택사항들이 일상에서 어떻게 드러나는지 구체적으로 표현하세요.

JSON 형식으로 응답:
{{
    "options": [
        {{
            "option_number": 1,
            "title": "일상 유형 (예: 분리된 평행선)",
            "description": "이 일상 패턴의 특징",
            "daily_patterns": {{
                "morning_routine": {{
                    "인물1": "인물1의 아침 루틴",
                    "인물2": "인물2의 아침 루틴",
                    "interaction": "아침 상호작용"
                }},
                "space_usage": {{
                    "territories": "각자의 영역",
                    "neutral_zones": "중립 지대",
                    "contested_areas": "갈등 지역"
                }},
                "money_patterns": {{
                    "income_control": "수입 관리",
                    "spending_habits": "지출 패턴",
                    "hidden_expenses": "숨겨진 지출"
                }},
                "stress_relief": {{
                    "인물1": "인물1의 스트레스 해소법",
                    "인물2": "인물2의 스트레스 해소법"
                }},
                "rituals": "반복되는 의례들"
            }}
        }},
        {{옵션2}},
        {{옵션3}}
    ]
}}"""
        
        return prompt
    
    def _generate_secrets_prompt(self, plot_text, title, character_info, characters_data, previous_info):
        """비밀과 욕망 프롬프트"""
        
        prompt = f"""선택된 정보를 바탕으로 각 인물의 비밀과 숨겨진 욕망을 설정해주세요.

【줄거리】
제목: {title}
내용: {plot_text}

【등장인물】
{character_info}

【이전 선택사항】
{previous_info}

【작업 지시사항】
각 인물이 숨기고 있는 비밀과 욕망에 대해 3가지 다른 버전을 제시하세요.

각 옵션은 다음 요소를 포함해야 합니다:
1. 가장 큰 비밀
2. 비밀을 지키는 이유
3. 발각될 경우의 결과
4. 진짜 욕망
5. 욕망을 억누르는 이유

이전 선택사항들과 연결되면서도 극적 긴장감을 높일 수 있는 비밀을 설정하세요.

JSON 형식으로 응답:
{{
    "options": [
        {{
            "option_number": 1,
            "title": "비밀 유형 (예: 이중생활)",
            "description": "이 비밀들의 핵심 주제",
            "character_secrets": [
                {{
                    "name": "인물 이름",
                    "biggest_secret": "가장 큰 비밀",
                    "reason_for_hiding": "숨기는 이유",
                    "consequences_if_revealed": "발각 시 결과",
                    "true_desire": "진짜 욕망",
                    "suppression_reason": "억누르는 이유",
                    "hints_in_behavior": "행동에서 드러나는 단서"
                }}
            ]
        }},
        {{옵션2}},
        {{옵션3}}
    ]
}}"""
        
        return prompt


if __name__ == "__main__":
    # 테스트
    gen = CharacterDetailGen()
    
    # 테스트 데이터
    test_plot = {
        'title': '성형의 늪',
        'plot': '옥순은 쌍꺼풀 수술을 시작으로 코, 턱, 가슴까지 성형수술에 빠져든다. 남편 광수가 벌어오는 돈을 모두 성형에 쓰고, 카드빚까지 만들어가며 수술을 반복한다.'
    }
    
    test_characters = [
        {
            'name': '옥순',
            'gender': '여성',
            'age': 38,
            'job': '백화점 판매원',
            'mbti': 'ESFP',
            'trait': '충동적이고 외모에 집착',
            'personality_analysis': 'ESFP 특유의 즉각적 만족 추구가 성형 중독으로 발현됨'
        },
        {
            'name': '광수',
            'gender': '남성',
            'age': 42,
            'job': '공장 주임',
            'mbti': 'ISTJ',
            'trait': '책임감 강하지만 무력함',
            'personality_analysis': 'ISTJ의 의무감으로 아내를 지원하지만 한계에 도달'
        }
    ]
    
    # 1. 관계 다이나믹스 프롬프트
    print("="*60)
    print("1. 관계 다이나믹스 프롬프트 예시")
    print("="*60)
    result = gen.generate_section('relationship', test_plot, test_characters)
    print(result['prompt'])
    
    # 2. 개인 배경 프롬프트 (이전 선택 포함)
    print("\n" + "="*60)
    print("2. 개인 배경 프롬프트 예시 (관계 선택 후)")
    print("="*60)
    
    # 가상의 관계 선택
    previous_selections = {
        'relationship': {
            'title': '공생적 의존',
            'relationships': [{
                'pair': '옥순-광수',
                'surface_relationship': '부부',
                'real_relationship': '가해자와 공모자',
                'emotional_temperature': '애증의 공존',
                'power_structure': '경제적 의존 vs 감정적 지배',
                'conflict_pattern': '폭발-후회-반복',
                'communication_style': '간접적 공격과 침묵'
            }]
        }
    }
    
    result = gen.generate_section('background', test_plot, test_characters, previous_selections)
    print(result['prompt'][:1000] + "...") # 첫 1000자만 출력