import sms
import sqlite3
import streamlit as st
from datetime import datetime

conn = sqlite3.connect("sdhsf2.db")
cursor = conn.cursor()


# 예약 정보 테이블 생성
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    booth TEXT NOT NULL,
    order_number INTEGER NOT NULL,
    time TEXT NOT NULL
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS order_sequence (
    booth TEXT PRIMARY KEY,
    last_order_number INTEGER NOT NULL
)
"""
)








booth_lst = [
    #"2-9반: 육인이네 먹퀴즈",
    "2-5반: 경제: 투자의 귀재들",
    "1-7반: 사대부고 광기.(광고 기획)",
    "미술실: 바다유리 업사이클링 작품 만들기",
    "1-8반: 이 방송은 이제 제 겁니다.",
    "도서관: 뇌주름 잡히는 방탈출",
    "구름다리 : 두 줄도 너무 길다(사진과 함께 쓰는 시 한편)",
    "2-6반: 음식 체험 미니 탕후루",
    #"글로벌외국어실: 영어 스피드 퀴즈",
    "아톰실: 향기의 과학",
    "2-7반: 과학과 함께하는 놀이 체험",
    "2-8반: 피부 봉합 실습",
    "1-9반: 심리 테스트 카페(심리학, 뇌과학)",
    "바이오토피아실: 너에게 좋은향이 나는데? 내 취향♡-친환경 손소독제 만들기",
    "국어학습실, 진로·진학활동실, 미래관 통로 : 두 번째 지구는 없다!",
    "코스모스실: 당신의 쿠키를 선택하세요!★ 기관계 쿠키 만들기",
    "컴퓨터실: 프로그래밍과 인공 지능 체험 학습",
    "사격장: 체육(사격, 기록 도전! 마인드 컨트롤)",
    "웅비관: 체육(농구, 기록 도전! 자유투 및 3점슛)",
    "학습도움반: 바리스타 음료 서비스",
    "사회학습실: 학술제 참가자 발표 영상_흡염 및 학교 폭력 예방 활동",
]

# 초기 대기 순서 설정 (0으로 시작)


for b in booth_lst:
    # 현재 부스가 이미 존재하는지 확인
    cursor.execute("SELECT booth FROM order_sequence WHERE booth = ?", (b,))
    exists = cursor.fetchone()

    # 부스가 존재하지 않는 경우에만 초기화
    if not exists:
        cursor.execute(
            "INSERT INTO order_sequence (booth, last_order_number) VALUES (?, 0)",
            (b,),
        )

# 변경사항 저장
conn.commit()

# 연결 종료
conn.close()

# 데이터베이스 공유용 함수


def get_database_connection():
    return sqlite3.connect("sdhsf2.db")


booth_number = 1 

# 손님용 인터페이스
def show_customer_interface(booth_number):
    st.session_state.logink = 12
    # Streamlit 페이지 설정
    st.title(booth_lst[booth_number])
    st.header("예약하기")
    st.divider()


    # 입력 필드
    name = st.text_input("이름")
    phone = st.text_input("전화번호")
       # if phone = f(reservation[2])

    # 제출 버튼
    submit = st.button("예약 제출")
    st.divider()

    # 제출 버튼이 눌렸을 때의 동작
    if submit:
        # 데이터베이스 연결
        conn = get_database_connection()
        cursor = conn.cursor()
        booth_n = booth_lst[booth_number]
        print(booth_n)


        cursor.execute(
            "SELECT COUNT(*) FROM reservations WHERE booth = ? AND phone = ?",
            (booth_n, phone),
        )
        existing_reservation_count = cursor.fetchone()[0]

        if existing_reservation_count > 0:
            st.warning("이미 해당 부스에 예약이 존재합니다. 중복 예약은 허용되지 않습니다.")
        else:
            # 대기 순서 가져오기
            time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
            cursor.execute(
                "SELECT last_order_number FROM order_sequence WHERE booth =?", (booth_n,)
            )
            last_order_number = cursor.fetchone()[0]
            print(last_order_number)

            # 예약 정보에 순서 추가
            order_number = f"{booth_lst[booth_number]} {str(last_order_number + 1).zfill(2)}번"

            # 예약 정보 삽입
            cursor.execute(
                "INSERT INTO reservations (name, phone, booth, order_number,time) VALUES (?, ?, ?, ?,?)",
                (name, phone, booth_lst[booth_number], order_number,time),
            )

            # 부스별 순서 업데이트

            last_order_number += 1
            cursor.execute(
                "UPDATE order_sequence SET last_order_number = ? WHERE booth =?",
                (last_order_number, booth_lst[booth_number]),
            )

            # 변경사항 저장 및 연결 종료
            conn.commit()
            conn.close()

            # 예약 완료 메시지 표시
            st.success(f"예약 완료! 순서는 {order_number} 입니다.")
            receiver_lst = []
            receiver_lst.append(phone)
            re_message = f"{booth_lst[booth_number]} 예약번호는 {last_order_number}입니다."
            # re_message2 = f"준비완료 문자를 받은 후 5분이 지나면 예약은 초기화됩니다."

            t1 = sms.send_sms(receivers=receiver_lst, message=re_message)
            receiver_lst = []
            print(t1)

    
    st.divider()
            

    st.text('프로그램 관련 문의사항 01022619433')


# 부스 관리자용 인터페이스
def get_reservations(booth_number):

    #send_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    st.title("부스 관리 시스템")
    st.header("예약 목록")

    sumlist = []

    conn = get_database_connection()
    cursor = conn.cursor()
    

    booth_n=booth_lst[booth_number]
    # 예약 목록 가져오기
    cursor.execute(
        "SELECT id, name, phone, booth, order_number, time  FROM reservations WHERE booth=?",
        (booth_n,),
    )

    reservations = cursor.fetchall()

    for reservation in reservations:
        if f"approved_{reservation[0]}" not in st.session_state:
            st.session_state[f"approved_{reservation[0]}"] = False

        if st.session_state[f"approved_{reservation[0]}"]:
            st.markdown(
                f'<span style="text-decoration: line-through;">'
                f"{reservation[4]}, 이름: <u><b>{reservation[1]}</b></u>, 전화번호: <u><b>{reservation[2]}</b></u> <br> 시간 : <u><b>{reservation[5]}</b></u>, 장소: {reservation[3]} "
                f"</span>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"{reservation[4]},  이름: <u><b>{reservation[1]}</b></u>, 전화번호: <u><b>{reservation[2]}</b></u> <br> 시간: <u><b>{reservation[5]}</b></u>, 장소: {reservation[3]}", unsafe_allow_html =True
            )
        
        # 예약 승인 버튼
        agree_b = st.checkbox(f"{reservation[4]} 예약 :blue[승인]")            
        if agree_b:         
            send_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
            receiver_lst = []
            receiver_lst.append(reservation[2])
            re_message = f"{reservation[1]}님 5분 안에 {reservation[4]} 방문해주세요"
            t1 = sms.send_sms(receivers=receiver_lst, message=re_message)
            st.session_state[f"approved_{reservation[0]}"] = True
            st.success(f"{reservation[1]}님의 예약(ID: {reservation[0]})이 승인되었습니다.")
        
        diagree_b = st.checkbox(f"{reservation[4]} 예약 :red[취소]")
        if diagree_b:
            send_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
            receiver_lst = []
            receiver_lst.append(reservation[2])
            re_message = f"{reservation[1]}님 {reservation[3]}이 마감되었습니다. 죄송합니다. "
            t1 = sms.send_sms(receivers=receiver_lst, message=re_message)
            st.session_state[f"approved_{reservation[0]}"] = True
            st.success(f"{reservation[1]}님의 예약(ID: {reservation[0]}) 이(가) 취소되었습니다.")
        note = st.number_input('받은 금액', key =reservation[4],value=0)
        sumlist.append(note)
        st.divider()  
        
    price_sum = sum(sumlist)
    st.write('수익',price_sum)   
        
        
         
    # 연결 종료
    conn.close()



# 관리자 인터페이스 비밀번호
fixed_password = "$$2023sdhs!@"

if 'logink' not in st.session_state:
    st.session_state.logink = 0
    

def login(password):
    """로그인"""
    return password == fixed_password

# 로그인 페이지 구성
def login_page():
    st.title("로그인")

    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        if login(password):
            st.success("로그인 성공")
            # 다음 화면으로 이동
            st.session_state.logink = 45
            return True
        else:
            st.error('잘못된 비밀번호')
            
            
            
# 메인 페이지 구성
def main_page():
    # if interface_option1==  "2-9반: 육인이네 먹퀴즈":
    #     booth_number = 0
    #     get_reservations(booth_number)

    if interface_option1 ==  "2-5반: 경제: 투자의 귀재들":
        booth_number = 1
        get_reservations(booth_number)
        
    if interface_option1 ==  "1-7반: 사대부고 광기.(광고 기획)":
        booth_number = 2
        get_reservations(booth_number)
        
    if interface_option1 ==  "미술실: 바다유리 업사이클링 작품 만들기":
        booth_number = 3
        get_reservations(booth_number)
        
    if interface_option1 ==  "1-8반: 이 방송은 이제 제 겁니다.":
        booth_number = 4
        get_reservations(booth_number)
        
    if interface_option1==  "도서관: 뇌주름 잡히는 방탈출":
        booth_number = 5
        get_reservations(booth_number)
        
    if interface_option1 ==  "구름다리 : 두 줄도 너무 길다(사진과 함께 쓰는 시 한편)":
        booth_number = 6
        get_reservations(booth_number)
        
    if interface_option1 ==  "2-6반: 음식 체험 미니 탕후루":
        booth_number = 7
        get_reservations(booth_number)
        
    # if interface_option1 ==  "글로벌외국어실: 영어 스피드 퀴즈":
    #     booth_number = 8
    #     get_reservations(booth_number)
        
    if interface_option1==  "아톰실: 향기의 과학":
        booth_number = 9
        get_reservations(booth_number)
        
    if interface_option1 ==  "2-7반: 과학과 함께하는 놀이 체험":
        booth_number = 10
        get_reservations(booth_number)
        
    if interface_option1 ==  "2-8반: 피부 봉합 실습":
        booth_number = 11
        get_reservations(booth_number)
        
    if interface_option1 ==  "1- 9반: 심리 테스트 카페(심리학, 뇌과학)":
        booth_number = 12
        get_reservations(booth_number)
        
    if interface_option1 ==  "바이오토피아실: 너에게 좋은향이 나는데? 내 취향♡-친환경 손소독제 만들기":
        booth_number = 13
        get_reservations(booth_number)
        
    if interface_option1 ==  "국어학습실, 진로·진학활동실, 미래관 통로 : 두 번째 지구는 없다!":
        booth_number = 14
        get_reservations(booth_number)
        
    if interface_option1 ==  "코스모스실: 당신의 쿠키를 선택하세요!★ 기관계 쿠키 만들기":
        booth_number = 15
        get_reservations(booth_number)
        
    if interface_option1 ==  "컴퓨터실: 프로그래밍과 인공 지능 체험 학습":
        booth_number = 16
        get_reservations(booth_number)
        
    if interface_option1 ==  "사격장: 체육(사격, 기록 도전! 마인드 컨트롤)":
        booth_number = 17
        get_reservations(booth_number)

    if interface_option1==  "웅비관: 체육(농구, 기록 도전! 자유투 및 3점슛)":
        booth_number = 18
        get_reservations(booth_number)

    if interface_option1 ==  "학습도움반: 바리스타 음료 서비":
        booth_number = 19
        get_reservations(booth_number)

    if interface_option1 ==  "사회학습실: 학술제 참가자 발표 영상_흡염 및 학교 폭력 예방 활동":
        booth_number = 20
        get_reservations(booth_number)



    


# 인터페이스 선택
interface_option = st.sidebar.selectbox("인터페이스 선택", ["고객용 인터페이스", "부스 관리용 인터페이스"])
interface_option1= st.sidebar.selectbox("부스선택", booth_lst)

if interface_option == "고객용 인터페이스":
    # if interface_option1==  "2-9반: 육인이네 먹퀴즈":
    #     booth_number = 0
    #     show_customer_interface(booth_number)
    
    if interface_option1 ==  "2-5반: 경제: 투자의 귀재들":
        booth_number = 1
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "1-7반: 사대부고 광기.(광고 기획)":
        booth_number = 2
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "미술실: 바다유리 업사이클링 작품 만들기":
        booth_number = 3
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "1-8반: 이 방송은 이제 제 겁니다.":
        booth_number = 4
        show_customer_interface(booth_number)
    
    if interface_option1==  "도서관: 뇌주름 잡히는 방탈출":
        booth_number = 5
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "구름다리 : 두 줄도 너무 길다(사진과 함께 쓰는 시 한편)":
        booth_number = 6
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "2-6반: 음식 체험 미니 탕후루":
        booth_number = 7
        show_customer_interface(booth_number)
    
    # if interface_option1 ==  "글로벌외국어실: 영어 스피드 퀴즈":
    #     booth_number = 8
    #     show_customer_interface(booth_number)
    
    if interface_option1==  "아톰실: 향기의 과학":
        booth_number = 9
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "2-7반: 과학과 함께하는 놀이 체험":
        booth_number = 10
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "2-8반: 피부 봉합 실습":
        booth_number = 11
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "1- 9반: 심리 테스트 카페(심리학, 뇌과학)":
        booth_number = 12
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "바이오토피아실: 너에게 좋은향이 나는데? 내 취향♡-친환경 손소독제 만들기":
        booth_number = 13
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "국어학습실, 진로·진학활동실, 미래관 통로 : 두 번째 지구는 없다!":
        booth_number = 14
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "코스모스실: 당신의 쿠키를 선택하세요!★ 기관계 쿠키 만들기":
        booth_number = 15
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "컴퓨터실: 프로그래밍과 인공 지능 체험 학습":
        booth_number = 16
        show_customer_interface(booth_number)
    
    if interface_option1 ==  "사격장: 체육(사격, 기록 도전! 마인드 컨트롤)":
        booth_number = 17
        show_customer_interface(booth_number)

    if interface_option1==  "웅비관: 체육(농구, 기록 도전! 자유투 및 3점슛)":
        booth_number = 18
        show_customer_interface(booth_number)

    if interface_option1 ==  "학습도움반: 바리스타 음료 서비":
        booth_number = 19
        show_customer_interface(booth_number)

    if interface_option1 ==  "사회학습실: 학술제 참가자 발표 영상_흡염 및 학교 폭력 예방 활동":
        booth_number = 20
        show_customer_interface(booth_number)

elif interface_option == "부스 관리용 인터페이스":
    if st.session_state.logink == 45:
        main_page()
    elif login_page():
        main_page()
    
    
    
    
    
    
    
    
    #login_page()


