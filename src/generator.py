import os
import time
from google.colab import drive
from google import genai
from google.genai import types

def call_ai_for_section(client, prompt_instruction, raw_data, section_name):
    """
    呼叫 Gemini API，提煉標準公文文字
    """
    full_prompt = f"{prompt_instruction}\n\n請針對【{section_name}】這個章節，將以下原始資料提煉轉譯：\n{raw_data}"
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=full_prompt,
        config=types.GenerateContentConfig(temperature=0.2)
    )
    return response.text

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
    
    # 🎯 物理防線：每一章節強制間隔 15 秒，規避 Google 針對免費版 API 的流量監控
    print("⏳ 正在轉譯：第一章節...")
    sec1 = call_ai_for_section(client, prompt_instruction, raw_meeting_data, "國內金融市場分析與研判")
    print("💤 防止 429 限制，系統強制冷卻 15 秒...")
    time.sleep(15)
    
    print("⏳ 正在轉譯：第二章節...")
    sec2 = call_ai_for_section(client, prompt_instruction, raw_meeting_data, "金管會放寬投信基金限制之影響及券商公會建議")
    print("💤 防止 429 限制，系統強制冷卻 15 秒...")
    time.sleep(15)
    
    print("⏳ 正在轉譯：第三章節...")
    sec3 = call_ai_for_section(client, prompt_instruction, raw_meeting_data, "元大證券營運概況與風險控管")
    print("💤 防止 429 限制，系統強制冷卻 15 秒...")
    time.sleep(15)
    
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
