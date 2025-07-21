from insta_login import get_logged_in_driver
from insta_chatbot import get_recent_messages, generate_reply, send_reply
import time

if __name__ == "__main__":
    driver = get_logged_in_driver("박신영")
    time.sleep(5)

    print("🤖 챗봇이 상대 메시지를 기다리는 중...")

    last_seen = None

    try:
        while True:
            input("엔터치면 종료 됌")
            messages = get_recent_messages(driver)
            if not messages:
                time.sleep(3)
                continue

            last_msg = messages[-1]

            # 상대방이 보낸 새 메시지가 있다면
            if last_msg.startswith("상대:") and last_seen == None:
                print("📥 새 메시지 감지:", last_msg)
                last_seen = last_msg  # 중복 응답 방지

                reply = generate_reply(messages)
                print("🧠 GPT 응답:", reply)

                # 길면 문장 나눠서 전송
                for sentence in reply.split(". "):
                    sentence = sentence.strip()
                    if sentence:
                        send_reply(driver, sentence)
                        time.sleep(1.5)

            time.sleep(3)

    except KeyboardInterrupt:
        print("\n🛑 챗봇 종료됨")
        driver.quit()