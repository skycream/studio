#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import os
import sys
from json_parser import RobustJSONParser


class ClaudeInterface:
    def __init__(self):
        self.selected_stories = {}  # 선택된 스토리 저장
        self.keywords = []  # 키워드 리스트
        self.tone = self._get_random_tone()  # 톤 설정 (랜덤 시작)
        self.num_stories = 5  # 생성할 스토리 개수
    
    def _get_random_tone(self):
        """랜덤 톤 선택"""
        import random
        tones = ["기본", "자극적", "현실적", "충격적", "선정적"]
        return random.choice(tones)
        
    def execute_prompt(self, prompt_data):
        """Claude Code로 프롬프트 자동 실행"""
        print("\n재생성 중...")
        print("="*60)
        
        # 프롬프트 출력
        print("\n[생성된 프롬프트]")
        print("-" * 60)
        print(prompt_data['prompt'])
        print("-" * 60)
        
        # 추가 랜덤 요소
        import random
        creativity_hints = [
            "\n※ 기존과 완전히 다른 새로운 스토리를 만들어주세요.",
            "\n★ 독창적이고 예상치 못한 전개를 포함해주세요.",
            "\n◆ 이전에 없던 신선한 설정으로 작성해주세요.",
            "\n▶ 창의적이고 독특한 이야기를 만들어주세요."
        ]
        prompt_data['prompt'] += random.choice(creativity_hints)
        
        # 재생성 시 30% 확률로 톤 자동 변경
        if random.random() < 0.3 and not hasattr(self, '_tone_locked'):
            self.tone = self._get_random_tone()
            print(f"톤 자동 변경: {self.tone}")
        
        # 이름 제한 및 캐릭터 매칭 가이드 추가
        name_restriction = """\n
중요: 등장인물 이름은 캐릭터의 성격과 역할에 맞게 다음 중에서만 선택하세요 (성 없이 이름만):

【남성 이름 가이드】
- 영수: 연장자, 신중하고 안정적인 성격, 리더형, 이공계 출신
  → 사용: 책임감 있는 남편, 가장, 형님 역할
- 영호: 밝고 활발한 분위기 메이커, 말이 많음, 막내형
  → 사용: 애인, 불륜 상대, 유쾌한 캐릭터
- 영식: 조용하고 차분함, 훈남형, 모범생 스타일, 신사적
  → 사용: 순진한 남편, 피해자, 선량한 인물
- 영철: 직진형, 남성적이고 터프함, 의지가 강함, 적극적
  → 사용: 가해자, 바람둥이, 강한 성격의 남편
- 광수: 엘리트 전문직(의사, 변호사, 연구원), 고학력, 높은 연봉
  → 사용: 능력 있는 불륜 상대, 재벌, 전문직 남편
- 상철: 평범하고 무난한 일반인, 균형잡힌 성격
  → 사용: 평범한 회사원, 동네 아저씨, 조연

【여성 이름 가이드】
- 영숙: 자신감 있는 커리어우먼, 주도적, 강인함, 전문직
  → 사용: 독립적인 아내, 복수하는 여성, 강한 며느리
- 정숙: 쿨하고 털털한 언니 스타일, 솔직함, 연장자
  → 사용: 시원한 성격의 아내, 조언자, 친구
- 순자: 당찬 막내형, 독립적, 자기 주관이 뚜렷함, 마이웨이
  → 사용: 시어머니에 맞서는 며느리, 반항적인 딸
- 영자: 감성적이고 여린 성격, 애교 많음, 눈물이 많음
  → 사용: 순진한 피해자, 감정적인 아내, 애인
- 옥순: 외모가 뛰어남, 화제의 중심, 인기 많음
  → 사용: 불륜 상대, 유혹하는 여성, 미인 역할
- 현숙: 세련되고 도시적, 전문직 여성, 쿨한 매력
  → 사용: 능력 있는 커리어우먼, 차가운 아내

【이름 선택 예시】
- 의사와 불륜하는 이야기 → 남자는 "광수"
- 시어머니와 싸우는 며느리 → "순자" 또는 "영숙"
- 순진하게 속는 남편 → "영식"
- 바람피우는 매력적인 여성 → "옥순"
- 복수를 계획하는 아내 → "영숙"
- 돈 때문에 범죄 저지르는 남자 → "영철"

반드시 캐릭터의 성격과 역할에 맞는 이름을 선택하세요!"""
        prompt_data['prompt'] += name_restriction
        
        # 키워드가 있으면 프롬프트에 추가
        if self.keywords:
            keyword_str = f"\n\n특히 다음 키워드들을 포함해주세요: {', '.join(self.keywords)}"
            prompt_data['prompt'] = prompt_data['prompt'].replace("생성해주세요.", f"생성해주세요.{keyword_str}")
        
        # 톤 설정 추가
        tone_map = {
            "자극적": "\n\n톤: 자극적이고 충격적인 전개로 작성해주세요.",
            "현실적": "\n\n톤: 현실적이고 일상적인 느낌으로 작성해주세요.",
            "충격적": "\n\n톤: 반전이 있고 충격적인 결말로 작성해주세요.",
            "기본": ""
        }
        if self.tone in tone_map:
            prompt_data['prompt'] = prompt_data['prompt'].replace("생성해주세요.", f"생성해주세요.{tone_map[self.tone]}")
        
        # Claude Code 명령어 구성
        # 캐릭터 생성인 경우 프롬프트만 전달
        if "캐릭터" in prompt_data['prompt'] or "character" in prompt_data['prompt']:
            claude_command = prompt_data['prompt']
        else:
            # 줄거리 생성인 경우 레퍼런스 포함
            claude_command = f"""다음 프롬프트를 실행해주세요:

{prompt_data['prompt']}

레퍼런스 데이터 (사랑과 전쟁에서 랜덤 선택한 {len(prompt_data.get('references', []))}개 에피소드):
{json.dumps(prompt_data.get('references', []), ensure_ascii=False, indent=2) if prompt_data.get('references') else ""}

위 레퍼런스를 참고하여 프롬프트에서 요청한 대로 새로운 이야기를 생성해주세요."""
        
        # Claude Code 실행
        try:
            # 명령어 길이 체크
            print(f"Claude 명령어 길이: {len(claude_command)} 문자")
            
            # 디버깅용: 명령어 첫 부분 출력
            print(f"명령어 시작: {claude_command[:200]}...")
            
            # 프롬프트가 너무 길면 경고
            if len(claude_command) > 20000:
                print("경고: 프롬프트가 매우 깁니다.")
            
            process = subprocess.Popen(
                ['claude'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            stdout, stderr = process.communicate(input=claude_command)
            
            # 디버깅: stdout과 stderr 모두 출력
            if stderr:
                print(f"Claude stderr: {stderr}")
            
            if process.returncode != 0:
                print(f"Claude Code 실행 오류 (return code: {process.returncode})")
                print(f"stderr: {stderr}")
                print(f"stdout: {stdout[:500]}")
                return None
            
            # 빈 출력 체크
            if not stdout or stdout.strip() == "":
                print("Claude가 빈 응답을 반환했습니다.")
                return None
            
            # 출력에서 JSON 추출 - RobustJSONParser 사용
            result = RobustJSONParser.parse(stdout)
            
            if result:
                return result
            else:
                print("JSON 파싱 실패")
                print("전체 출력:")
                print(stdout[:1000])  # 첫 1000자만 출력
                
                # 더미 데이터 반환 (stories 또는 characters)
                if "캐릭터" in claude_command or "character" in claude_command:
                    return {
                        "characters": {
                            "영수": [
                                {
                                    "version": 1,
                                    "name": "영수",
                                    "gender": "남성",
                                    "age": 35,
                                    "job": "회사원",
                                    "hometown": "서울",
                                    "mbti": "ISTJ",
                                    "mbti_description": "현실주의자형 - 책임감이 강하고 신뢰할 수 있습니다",
                                    "personality_analysis": "임시 성격 분석입니다.",
                                    "trait": "성실함"
                                },
                                {
                                    "version": 2,
                                    "name": "영수",
                                    "gender": "남성",
                                    "age": 40,
                                    "job": "공무원",
                                    "hometown": "부산",
                                    "mbti": "ESTJ",
                                    "mbti_description": "경영자형 - 리더십이 강합니다",
                                    "personality_analysis": "임시 성격 분석 2입니다.",
                                    "trait": "리더십"
                                },
                                {
                                    "version": 3,
                                    "name": "영수",
                                    "gender": "남성",
                                    "age": 38,
                                    "job": "자영업",
                                    "hometown": "대구",
                                    "mbti": "ENTJ",
                                    "mbti_description": "통솔자형 - 야망이 있습니다",
                                    "personality_analysis": "임시 성격 분석 3입니다.",
                                    "trait": "야심"
                                }
                            ]
                        }
                    }
                else:
                    return {
                        "stories": [
                            {"title": f"임시 제목 {i+1}", "plot": f"임시 줄거리 {i+1}"} 
                            for i in range(self.num_stories)
                        ]
                    }
                
        except FileNotFoundError:
            print("Claude Code가 설치되어 있지 않습니다.")
            return None
        except Exception as e:
            print(f"오류 발생: {e}")
            return None
    
    def display_stories(self, stories):
        """스토리 목록 표시"""
        print("\n" + "="*60)
        selected_count = len([k for k, v in self.selected_stories.items() if v is not None])
        print(f"생성된 줄거리 ({selected_count}/{self.num_stories} 선택됨)")
        print("="*60 + "\n")
        
        for i, story in enumerate(stories, 1):
            # 선택 상태 확인
            if i in self.selected_stories and self.selected_stories[i] is not None:
                status = "✓"
                display_story = self.selected_stories[i]
            else:
                status = "✗"
                display_story = story
            
            print(f"[{i}] {status} {display_story['title']}")
            print(f"    {display_story['plot']}")
            print()
    
    def get_user_choice(self):
        """사용자 선택 받기"""
        print("="*60)
        print("옵션:")
        print("="*60)
        print("1) 선택 안 된 것만 재생성")
        print("2) 전체 재생성")
        print("3) 특정 번호 선택/해제 (예: 2,4)")
        print("4) 키워드 추가/변경")
        print("5) 톤 변경")
        print("6) 개수 변경")
        print("7) 완료 (5개 모두 선택 필요)")
        print()
        
        return input("선택: ").strip()
    
    def toggle_selection(self, numbers, current_stories):
        """특정 번호 선택/해제"""
        for num in numbers:
            if 1 <= num <= len(current_stories):
                if num in self.selected_stories and self.selected_stories[num] is not None:
                    # 선택 해제
                    self.selected_stories[num] = None
                    print(f"{num}번 선택 해제됨")
                else:
                    # 선택
                    self.selected_stories[num] = current_stories[num-1]
                    print(f"{num}번 선택됨")
    
    def update_keywords(self):
        """키워드 업데이트"""
        print(f"\n현재 키워드: {', '.join(self.keywords) if self.keywords else '없음'}")
        new_keywords = input("새 키워드 입력 (쉼표로 구분, Enter 시 초기화): ").strip()
        
        if new_keywords:
            self.keywords = [k.strip() for k in new_keywords.split(',')]
            print(f"키워드 설정됨: {', '.join(self.keywords)}")
        else:
            self.keywords = []
            print("키워드 초기화됨")
    
    def update_tone(self):
        """톤 변경"""
        print(f"\n현재 톤: {self.tone}")
        print("1) 기본")
        print("2) 자극적")
        print("3) 현실적")
        print("4) 충격적")
        print("5) 선정적")
        
        choice = input("선택: ").strip()
        tone_map = {"1": "기본", "2": "자극적", "3": "현실적", "4": "충격적", "5": "선정적"}
        
        if choice in tone_map:
            self.tone = tone_map[choice]
            print(f"톤 변경됨: {self.tone}")
    
    def run_interactive(self):
        """대화형 실행"""
        from prompt_1_plot import PlotGen
        
        # 초기 생성
        plot_gen = PlotGen(num=self.num_stories)
        prompt_data = plot_gen.generate()
        
        current_stories = []
        
        while True:
            # 재생성이 필요한 위치 확인
            positions_to_generate = []
            for i in range(1, self.num_stories + 1):
                if i not in self.selected_stories or self.selected_stories[i] is None:
                    positions_to_generate.append(i)
            
            # 필요한 만큼만 생성
            if positions_to_generate:
                plot_gen = PlotGen(num=len(positions_to_generate))
                prompt_data = plot_gen.generate()
                response = self.execute_prompt(prompt_data)
                
                if response and 'stories' in response:
                    # 생성된 스토리를 빈 위치에 채우기
                    new_stories = response['stories']
                    for idx, pos in enumerate(positions_to_generate):
                        if idx < len(new_stories):
                            if pos <= len(current_stories):
                                current_stories[pos-1] = new_stories[idx]
                            else:
                                current_stories.append(new_stories[idx])
            
            # 현재 상태 표시
            self.display_stories(current_stories)
            
            # 모두 선택되었는지 확인
            selected_count = len([k for k, v in self.selected_stories.items() if v is not None])
            if selected_count >= self.num_stories:
                print(f"\n축하합니다! {self.num_stories}개 스토리가 모두 선택되었습니다.")
                complete = input("완료하시겠습니까? (y/n): ").strip().lower()
                if complete == 'y':
                    break
            
            # 사용자 선택
            choice = self.get_user_choice()
            
            if choice == "1":  # 선택 안 된 것만 재생성
                continue
            elif choice == "2":  # 전체 재생성
                self.selected_stories.clear()
                current_stories = []
            elif choice == "3":  # 특정 번호 선택/해제
                numbers = input("번호 입력 (쉼표로 구분): ").strip()
                try:
                    nums = [int(n.strip()) for n in numbers.split(',')]
                    self.toggle_selection(nums, current_stories)
                except ValueError:
                    print("잘못된 입력입니다.")
            elif choice == "4":  # 키워드 변경
                self.update_keywords()
            elif choice == "5":  # 톤 변경
                self.update_tone()
            elif choice == "6":  # 개수 변경
                new_num = input(f"새로운 개수 입력 (현재: {self.num_stories}): ").strip()
                try:
                    self.num_stories = int(new_num)
                    print(f"개수 변경됨: {self.num_stories}")
                    # 선택 초기화
                    self.selected_stories.clear()
                    current_stories = []
                except ValueError:
                    print("잘못된 입력입니다.")
            elif choice == "7":  # 완료
                if selected_count >= self.num_stories:
                    break
                else:
                    print(f"\n아직 {self.num_stories - selected_count}개를 더 선택해야 합니다.")
        
        # 최종 선택된 스토리 반환
        final_stories = []
        for i in range(1, self.num_stories + 1):
            if i in self.selected_stories and self.selected_stories[i] is not None:
                final_stories.append(self.selected_stories[i])
        
        return final_stories


if __name__ == "__main__":
    # Claude 인터페이스 실행
    claude = ClaudeInterface()
    final_stories = claude.run_interactive()
    
    print("\n" + "="*60)
    print("최종 선택된 스토리:")
    print("="*60)
    for i, story in enumerate(final_stories, 1):
        print(f"\n{i}. {story['title']}")
        print(f"   {story['plot']}")
    
    # 결과 저장
    output_file = "outputs/selected_plots.json"
    os.makedirs("outputs", exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"stories": final_stories}, f, ensure_ascii=False, indent=2)
    print(f"\n결과가 {output_file}에 저장되었습니다.")