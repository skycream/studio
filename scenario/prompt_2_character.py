#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
from collections import defaultdict


class CharacterGen:
    def __init__(self):
        # 나는 솔로 이름 풀
        self.male_names = ["영수", "영호", "영식", "영철", "광수", "상철"]
        self.female_names = ["영숙", "정숙", "순자", "영자", "옥순", "현숙"]
        
        # MBTI 추론을 위한 행동 패턴 사전
        self.mbti_patterns = {
            # E vs I
            "E": ["주도", "먼저", "공개", "모임", "표현", "드러내", "요구", "선언", "외치"],
            "I": ["혼자", "조용히", "속으로", "참고", "숨기", "견디", "삭이", "속앓이"],
            
            # S vs N
            "S": ["증거", "확인", "목격", "사실", "구체적", "현실", "실제", "직접"],
            "N": ["예감", "직감", "의심", "느낌", "짐작", "암시", "눈치", "분위기"],
            
            # T vs F
            "T": ["계산", "계획", "전략", "냉정", "논리", "분석", "이익", "효율"],
            "F": ["감정", "눈물", "마음", "상처", "사랑", "미움", "분노", "슬픔"],
            
            # J vs P
            "J": ["계획", "준비", "규칙", "원칙", "체계", "정리", "미리", "철저"],
            "P": ["즉흥", "유연", "상황", "적응", "자유", "충동", "즉시", "변경"]
        }
        
        # MBTI별 전형적인 행동 패턴
        self.mbti_behaviors = {
            "INTJ": {
                "전략가": ["장기 계획 수립", "냉철한 분석", "독립적 행동", "완벽주의"],
                "복수": ["치밀한 증거 수집", "최적의 타이밍 대기", "감정 배제"],
                "갈등": ["논리적 대응", "감정 절제", "독자적 해결"]
            },
            "ISFJ": {
                "보호자": ["가족 우선", "희생적", "전통 중시", "조화 추구"],
                "복수": ["정의 실현", "도덕적 우위", "조용한 저항"],
                "갈등": ["인내와 참음", "간접적 표현", "타협 시도"]
            },
            "ESTJ": {
                "관리자": ["규칙 강요", "권위 행사", "효율 추구", "통제욕"],
                "복수": ["공개적 응징", "체면 손상", "권력 행사"],
                "갈등": ["직접 대면", "명령과 지시", "굴복 요구"]
            },
            "ENFP": {
                "활동가": ["감정 표출", "즉흥적", "열정적", "이상주의"],
                "복수": ["감정적 폭발", "주변 동원", "드라마틱"],
                "갈등": ["감정 호소", "관계 중심", "화해 시도"]
            },
            "ISTP": {
                "장인": ["실용적", "독립적", "과묵함", "행동파"],
                "복수": ["직접 행동", "최소한의 말", "효과적 타격"],
                "갈등": ["회피 우선", "필요시 대응", "감정 분리"]
            },
            "ESFP": {
                "연예인": ["주목받기", "감정적", "사교적", "현재 중심"],
                "복수": ["즉각 반응", "공개적 드라마", "감정 폭발"],
                "갈등": ["직접 표현", "눈물과 호소", "화해 추구"]
            }
        }
        
        # MBTI 상세 설명
        self.mbti_descriptions = {
            "INTJ": {
                "type": "전략가형",
                "basic": "독립적이고 분석적이며, 장기적인 계획을 세우는 것을 좋아합니다.",
                "traits": ["냉철한 논리", "전략적 사고", "완벽주의", "독립성"]
            },
            "ISTJ": {
                "type": "현실주의자형",
                "basic": "책임감이 강하고 전통을 중시하며, 체계적이고 신뢰할 수 있습니다.",
                "traits": ["원칙주의", "인내심", "신중함", "책임감"]
            },
            "INTJ": {
                "type": "전략가형",
                "basic": "독립적이고 분석적이며, 장기적인 계획을 세우는 것을 좋아합니다.",
                "traits": ["냉철한 논리", "전략적 사고", "완벽주의", "독립성"]
            },
            "ISFJ": {
                "type": "수호자형",
                "basic": "따뜻하고 헌신적이며, 타인을 돕는 것을 좋아하고 전통을 중시합니다.",
                "traits": ["배려심", "희생정신", "조화추구", "세심함"]
            },
            "ESTJ": {
                "type": "경영자형",
                "basic": "리더십이 강하고 체계적이며, 목표 달성을 위해 효율적으로 일합니다.",
                "traits": ["통솔력", "결단력", "실용성", "권위적"]
            },
            "ESFJ": {
                "type": "집정관형",
                "basic": "사교적이고 협력적이며, 타인의 감정을 잘 배려하고 조화를 추구합니다.",
                "traits": ["친화력", "책임감", "배려심", "전통중시"]
            },
            "ENFP": {
                "type": "활동가형",
                "basic": "열정적이고 창의적이며, 가능성을 추구하고 타인과의 연결을 중시합니다.",
                "traits": ["열정", "창의성", "공감능력", "자유로움"]
            },
            "ESFP": {
                "type": "연예인형",
                "basic": "활발하고 사교적이며, 현재를 즐기고 타인과 함께하는 것을 좋아합니다.",
                "traits": ["즉흥성", "낙천성", "감성적", "현재중심"]
            },
            "ISTP": {
                "type": "장인형",
                "basic": "논리적이고 실용적이며, 문제 해결을 좋아하고 독립적입니다.",
                "traits": ["실용성", "적응력", "과묵함", "행동지향"]
            },
            "ESTP": {
                "type": "사업가형",
                "basic": "행동 지향적이고 현실적이며, 즉각적인 결과를 추구합니다.",
                "traits": ["대담함", "현실감각", "순발력", "경쟁심"]
            },
            "INFP": {
                "type": "중재자형",
                "basic": "이상주의적이고 창의적이며, 개인의 가치와 신념을 중시합니다.",
                "traits": ["이상주의", "공감능력", "창의성", "개인주의"]
            },
            "ISFP": {
                "type": "모험가형",
                "basic": "온화하고 겸손하며, 현재를 살아가고 타인을 배려합니다.",
                "traits": ["유연성", "예술성", "겸손함", "평화추구"]
            },
            "ENTJ": {
                "type": "통솔자형",
                "basic": "대담하고 지도력이 있으며, 목표 달성을 위해 전략적으로 행동합니다.",
                "traits": ["리더십", "결단력", "효율성", "야망"]
            },
            "ENTP": {
                "type": "변론가형",
                "basic": "호기심이 많고 창의적이며, 지적 도전을 즐기고 혁신을 추구합니다.",
                "traits": ["창의성", "논리력", "도전정신", "융통성"]
            },
            "INTP": {
                "type": "논리술사형",
                "basic": "분석적이고 객관적이며, 지식 탐구를 좋아하고 독창적입니다.",
                "traits": ["분석력", "독창성", "객관성", "지적호기심"]
            },
            "INFJ": {
                "type": "옹호자형",
                "basic": "통찰력이 있고 이타적이며, 타인을 돕고 조화를 추구합니다.",
                "traits": ["통찰력", "이타심", "완벽주의", "직관력"]
            }
        }
        
        # 나는솔로 이름과 MBTI 매칭
        self.name_mbti_affinity = {
            # 남성
            "영수": ["ESTJ", "ISTJ", "ENTJ"],  # 리더형, 책임감
            "영호": ["ENFP", "ESFP", "ENTP"],  # 활발, 사교적
            "영식": ["ISFJ", "ISFP", "INFP"],  # 순수, 선량
            "영철": ["ESTP", "ISTP", "ESTJ"],  # 강한 남성성
            "광수": ["INTJ", "ENTJ", "ISTJ"],  # 엘리트, 전문직
            "상철": ["ISFJ", "ISTJ", "ESFJ"],  # 평범, 균형
            
            # 여성
            "영숙": ["ENTJ", "ESTJ", "INTJ"],  # 강한 여성
            "정숙": ["ESFJ", "ESTJ", "ISFJ"],  # 전통적, 직설적
            "순자": ["INFP", "ISFP", "ENFP"],  # 독립적, 반항적
            "영자": ["ESFP", "ISFP", "ENFP"],  # 감성적, 여린
            "옥순": ["ESFP", "ENFP", "ESFJ"],  # 매력적, 사교적
            "현숙": ["INTJ", "ENTJ", "ISTJ"]   # 세련된, 전문직
        }
    
    def analyze_plot_for_characters(self, plot):
        """줄거리에서 필요한 캐릭터 추출"""
        characters = []
        
        # 가족 관계 추출
        family_patterns = {
            r"시어머니": ("female", "50-60대", "antagonist"),
            r"며느리": ("female", "30-40대", "protagonist"),
            r"남편|아내": ("flexible", "30-50대", "support"),
            r"시누이": ("female", "30-40대", "antagonist"),
            r"자녀|아이": ("flexible", "10-20대", "victim")
        }
        
        # 직장 관계 추출
        work_patterns = {
            r"상사|부장|사장": ("flexible", "40-50대", "antagonist"),
            r"동료|직원": ("flexible", "30-40대", "support"),
            r"부하|신입": ("flexible", "20-30대", "victim")
        }
        
        # 불륜 관계 추출
        affair_patterns = {
            r"불륜|바람|애인": ("flexible", "30-40대", "catalyst"),
            r"첫사랑|옛.*사랑": ("flexible", "30-50대", "catalyst")
        }
        
        # 모든 패턴 검색
        all_patterns = {**family_patterns, **work_patterns, **affair_patterns}
        
        for pattern, (gender, age, role) in all_patterns.items():
            if re.search(pattern, plot):
                characters.append({
                    "pattern": pattern,
                    "gender": gender,
                    "age_range": age,
                    "role": role
                })
        
        return characters
    
    def infer_mbti_from_behavior(self, plot, character_role):
        """줄거리와 역할에서 MBTI 추론"""
        mbti_scores = defaultdict(int)
        
        # E/I 추론
        for word in self.mbti_patterns["E"]:
            if word in plot:
                mbti_scores["E"] += 1
        for word in self.mbti_patterns["I"]:
            if word in plot:
                mbti_scores["I"] += 1
        
        # S/N 추론
        for word in self.mbti_patterns["S"]:
            if word in plot:
                mbti_scores["S"] += 1
        for word in self.mbti_patterns["N"]:
            if word in plot:
                mbti_scores["N"] += 1
        
        # T/F 추론
        for word in self.mbti_patterns["T"]:
            if word in plot:
                mbti_scores["T"] += 1
        for word in self.mbti_patterns["F"]:
            if word in plot:
                mbti_scores["F"] += 1
        
        # J/P 추론
        for word in self.mbti_patterns["J"]:
            if word in plot:
                mbti_scores["J"] += 1
        for word in self.mbti_patterns["P"]:
            if word in plot:
                mbti_scores["P"] += 1
        
        # 역할별 가중치
        role_weights = {
            "protagonist": {"I": 1, "N": 1, "J": 1},
            "antagonist": {"E": 1, "S": 1, "J": 1},
            "catalyst": {"E": 1, "N": 1, "P": 1},
            "support": {"I": 1, "S": 1, "F": 1},
            "victim": {"I": 1, "F": 1, "P": 1}
        }
        
        if character_role in role_weights:
            for trait, weight in role_weights[character_role].items():
                mbti_scores[trait] += weight
        
        # MBTI 결정
        mbti = ""
        mbti += "E" if mbti_scores["E"] >= mbti_scores["I"] else "I"
        mbti += "S" if mbti_scores["S"] >= mbti_scores["N"] else "N"
        mbti += "T" if mbti_scores["T"] >= mbti_scores["F"] else "F"
        mbti += "J" if mbti_scores["J"] >= mbti_scores["P"] else "P"
        
        return mbti, mbti_scores
    
    def match_name_to_mbti(self, mbti, gender, used_names):
        """MBTI에 맞는 나는솔로 이름 매칭"""
        name_pool = self.male_names if gender == "male" else self.female_names
        available_names = [n for n in name_pool if n not in used_names]
        
        # MBTI 친화도 점수 계산
        best_name = None
        best_score = -1
        
        for name in available_names:
            if name in self.name_mbti_affinity:
                score = 0
                for preferred_mbti in self.name_mbti_affinity[name]:
                    # MBTI 유사도 계산 (같은 글자 수)
                    similarity = sum(1 for a, b in zip(mbti, preferred_mbti) if a == b)
                    score = max(score, similarity)
                
                if score > best_score:
                    best_score = score
                    best_name = name
        
        # 매칭되는 이름이 없으면 랜덤 선택
        if not best_name and available_names:
            import random
            best_name = random.choice(available_names)
        
        return best_name
    
    def generate(self, selected_plot):
        """캐릭터 생성 프롬프트 생성"""
        import random
        
        # 줄거리 분석
        plot_text = selected_plot.get('plot', '')
        title = selected_plot.get('title', '')
        
        # 필요한 캐릭터 추출
        required_characters = self.analyze_plot_for_characters(plot_text)
        
        # 각 캐릭터의 MBTI 추론
        characters_with_mbti = []
        used_names = []
        
        for char in required_characters:
            mbti, scores = self.infer_mbti_from_behavior(plot_text, char['role'])
            
            # 성별 결정 (flexible인 경우)
            if char['gender'] == 'flexible':
                gender = random.choice(['male', 'female'])
            else:
                gender = char['gender']
            
            # 이름 매칭
            name = self.match_name_to_mbti(mbti, gender, used_names)
            if name:
                used_names.append(name)
            
            characters_with_mbti.append({
                'name': name,
                'gender': gender,
                'age_range': char['age_range'],
                'role': char['role'],
                'mbti': mbti,
                'mbti_scores': dict(scores)
            })
        
        # 프롬프트 생성
        prompt = f"""선택된 줄거리를 바탕으로 등장인물을 생성해주세요.

【줄거리】
제목: {title}
내용: {plot_text}

【분석된 캐릭터 정보】
"""
        
        for i, char in enumerate(characters_with_mbti, 1):
            prompt += f"\n{i}. {char['name']} ({char['gender']}, {char['age_range']})"
            prompt += f"\n   역할: {char['role']}"
            prompt += f"\n   추론된 MBTI: {char['mbti']}"
            
            # MBTI 설명 추가
            mbti_info = self.mbti_descriptions.get(char['mbti'], {})
            if mbti_info:
                prompt += f"\n   MBTI 유형: {mbti_info.get('type', '')} - {mbti_info.get('basic', '')}"
                prompt += f"\n   주요 특성: {', '.join(mbti_info.get('traits', []))}"
            
            behavior = self.mbti_behaviors.get(char['mbti'], {})
            if behavior:
                prompt += f"\n   예상 행동: {', '.join(list(behavior.get('복수', []))[:2])}"
        
        prompt += """

위 분석을 바탕으로 각 인물의 구체적인 프로필을 생성해주세요:

1. 나이는 범위 내에서 구체적으로
2. 직업은 줄거리와 MBTI에 맞게
3. 고향은 다양하게 (서울, 부산, 대구, 인천, 광주, 대전, 수원 등)
4. 각 인물의 핵심 특징을 MBTI 기반으로 작성
5. MBTI 성격 분석을 줄거리와 연결하여 상세히 설명

JSON 형식으로 응답:
{
    "characters": [
        {
            "name": "이름",
            "gender": "성별",
            "age": 구체적나이,
            "job": "직업",
            "hometown": "고향",
            "mbti": "MBTI",
            "mbti_description": "MBTI 타입명과 기본 설명",
            "personality_analysis": "줄거리 속 행동과 연결한 상세 성격 분석 (3-4줄)",
            "trait": "핵심 특징 (MBTI 반영)",
            "role_in_story": "줄거리에서의 역할"
        }
    ]
}"""
        
        return {
            "prompt": prompt,
            "references": [],  # 캐릭터 생성에는 레퍼런스 불필요
            "analyzed_characters": characters_with_mbti,
            "selected_plot": selected_plot
        }


if __name__ == "__main__":
    # 테스트
    gen = CharacterGen()
    
    # 테스트 줄거리
    test_plot = {
        "title": "시어머니의 복수",
        "plot": "10년간 시어머니의 구박을 참고 견딘 며느리 순자는 우연히 시어머니의 불륜 증거를 발견하고, 차분하게 증거를 수집한 뒤 가족 모임에서 폭로한다."
    }
    
    result = gen.generate(test_plot)
    print("프롬프트:")
    print(result["prompt"])
    print("\n분석된 캐릭터:")
    for char in result["analyzed_characters"]:
        print(f"- {char['name']}: {char['mbti']} ({char['role']})")