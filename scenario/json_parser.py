#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re


class RobustJSONParser:
    """강력한 JSON 파싱 클래스"""
    
    @staticmethod
    def extract_json(text):
        """텍스트에서 JSON 추출 및 정제"""
        
        # 1. JSON 블록 찾기 (여러 패턴 시도)
        json_patterns = [
            r'\{[\s\S]*\}',  # 가장 바깥쪽 중괄호
            r'```json\s*([\s\S]*?)\s*```',  # 마크다운 코드 블록
            r'```\s*([\s\S]*?)\s*```',  # 일반 코드 블록
        ]
        
        json_str = None
        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                json_str = match.group(1) if match.groups() else match.group(0)
                break
        
        if not json_str:
            # 마지막 시도: 첫 {부터 마지막 }까지
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = text[start:end+1]
            else:
                return None
        
        return json_str
    
    @staticmethod
    def clean_json(json_str):
        """JSON 문자열 정제"""
        
        # 1. 주석 제거 (//와 /* */ 스타일 모두)
        # 한 줄 주석 제거
        json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
        # 여러 줄 주석 제거
        json_str = re.sub(r'/\*[\s\S]*?\*/', '', json_str)
        
        # 2. 마지막 쉼표 제거
        # 배열의 마지막 쉼표
        json_str = re.sub(r',\s*\]', ']', json_str)
        # 객체의 마지막 쉼표
        json_str = re.sub(r',\s*\}', '}', json_str)
        
        # 3. 제어 문자 제거
        json_str = json_str.replace('\t', '    ')  # 탭을 공백으로
        json_str = json_str.replace('\r\n', '\n')  # Windows 줄바꿈
        json_str = json_str.replace('\r', '\n')    # Mac 줄바꿈
        
        # 4. 문자열 내부의 이스케이프되지 않은 따옴표 처리
        # 문자열 내부의 따옴표를 찾아서 이스케이프
        def escape_quotes(match):
            content = match.group(1)
            # 이미 이스케이프된 것은 제외하고 처리
            content = re.sub(r'(?<!\\)"', r'\"', content)
            return f'"{content}"'
        
        # "..." 패턴의 문자열 찾기 (multiline 지원)
        json_str = re.sub(r'"((?:[^"\\]|\\.)*)?"', escape_quotes, json_str, flags=re.DOTALL)
        
        # 5. 줄바꿈 처리
        # JSON 문자열 내부의 실제 줄바꿈을 \n으로 변환
        def fix_newlines(match):
            content = match.group(1)
            content = content.replace('\n', '\\n')
            return f'"{content}"'
        
        json_str = re.sub(r'"([^"]*)"', fix_newlines, json_str)
        
        # 6. BOM 제거
        json_str = json_str.lstrip('\ufeff')
        
        # 7. 앞뒤 공백 제거
        json_str = json_str.strip()
        
        return json_str
    
    @staticmethod
    def parse(text):
        """텍스트에서 JSON을 추출하고 파싱"""
        
        # 1. JSON 추출
        json_str = RobustJSONParser.extract_json(text)
        if not json_str:
            return None
        
        # 2. JSON 정제
        json_str = RobustJSONParser.clean_json(json_str)
        
        # 3. 파싱 시도
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # 오류 위치 근처 출력 (디버깅용)
            error_line = e.lineno
            lines = json_str.split('\n')
            
            print(f"JSON 파싱 오류: {e}")
            print(f"오류 위치: 줄 {error_line}, 열 {e.colno}")
            
            # 오류 위치 근처 3줄 출력
            start = max(0, error_line - 2)
            end = min(len(lines), error_line + 1)
            
            for i in range(start, end):
                if i < len(lines):
                    marker = " >> " if i == error_line - 1 else "    "
                    print(f"{marker}{i+1}: {lines[i]}")
            
            # 추가 복구 시도
            return RobustJSONParser.recover_json(json_str)
    
    @staticmethod
    def recover_json(json_str):
        """JSON 복구 시도"""
        
        # 1. 가장 간단한 형태로 시도
        try:
            # stories 배열만 추출
            stories_match = re.search(r'"stories"\s*:\s*\[([\s\S]*?)\]', json_str)
            if stories_match:
                stories_content = stories_match.group(1)
                
                # 각 스토리 객체 추출
                story_pattern = r'\{[^{}]*"title"\s*:\s*"([^"]+)"[^{}]*"plot"\s*:\s*"([^"]+)"[^{}]*\}'
                stories = []
                
                for match in re.finditer(story_pattern, stories_content):
                    title = match.group(1)
                    plot = match.group(2)
                    stories.append({
                        "title": title,
                        "plot": plot
                    })
                
                if stories:
                    return {"stories": stories}
        except:
            pass
        
        return None


# claude_interface.py에 통합할 함수
def parse_claude_response(stdout):
    """Claude 응답을 안전하게 파싱"""
    
    # RobustJSONParser 사용
    result = RobustJSONParser.parse(stdout)
    
    if result:
        return result
    
    # 파싱 실패 시 더미 데이터 반환
    print("JSON 파싱 실패 - 더미 데이터 반환")
    return {
        "stories": [
            {"title": f"임시 제목 {i+1}", "plot": f"임시 줄거리 {i+1}"} 
            for i in range(5)
        ]
    }