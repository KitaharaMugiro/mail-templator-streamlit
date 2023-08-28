import openai
import streamlit as st

openai.api_base = "https://oai.langcore.org/v1"

def main():
    st.title('メール自動作成ツール')
    st.write('URLを入力すると、その内容を元にChatGPTを使ってメールを自動作成するツールです。')

    url = st.text_input('URL', "https://about.yahoo.co.jp/hr/job-info/role/1601/")
    mail_template = st.text_area('メールのテンプレート', get_mail_template(), height=500)

    if st.button('メールを作成する'):
        with st.spinner('メールを作成中です...'):
            mail, prompt = create_mail(url, mail_template)
        st.markdown('<span style="font-size:0.8em;color:gray">メールを作成しました！</span>', unsafe_allow_html=True)
        st.text_area("作成されたメール", mail, height=500)

        expander = st.expander("実行したプロンプト", expanded=False)
        with expander:
            st.text(prompt)


        



def create_mail(url, mail_template):
    from trafilatura import fetch_url, extract
    from trafilatura.settings import use_config
    config = use_config()
    config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")
    config.set("DEFAULT", "MIN_EXTRACTED_SIZE", "1000")
    downloaded = fetch_url(url)
    result = extract(downloaded, config=config)

    # テキストが長すぎる場合は、一部を削除します。
    content = result
    if len(content) > 2500: 
        content = result[:2500]
    
    prompt = f"""
    企業情報:
    {content}

    MAIL_TEMPLATE:
    {mail_template}

    制約条件
    - MAIL_TEMPLATEにある[]を全て埋めていること
    - MAIL_TEMPLATE:の文章をそのまま使うこと
    - []は削除してください

    補完したMAIL_TEMPLATE:
    """

    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
        ]

    )
    mail = res.choices[0].message.content

    return mail, prompt

    
def get_mail_template():
    day1, day2, day3, day1_youbi, day2_youbi, day3_youbi = get_jikoku()

    MAIL_TEMPLATE = f"""
[企業名]様

初めまして、ちぇんと申します。

ホームページを拝見し、[企業の困っていること]で課題を抱えられているのではないかと思い、ご連絡させていただきました。

私は[企業の困っている領域]での経験があります。
[企業に刺さりそうな謳い文句]

ご多用かと存じますが、下記の中から30分、面接のお時間を頂戴できますと幸いです。

- {day1}({day1_youbi}) 11:00 ~ 18:00
- {day2}({day2_youbi}) 11:00 ~ 18:00
- {day3}({day3_youbi}) 11:00 ~ 18:00

ご連絡を心よりお待ち申し上げております。
    """
    return MAIL_TEMPLATE

def get_jikoku():
    import datetime
    import workdays
    import locale
    locale.setlocale(locale.LC_TIME, '')
    today = datetime.date.today()
    day1 = workdays.workday(today, days=2)
    day2 = workdays.workday(today, days=3)
    day3 = workdays.workday(today, days=4)
    day1_youbi = day1.strftime('%a')
    day2_youbi = day2.strftime('%a')
    day3_youbi = day3.strftime('%a')
    day1 = day1.strftime('%-m/%-d')
    day2 = day2.strftime('%-m/%-d')
    day3 = day3.strftime('%-m/%-d')
    return day1, day2, day3, day1_youbi, day2_youbi, day3_youbi




if __name__ == '__main__':
    main()
