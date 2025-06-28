#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prompt_2_character import CharacterGen
from claude_interface import ClaudeInterface

# 테스트 줄거리
test_plot = {
    'title': '성형의 늪',
    'plot': '옥순은 쌍꺼풀 수술을 시작으로 코, 턱, 가슴까지 성형수술에 빠져든다. 남편 광수가 벌어오는 돈을 모두 성형에 쓰고, 카드빚까지 만들어가며 수술을 반복한다.'
}

# CharacterGen으로 프롬프트 생성
char_gen = CharacterGen()
prompt_data = char_gen.generate(test_plot)

print("생성된 프롬프트:")
print("="*60)
print(prompt_data['prompt'][:500] + "...")
print("="*60)

# Claude 실행
claude = ClaudeInterface()
result = claude.execute_prompt(prompt_data)

if result:
    print("\n결과:")
    print(result)
else:
    print("\n실행 실패")