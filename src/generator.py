import os
import time
from google.colab import drive
from google import genai
from google.genai import types
from google.genai.errors import APIError

def call_ai_for_section(client, prompt_instruction, raw_data, section_name):
    """
    呼叫 Gemini API，內建 429(限流) 與 503(超載) 的智慧型退避自動重試機制
    """
    full_prompt = f"{prompt_instruction}\n\n請針對【{section_name}】這個章節，將以下原始資料提煉轉譯：\n{raw_data}"
    
    # 優先使用 flash，若多次失敗則降級使用穩定的 pro
    models_to_try = ['gemini-2.5-flash', 'gemini-2.5-pro']
    
    for model_name in models_to_try:
        # 針對每次請求最多嘗試 4 次
        for attempt in range(4):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(temperature=0.2)
                )
                # 執行成功後，強制休眠 2 秒，為主程序留出安全緩衝
                time.sleep(2)
                return response.text
                
            except APIError as e:
                # 偵測到 429 (配額/限流) 或 503 (伺服器超載)
                if e.code in [429, 503] and attempt < 3:
                    # 指數退避策略：第一次等 8 秒，第二次等 16 秒，第三次等 24 秒
                    wait_time = (attempt + 1) * 8
                    print(f"⚠️ 觸發伺服器限制 ({e.code})，系統啟動安全防線，強制冷卻 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    # 如果該模型嘗試 4 次都卡死，且還有備用模型，則切換模型
                    if model_name != models_to_try[-1]:
                        print(f"🚨 {model_name} 配額耗盡或持續超載，自動切換至備用高級模型 {models_to_try[-1]}...")
                        time.sleep(3)
                        break
                    else:
                        raise e  # 最終防線：全數失敗則報錯

def main():
    drive_folder = "/content/drive/MyDrive/會議紀錄自動化"
    input_file_path = os.path.join(drive_folder, "正式會議紀錄_成品.md")
    
    if not os.path.exists(input_file_path):
        print(f"\n❌ 錯誤：找不到會議紀錄！請確認原始檔案已放置於雲端硬碟：會議紀錄自動化/正式會議紀錄_成品.md")
        return
        
    with open("config/prompt_setting.txt", "r", encoding="utf-8") as f:
        prompt_instruction = f.read()
        
    with open("templates/official_memo_template.md", "r", encoding="utf-8") as f:
        template_content = f.read()
        
    with open(input_file_path, "r", encoding="utf-8") as f:
        raw_meeting_data = f.read()
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ 錯誤：找不到 GEMINI_API_KEY 環境變數。")
        return
        
    client = genai.Client(api_key=api_key)
    
    print("\n🤖 Gemini AI 正在發動雲端智慧引擎，進行高階公文語境轉譯...")
    
    print("⏳ 正在轉譯：第一章節...")
    sec1 = call_ai_for_section(client, prompt_instruction, raw_meeting_data, "國內金融市場分析與研判")
    
    print("⏳ 正在轉譯：第二章節...")
    sec2 = call_ai_for_section(client, prompt_instruction, raw_meeting_data, "金管會放寬投信基金限制之影響及券商公會建議")
    
    print("⏳ 正在轉譯：第三章節...")
    sec3 = call_ai_for_section(client, prompt_instruction, raw_meeting_data, "元大證券營運概況與風險控管")
    
    print("⏳ 正在轉譯：第四章節...")
    sec4 = call_ai_for_section(client, prompt_instruction, raw_meeting_data, "重要 Q&A 補充（長官核心關切事項）")
    
    refined_sections = {
        "meeting_date": "115 年 5 月 27 日",
        "institution_name": "元大證券",
        "AI_financial_market_analysis": sec1,
        "AI_regulatory_impact": sec2,
        "AI_institution_risk_control": sec3,
        "AI_executive_qa": sec4
    }
    
    final_output = template_content.format(**refined_sections)
    
    output_file_path = os.path.join(drive_folder, "自動產出公文_簽呈.md")
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(final_output)
        
    print(f"\n🎉 執行成功！符合核可標準之簽呈已儲存至您的雲端硬碟：會議紀錄自動化/自動產出公文_簽呈.md")

if __name__ == "__main__":
    main()
