# insta_chatbot.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from openai import OpenAI
import os, time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_recent_messages(driver, limit=10):
    """
    인스타그램 메시지창에서 내/상대 대화 모두 포함한 최근 메시지 N개 수집
    """
    all_msgs = driver.find_elements(By.XPATH, '//div[@dir="auto" and contains(@class, "html-div")]')

    message_data = []

    for msg in all_msgs:
        text = msg.text.strip()
        if not text:
            continue

        # 내 메시지는 xyk4ms5 클래스가 있음
        class_attr = msg.get_attribute("class")
        role = "나" if "xyk4ms5" in class_attr else "상대"
        message_data.append(f"{role}: {text}")

    return message_data[-limit:]

def generate_reply(messages):
    # 최근 5개 메시지를 하나의 대화 컨텍스트로 구성
    context = "\n".join(messages[-5:])

    # 시스템 프롬프트
    system_prompt = '''
    당신은 대한민국 서울에 거주하는 2002년생 서강대학교 컴퓨터공학과 22학번 구종빈입니다.
    상대방과 자연스럽게 대화해야 하며, 인공지능처럼 말하면 안 됩니다.
    당신은 실존 인물이며, 상대방에게 맞춤형 답변을 해야 합니다.
    너무 형식적이거나 모범답안처럼 답하지 마세요. 말투는 싸가지 없고 무례하게 하세요.
    당신은 상남자중의 상남자인 경상도 남자입니다. 말투는 싸가지 없고 무례하게 하세요
    규칙:
    - 메시지 맥락을 이해해서 자연스럽게 이어가는 말로 답변할 것
    - "나:" 같은 접두사는 쓰지 말고, 메시지만 출력할 것
    - 이모티콘은 절대로 절대로  사용하지마
    - 젊은 사람의 말투로
    - 나의 말투는 좀 짧게 답하는 편 문장이 길면 나눠서 여러번 보내야해
    '''

    # GPT 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음은 최근 대화야:\n{context}\n이 대화에 이어서 자연스럽게 대답해줘."}
        ]
    )

    return response.choices[0].message.content.strip()

def remove_non_bmp(text):
    import re
    return re.sub(r'[^\u0000-\uFFFF]', '', text)

def send_reply(driver, text):
    try:
        # 메시지 입력창 찾기 (contenteditable div)
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                '//div[@role="textbox" and @aria-label="메시지"]'
            ))
        )
        input_box.click()
        input_box.send_keys(remove_non_bmp(text))
        time.sleep(0.5)  # 약간의 delay

        # 전송 버튼 클릭
        send_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//div[@role="button" and text()="Send"]'
            ))
        )
        send_button.click()
        print("✅ 메시지 전송 완료:", text)

    except Exception as e:
        print("❌ 메시지 전송 실패:", e)