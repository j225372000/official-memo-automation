import os
from google.colab import drive
from openai import OpenAI

def call_ai_for_section(client, prompt_instruction, raw_data, section_name):
    full_prompt = f"{prompt_instruction}\n\n請針對【{section_name}】這個章節，將以下原始資料提煉轉譯：\n{raw_data}"
    
    response = client.chat.completions.create(
        model="gpt-4o",  # 可依實際需求更換模型
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content

def main():
    print("📂 正在連動您的 Google Drive...")
    drive.mount('/content/drive')
    
    # 指向您在雲端硬碟建立的新資料夾路徑
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
        
    client = OpenAI(api_key=os.environ.get("AI_API_KEY"))
    
    print("\n🤖 AI 正在發動雲端智慧引擎，進行高階公文語境轉譯...")
    
    refined_sections = {
        "meeting_date": "115 年 5 月 27 日",
        "institution_name": "元大證券",
        "AI_financial_market_analysis": call_ai_for_section(client, prompt_instruction, raw_meeting_data, "國內金融市場分析與研判"),
        "AI_regulatory_impact": call_ai_for_section(client, prompt_instruction, raw_meeting_data, "金管會放寬投信基金限制之影響及券商公會建議"),
        "AI_institution_risk_control": call_ai_for_section(client, prompt_instruction, raw_meeting_data, "元大證券營運概況與風險控管"),
        "AI_executive_qa": call_ai_for_section(client, prompt_instruction, raw_meeting_data, "重要 Q&A 補充（長官核心關切事項）")
    }
    
    final_output = template_content.format(**refined_sections)
    
    output_file_path = os.path.join(drive_folder, "自動產出公文_簽呈.md")
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(final_output)
        
    print(f"\n🎉 完美通關！成品已直接儲存至您的雲端硬碟：會議紀錄自動化/自動產出公文_簽呈.md")

if __name__ == "__main__":
    main()
