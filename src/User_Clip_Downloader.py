#######################################
#### 필수 설치 목록                 ####
#### pip install selenium          ####
#### pip install webdriver-manager ####
#### pip install re                ####
#######################################



from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from webdriver_manager.chrome import ChromeDriverManager
from urllib.request import urlretrieve
import os

import csv
import logging
import traceback
import datetime
from datetime import timedelta
import requests

from multiprocessing import  cpu_count, Pool, freeze_support
from tqdm import tqdm

from tkinter import messagebox


# 이 부분은 일부러 비웠습니다.
# 아래 두 주소 참고해서 본인만의 키를 발급 받아 사용하세요 킹아!
# https://dev.twitch.tv/docs/api/get-started
# https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#oauth-client-credentials-flow
headers={'Authorization': '', 'client-id': ''}


# 스트리머별 ID
wak_id = '49045679'
ine_id = '702754423'
jing_id = '181985298'
lilpa_id = '105447547'
jururu_id = '203667951'
segu_id = '245391004'
vii_id = '195641865'


# 쪼갤 시간 (초) 안씀
Time_Split_Step_sec = 86400 #7200


def clip_search(streamer_id, now, dt, next_page=''):

    now_1 =  now + timedelta(seconds=dt)

    now_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    now_1_str = now_1.strftime("%Y-%m-%dT%H:%M:%SZ")

    response = requests.get("https://api.twitch.tv/helix/clips?broadcaster_id="+streamer_id+"&started_at="+now_str+"&ended_at="+now_1_str+'&first=100'+next_page, headers=headers)
    try:
        res = response.json()
        clips = res['data']
        page = res["pagination"]
    except:
        clips = response.json()
        #logger.error("API 응답 오류 : " + str(clips))

    if len(page)>0:
        res1 = clip_search(streamer_id, now, dt, '&after=' + page['cursor'] )
        clips = clips + res1
    
    return clips

def get_clip_info_from_twitch(args):

    st, et, streamer_id, user_name = args

    now = st
    remained_time = et - now
    remained_time = remained_time.total_seconds()

    dt = remained_time

    res_lists = []
    while remained_time>0:

        clips = clip_search(streamer_id, now, dt)

        for clip in clips:
            if clip['creator_name'] == user_name:
                # 결과 배열 생성
                res_lists.append(clip)


        now = now + timedelta(seconds=dt)

        remained_time = et - now
        remained_time = remained_time.total_seconds()

        #print(remained_time)
    #print(st,et)
    return res_lists


def check_saved_file(Clip_file):

    if not os.path.exists(Clip_file):
        
        f_clips = open(Clip_file,'a', encoding='UTF8', newline="")       
        wr = csv.writer(f_clips)
        keys = ['id', 'url', 'embed_url', 'broadcaster_id', 'broadcaster_name', 'creator_id', 'creator_name', 'video_id', 'game_id', 'language', 'title', 'view_count', 'created_at', 'thumbnail_url', 'duration', 'vod_offset']
        wr.writerow(keys)
        f_clips.close()

        return False, None

    else:
        f_clips = open(Clip_file,'r', encoding='UTF8')
        rdr = csv.reader(f_clips)

        read_csv = list(rdr)
        n = len(read_csv)

        #라인 개수
        if n >1:
            if read_csv[-1][-1] == 'error':
                st_all = read_csv[-1][0]
                f_clips.close()


                f_clips = open(Clip_file,'w', encoding='UTF8', newline="")
                wr = csv.writer(f_clips)
                wr.writerows(read_csv[0:-1])
                f_clips.close()

                return False, st_all

            else:
                return True, None


        elif n == 1:
            f_clips.close()
            return False, None

        else:
            f_clips.close()
            f_clips = open(Clip_file,'w', encoding='UTF8', newline="")
            wr = csv.writer(f_clips)
            keys = ['id', 'url', 'embed_url', 'broadcaster_id', 'broadcaster_name', 'creator_id', 'creator_name', 'video_id', 'game_id', 'language', 'title', 'view_count', 'created_at', 'thumbnail_url', 'duration', 'vod_offset']
            wr.writerow(keys)
            f_clips.close()

            return False, None


def read_config_file():

    ### config 파일 읽기

    f_conf = open('config.txt','r', encoding='UTF8')

    conf = f_conf.read().split('\n')

    # 스트리머
    streamer_name = conf[1]

    if streamer_name == '우왁굳':
        streamer_id = wak_id
    elif streamer_name == '아이네':
        streamer_id = ine_id
    elif streamer_name == '징버거':
        streamer_id = jing_id
    elif streamer_name == '릴파':
        streamer_id = lilpa_id
    elif streamer_name == '주르르':
        streamer_id = jururu_id
    elif streamer_name == '고세구':
        streamer_id = segu_id
    elif streamer_name == '비챤':
        streamer_id = vii_id

    # 자기 닉네임
    user_name = conf[4]

    # 검색 시작 날짜
    st_string = conf[7]

    st_list = st_string.split(' ')  # 나누기
    st_date = st_list[0].split('-') # 날짜
    st_time = st_list[1].split(':') # 시간

    st_all = datetime.datetime(int(st_date[0]), int(st_date[1]), int(st_date[2]), int(st_time[0]), int(st_time[1]), int(st_time[2]))
    st_all = st_all - timedelta(hours=9)    # 트위치 서버는 UTC+0

    # 검색 끝 날짜
    et_string = conf[10]

    et_list = et_string.split(' ')  # 나누기
    et_date = et_list[0].split('-') # 날짜
    et_time = et_list[1].split(':') # 시간

    et_all = datetime.datetime(int(et_date[0]), int(et_date[1]), int(et_date[2]), int(et_time[0]), int(et_time[1]), int(et_time[2]))
    et_all = et_all - timedelta(hours=9)    # 트위치 서버는 UTC+0

    f_conf.close()

    return streamer_id, user_name, st_all, et_all




if __name__ == '__main__':

    freeze_support()

    #로그 설정
    logger = logging.getLogger()
    logger.handlers = []
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(formatter)
    logger.addHandler(streamhandler)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    filehandler = logging.FileHandler('logs/logfile_{:%Y%m%d-%H_%M_%S}.log'.format(datetime.datetime.now()), encoding='utf-8')
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)

    logger.info("시작")
    res_lists=[]

    ### 클립 주소 목록 있는지 확인

    Clip_file = "Clip_list.csv"

    st = None

    try:

        boo, st = check_saved_file(Clip_file)

        #if not os.path.exists(Clip_file):
        if not boo:
            logger.info("cofing 파일 읽기")
            streamer_id, user_name, st_all, et_all = read_config_file()

            if st is not None:
                st_all = datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S") - timedelta(hours=9)

            '''
            ## 시간 쪼개기
            # 트위치 서버 터져도 중간부터 수집 시작할 수 있게 태스크 분리
            logger.info("시간대 분리 시작")
            time_list =[]
            dt = et_all - st_all
            dt = dt.total_seconds()
            idx = 0

            while True:
                dt = dt - Time_Split_Step_sec
                st = st_all + timedelta(seconds=Time_Split_Step_sec)*idx

                if dt>0:                    
                    et = st_all + timedelta(seconds=Time_Split_Step_sec)*(idx+1)

                    time_list.append([st, et])
                else:
                    time_list.append([st, et_all])
                    break

                idx = idx + 1

            '''

            # 시간 쪼개기 필요 없음. 속도 빠르니 그냥 쓰자
            time_list =[[st_all, et_all]]


            ### 트위치 API 리퀘스트 시작 ###
            ## 아이디 매칭하여 클립 정보 얻기 ##
            logger.info("Twitch API 리퀘 시작")

            for args in time_list:

                st = args[0]
                et = args[1]

                log_text = (st + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")+" ~ "+(et + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")+" - 클립 정보 수집 시작"
                logger.info(log_text)


                res_lists = []

                now = st
                remained_time = et - now
                remained_time = remained_time.total_seconds()

                
                cpu_num = cpu_count()
                task_num = cpu_num*3

                
                pool = Pool(cpu_num)
                #pbar = tqdm(total=cpu_num)

                args = []
                dt = remained_time/task_num
                for i in range(0, task_num):
                    args.append([st + timedelta(seconds=(dt*i)), st + timedelta(seconds=(dt*(i+1))), streamer_id, user_name])
                
                #'''
                raw_res_lists=[]
                #raw_res_lists = pool.map(get_clip_info_from_twitch, args)
                for x in tqdm(pool.imap(get_clip_info_from_twitch, args), total=task_num):
                    raw_res_lists.append(x)
                pool.close()
                pool.join()
                '''
                
                # 싱글 코어용
                args=[st, et, streamer_id, user_name]
                raw_res_lists=[]
                raw_res_lists.append(get_clip_info_from_twitch(args))
                '''

                res_lists = []
                for res in raw_res_lists:
                    res_lists = res_lists + res


                logger.info("클립 정보 수집 완료")


                # 클립 주소 파일에 저장하기           

                f_clips = open(Clip_file,'a', encoding='UTF8', newline="")
                for res in res_lists:

                    wr = csv.writer(f_clips)                    
                    wr.writerow(list(res.values()))

                    #f_clips.write(str(res)+'\n')

                        
                f_clips.close()

                #print("클립 주소 저장 완료")
                #print("다음 실행 시 왁물원이 아닌 저장된 파일에서 클립을 불러옵니다.")
                log_text = (st + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")+" ~ "+(et + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")+" - 클립 정보 저장 완료"
                logger.info(log_text)

            logger.info("모든 클립 정보 저장 완료\n 다음 실행 시 저장된 파일에서 정보를 불러옵니다.")
            #messagebox.showinfo("알림", "모든 클립 정보 저장 완료\n다음 실행 시 저장된 파일에서 정보를 불러옵니다.")
            boo = True




        ## 클립 주소 파일이 존재할 시 불러오기

        #print("저장된 클립 주소 파일에서 데이터를 불러옵니다.")
        logger.info("저장된 클립 정보 파일에서 데이터를 불러옵니다.")

        # 클립 주소 파일 열기
        f_clips = open(Clip_file,'r', encoding='UTF8')

        rdr = csv.reader(f_clips)

        read_csv = list(rdr)

        res_text_list = read_csv 

        keys = res_text_list.pop(0)    #맨 윗줄은 정보

        f_clips.close()


        res_lists = []
        for text_list in res_text_list:

            list_to_dict = []
            for i in range(len(keys)):
                list_to_dict.append([keys[i],text_list[i]])

            dict_ = dict(list_to_dict)
            res_lists.append(dict_ )




        #print("클립 주소 불러오기 완료")
        logger.info("클립 주소 불러오기 완료")



        #크롬 실행
        driver = webdriver.Chrome(ChromeDriverManager().install())



        ### 트위치 클립 다운로드 ###
        #print('클립 다운로드를 시작합니다.')
        logger.info('클립 다운로드를 시작합니다.')


        for res_list in res_lists:

            # 스트리머 이름으로 폴더 생성
            directory_streamer = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', res_list['broadcaster_name'])

            # 폴더 존재 여부 확인 후 폴더 생성
            if not os.path.exists(directory_streamer):
                os.mkdir(directory_streamer)



            # 날짜별로 폴더 생성
            vid_UTC0 = datetime.datetime.strptime(res_list['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            vid_UTC9 = vid_UTC0 + timedelta(hours=9)
            vid_time = vid_UTC9.strftime("%Y-%m-%dT%H:%M:%SZ")
            vid_date = vid_time[0:vid_time.find("T")]
            directory_date= re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_date)

            # 폴더 존재 여부 확인 후 폴더 생성
            if not os.path.exists(directory_streamer+'/'+ directory_date):
                os.mkdir(directory_streamer+'/'+ directory_date)

            Clip_link = res_list['url']

            #print("클립 접속 : ", Clip_link)
            logger.info("클립 접속 : " + Clip_link)

            # 클립 주소가 아닐 시 루프 넘어감
            if Clip_link.find('https://clips.twitch.tv/')<0:
                #print("!유효한 주소가 아닙니다 : ", Clip_link)
                logger.warning("!유효한 주소가 아닙니다 : " + Clip_link)
                continue

            # 주소 이동
            driver.get(Clip_link)

            # 영상 정보 받기
            vid_url = ''
            idx = 0
            while vid_url.find('https://')<0:                               #while문은 로딩이 덜 되을 떄를 대비 10초까지 기다림
                time.sleep(0.1)                    
                idx = idx + 1

                if driver.current_url.find('clip_missing')>=0:
                    logger.error("!클립이 지워졌습니다 : " + Clip_link)       # 클립이 지워졌을 경우
                    idx = 100
                    break

                vid_url_element = driver.find_element(By.TAG_NAME,'video')
                vid_url = vid_url_element.get_attribute('src')

                if idx>=100:
                    break

            if idx>=100:
                logger.error("영상이 존재하지 않습니다? 왜지? : " + Clip_link)
                continue


            # 제목 가져오기
            vid_title = res_list['title']


            #logger.info(vid_date)

            #파일명엔 특수문자가 불가능. 전부 _로 치환
            vid_title = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_title)
            vid_time = re.sub('[^0-9a-zA-Zㄱ-힗\s]', '_', vid_time).replace('T','_').replace('Z','')
            logger.info("클립 다운로드 시작 : " + vid_title + " " + vid_time)

            #-> from urllib.request import urlretrieve 참조
            #-> 영상을 실제로 다운로드
            urlretrieve(vid_url, directory_streamer + '/' + directory_date + '/['+vid_time+']'+vid_title+'.mp4')

            logger.info("클립 다운로드 완료")




        logger.info("모든 클립 다운로드가 완료되었습니다.")
        
        driver.close()
        #messagebox.showinfo("알림", "모든 클립 다운로드가 완료되었습니다.")


    except:
        #logger.error(str(res_lists))
        logger.error(traceback.format_exc())

        if traceback.format_exc().find("Connection to api.twitch.tv timed out")>=0:
            messagebox.showwarning("타임아웃", "트위치 서버가 아파서 클립 정보를 받지 못했습니다.\n 이어서 진행하려면 프로그램을 바로 다시 실행해주세요")

        else:
            messagebox.showerror("치명적인 오류 발생", "알 수 없는 오류가 발생했습니다.\n 용량이 가장 큰 log 파일을 피드백 사이트에 보고해주세요")

        if not boo:     
            csv_error_log = [(st + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")] + ['error']*15

            f_clips = open(Clip_file,'a', encoding='UTF8',newline="")       
            wr = csv.writer(f_clips)
            wr.writerow(csv_error_log)
            f_clips.close()
        
