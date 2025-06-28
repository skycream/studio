#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from prompt_1_plot import PlotGen
from prompt_2_character import CharacterGen
from claude_interface import ClaudeInterface


class TelegramScenarioBot:
    def __init__(self, token):
        self.token = token
        self.claude = ClaudeInterface()
        
        # 사용자별 상태 저장
        self.user_states = {}
        
    def get_user_state(self, user_id):
        """사용자 상태 가져오기"""
        if user_id not in self.user_states:
            import random
            self.user_states[user_id] = {
                'selected_stories': {},
                'current_stories': [],
                'keywords': [],
                'tone': random.choice(['기본', '자극적', '현실적', '충격적', '선정적']),
                'num_stories': 5,
                'stage': 'plot'  # plot, character, detail, narrative, structure, scene
            }
        return self.user_states[user_id]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """봇 시작"""
        user_id = update.effective_user.id
        state = self.get_user_state(user_id)
        
        welcome_message = """🎬 시나리오 생성 봇에 오신 것을 환영합니다!

이 봇은 6단계를 거쳐 완성된 시나리오를 만들어드립니다:
1️⃣ 줄거리 생성
2️⃣ 캐릭터 개요
3️⃣ 캐릭터 상세
4️⃣ 서술 스타일
5️⃣ 막/장 구조
6️⃣ 상세 씬

지금부터 1단계 줄거리 생성을 시작합니다!"""
        
        await update.message.reply_text(welcome_message)
        await self.generate_plots(update, context)
    
    async def generate_plots(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """줄거리 생성"""
        user_id = update.effective_user.id
        state = self.get_user_state(user_id)
        
        # 재생성이 필요한 위치 확인
        positions_to_generate = []
        for i in range(1, state['num_stories'] + 1):
            if i not in state['selected_stories'] or state['selected_stories'][i] is None:
                positions_to_generate.append(i)
        
        if not positions_to_generate:
            # 모두 선택됨
            await self.show_current_stories(update, context)
            return
        
        # 생성 중 메시지
        generating_msg = await update.effective_chat.send_message("🔄 줄거리 생성 중...")
        
        # 필요한 만큼만 생성
        plot_gen = PlotGen(num=len(positions_to_generate))
        prompt_data = plot_gen.generate()
        
        # Claude 실행
        try:
            response = self.claude.execute_prompt(prompt_data)
        except Exception as e:
            await generating_msg.edit_text(f"❌ 오류 발생: {str(e)}")
            print(f"Claude 실행 오류: {e}")
            response = None
        
        # 생성 메시지 삭제
        if generating_msg:
            try:
                await generating_msg.delete()
            except:
                pass
        
        if response and 'stories' in response:
            # 생성된 스토리를 빈 위치에 채우기
            new_stories = response['stories']
            for idx, pos in enumerate(positions_to_generate):
                if idx < len(new_stories):
                    if pos <= len(state['current_stories']):
                        state['current_stories'][pos-1] = new_stories[idx]
                    else:
                        state['current_stories'].append(new_stories[idx])
        
        await self.show_current_stories(update, context)
    
    async def show_current_stories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """현재 스토리 목록 표시"""
        user_id = update.effective_user.id
        state = self.get_user_state(user_id)
        
        # 선택 상태 확인
        selected_count = len([k for k, v in state['selected_stories'].items() if v is not None])
        
        # 메시지 구성
        message = f"📚 **생성된 줄거리** ({selected_count}/{state['num_stories']} 선택됨)\n\n"
        
        for i, story in enumerate(state['current_stories'], 1):
            if i in state['selected_stories'] and state['selected_stories'][i] is not None:
                status = "✅"
                display_story = state['selected_stories'][i]
            else:
                status = "❌"
                display_story = story
            
            message += f"{status} **{i}. {display_story['title']}**\n"
            message += f"{display_story['plot']}\n\n"
        
        # 인라인 키보드 생성
        keyboard = []
        
        # 스토리 선택/해제 버튼 (2개씩 한 줄)
        for i in range(1, len(state['current_stories']) + 1, 2):
            row = []
            for j in range(i, min(i + 2, len(state['current_stories']) + 1)):
                if j in state['selected_stories'] and state['selected_stories'][j] is not None:
                    btn_text = f"✅ {j}번"
                else:
                    btn_text = f"❌ {j}번"
                row.append(InlineKeyboardButton(btn_text, callback_data=f"toggle_{j}"))
            keyboard.append(row)
        
        # 액션 버튼들
        keyboard.append([
            InlineKeyboardButton("🔄 선택 안 된 것만 재생성", callback_data="regen_unselected"),
            InlineKeyboardButton("♻️ 전체 재생성", callback_data="regen_all")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔤 키워드 설정", callback_data="set_keywords"),
            InlineKeyboardButton("🎭 톤 변경", callback_data="set_tone")
        ])
        
        # 완료 버튼 (5개 모두 선택 시에만 활성화)
        if selected_count >= state['num_stories']:
            keyboard.append([
                InlineKeyboardButton("✅ 완료하고 다음 단계로", callback_data="complete_plot")
            ])
        
        # 현재 설정 표시
        settings_text = f"\n📌 현재 설정:\n"
        if state['keywords']:
            settings_text += f"• 키워드: {', '.join(state['keywords'])}\n"
        settings_text += f"• 톤: {state['tone']}"
        
        message += settings_text
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # 메시지 전송 또는 업데이트
        if update.callback_query:
            await update.callback_query.message.edit_text(
                message, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.effective_chat.send_message(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """버튼 콜백 처리"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        state = self.get_user_state(user_id)
        
        data = query.data
        
        # 스토리 선택/해제
        if data.startswith("toggle_"):
            story_num = int(data.split("_")[1])
            if story_num in state['selected_stories'] and state['selected_stories'][story_num] is not None:
                state['selected_stories'][story_num] = None
            else:
                state['selected_stories'][story_num] = state['current_stories'][story_num-1]
            await self.show_current_stories(update, context)
        
        # 선택 안 된 것만 재생성
        elif data == "regen_unselected":
            await self.generate_plots(update, context)
        
        # 전체 재생성
        elif data == "regen_all":
            state['selected_stories'].clear()
            state['current_stories'] = []
            await self.generate_plots(update, context)
        
        # 키워드 설정
        elif data == "set_keywords":
            await query.message.reply_text(
                "🔤 키워드를 입력해주세요 (쉼표로 구분):\n"
                "예시: 불륜, 복수, 재벌\n"
                "초기화하려면 /clear_keywords 를 입력하세요."
            )
            context.user_data['waiting_for'] = 'keywords'
        
        # 톤 변경
        elif data == "set_tone":
            keyboard = [
                [InlineKeyboardButton("기본", callback_data="tone_기본")],
                [InlineKeyboardButton("자극적", callback_data="tone_자극적")],
                [InlineKeyboardButton("현실적", callback_data="tone_현실적")],
                [InlineKeyboardButton("충격적", callback_data="tone_충격적")],
                [InlineKeyboardButton("선정적", callback_data="tone_선정적")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("🎭 톤을 선택하세요:", reply_markup=reply_markup)
        
        # 톤 선택
        elif data.startswith("tone_"):
            tone = data.split("_")[1]
            state['tone'] = tone
            self.claude.tone = tone
            await query.message.edit_text(f"✅ 톤이 '{tone}'으로 변경되었습니다.")
            await self.show_current_stories(update, context)
        
        # 줄거리 완료
        elif data == "complete_plot":
            # 선택된 스토리 저장
            final_stories = []
            for i in range(1, state['num_stories'] + 1):
                if i in state['selected_stories'] and state['selected_stories'][i] is not None:
                    final_stories.append(state['selected_stories'][i])
            
            # 결과 저장
            output_dir = f"outputs/user_{user_id}"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"plots_{timestamp}.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"stories": final_stories}, f, ensure_ascii=False, indent=2)
            
            # 하나의 스토리 선택 (첫 번째 것으로 시작)
            state['selected_plot'] = final_stories[0]
            state['final_plots'] = final_stories
            state['current_plot_index'] = 0
            state['stage'] = 'character'
            
            # 스토리 선택 메시지
            await self.show_plot_selection(update, context)
        
        # 줄거리 네비게이션
        elif data == "prev_plot":
            state['current_plot_index'] = max(0, state['current_plot_index'] - 1)
            state['selected_plot'] = state['final_plots'][state['current_plot_index']]
            await self.show_plot_selection(update, context)
        
        elif data == "next_plot":
            max_index = len(state['final_plots']) - 1
            state['current_plot_index'] = min(max_index, state['current_plot_index'] + 1)
            state['selected_plot'] = state['final_plots'][state['current_plot_index']]
            await self.show_plot_selection(update, context)
        
        # 캐릭터 생성 시작
        elif data == "select_plot_for_character":
            await self.generate_characters(update, context)
        
        # 캐릭터 재생성
        elif data == "regenerate_characters":
            await self.generate_characters(update, context)
        
        # 다른 줄거리 선택
        elif data == "change_plot":
            await self.show_plot_selection(update, context)
        
        # 캐릭터 확정
        elif data == "confirm_characters":
            # 캐릭터 저장
            output_dir = f"outputs/user_{user_id}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"characters_{timestamp}.json")
            
            character_data = {
                "plot": state['selected_plot'],
                "characters": state['current_characters'],
                "analyzed": state.get('analyzed_characters', [])
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=2)
            
            await query.message.reply_text(
                "✅ 캐릭터가 확정되었습니다!\n\n"
                "다음 단계: 캐릭터 디테일 설정 (준비 중...)"
            )
            
            state['stage'] = 'character_detail'
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """일반 메시지 처리"""
        user_id = update.effective_user.id
        state = self.get_user_state(user_id)
        
        if context.user_data.get('waiting_for') == 'keywords':
            # 키워드 입력 처리
            keywords = [k.strip() for k in update.message.text.split(',')]
            state['keywords'] = keywords
            self.claude.keywords = keywords
            
            await update.message.reply_text(f"✅ 키워드가 설정되었습니다: {', '.join(keywords)}")
            context.user_data['waiting_for'] = None
            
            # 다시 스토리 목록 표시
            await self.show_current_stories(update, context)
    
    async def clear_keywords(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """키워드 초기화"""
        user_id = update.effective_user.id
        state = self.get_user_state(user_id)
        
        state['keywords'] = []
        self.claude.keywords = []
        
        await update.message.reply_text("✅ 키워드가 초기화되었습니다.")
        await self.show_current_stories(update, context)
    
    async def show_plot_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """최종 선택된 줄거리 중 하나 선택"""
        user_id = update.effective_user.id
        state = self.get_user_state(user_id)
        
        plots = state.get('final_plots', [])
        current_index = state.get('current_plot_index', 0)
        
        if not plots:
            await update.effective_chat.send_message("선택된 줄거리가 없습니다.")
            return
        
        current_plot = plots[current_index]
        
        message = f"""📖 **어떤 이야기로 시나리오를 만들까요?** ({current_index + 1}/{len(plots)})

**제목**: {current_plot['title']}

**줄거리**:
{current_plot['plot']}

이 줄거리로 캐릭터를 만들까요?"""
        
        keyboard = []
        
        # 네비게이션 버튼
        nav_buttons = []
        if current_index > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ 이전", callback_data="prev_plot"))
        if current_index < len(plots) - 1:
            nav_buttons.append(InlineKeyboardButton("➡️ 다음", callback_data="next_plot"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # 선택 버튼
        keyboard.append([
            InlineKeyboardButton("✅ 이 줄거리로 진행", callback_data="select_plot_for_character")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.message.edit_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.effective_chat.send_message(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def generate_characters(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """캐릭터 생성"""
        user_id = update.effective_user.id
        state = self.get_user_state(user_id)
        
        selected_plot = state.get('selected_plot')
        if not selected_plot:
            await update.effective_chat.send_message("선택된 줄거리가 없습니다.")
            return
        
        # 생성 중 메시지
        generating_msg = await update.effective_chat.send_message("🎭 캐릭터 생성 중...")
        
        # CharacterGen 사용
        char_gen = CharacterGen()
        prompt_data = char_gen.generate(selected_plot)
        
        # 분석된 캐릭터 정보 저장
        state['analyzed_characters'] = prompt_data['analyzed_characters']
        
        # Claude 실행
        try:
            response = self.claude.execute_prompt(prompt_data)
        except Exception as e:
            await generating_msg.edit_text(f"❌ 오류 발생: {str(e)}")
            return
        
        # 생성 메시지 삭제
        if generating_msg:
            try:
                await generating_msg.delete()
            except:
                pass
        
        if response and 'characters' in response:
            state['current_characters'] = response['characters']
            await self.show_characters(update, context)
        else:
            await update.effective_chat.send_message("캐릭터 생성에 실패했습니다.")
    
    async def show_characters(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """생성된 캐릭터 표시"""
        user_id = update.effective_user.id
        state = self.get_user_state(user_id)
        
        characters = state.get('current_characters', [])
        selected_plot = state.get('selected_plot', {})
        
        message = f"""🎭 **생성된 캐릭터**

📖 줄거리: {selected_plot.get('title', '')}

"""
        
        for i, char in enumerate(characters, 1):
            message += f"""**{i}. {char.get('name', '')}** ({char.get('gender', '')}, {char.get('age', '')}세)
📍 고향: {char.get('hometown', '')}
💼 직업: {char.get('job', '')}
🧩 MBTI: {char.get('mbti', '')}
✨ 특징: {char.get('trait', '')}
🎬 역할: {char.get('role_in_story', '')}

"""
        
        keyboard = [
            [InlineKeyboardButton("✅ 확정하고 다음 단계로", callback_data="confirm_characters")],
            [InlineKeyboardButton("🔄 다시 생성", callback_data="regenerate_characters")],
            [InlineKeyboardButton("📝 다른 줄거리 선택", callback_data="change_plot")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.message.edit_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.effective_chat.send_message(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    def run(self):
        """봇 실행"""
        # 애플리케이션 생성
        application = Application.builder().token(self.token).build()
        
        # 핸들러 추가
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("clear_keywords", self.clear_keywords))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # 봇 실행
        print("🤖 텔레그램 봇이 시작되었습니다...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # 봇 토큰을 환경변수에서 가져오기
    BOT_TOKEN = "5523500847:AAEJ46kC3hyKH3p3pnfC-7KoUfz0Ul-Sv3k"
    
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN 환경변수를 설정해주세요!")
        print("export TELEGRAM_BOT_TOKEN='your-bot-token-here'")
        exit(1)
    
    bot = TelegramScenarioBot(BOT_TOKEN)
    bot.run()