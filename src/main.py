#######################################
#### 필수 설치 목록                 ####
#### pip install selenium          ####
#### pip install webdriver-manager ####
#### pip install re                ####
#######################################


import logging
import traceback

import datetime, os
from datetime import timedelta
import csv

from multiprocessing import freeze_support
from tkinter import messagebox


# 내가 싼 라이브러리
from Twitch_API import Twitch_API
from Read_Clip_list_and_Downloader import Read_Clip_list_and_Downloader


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


    TAPI = Twitch_API(Clip_file, logger)
    RCLD = Read_Clip_list_and_Downloader(Clip_file, logger)

    st = None

    try:

        TAPI.Get_and_Save_Clip_list()

        RCLD.Run()

        #messagebox.showinfo("알림", "모든 클립 다운로드가 완료되었습니다.")


    except:
        #logger.error(str(res_lists))
        logger.error(traceback.format_exc())

        if traceback.format_exc().find("Connection to api.twitch.tv timed out")>=0:
            messagebox.showwarning("타임아웃", "트위치 서버가 아파서 클립 정보를 받지 못했습니다.\n 이어서 진행하려면 프로그램을 바로 다시 실행해주세요")

        else:
            messagebox.showerror("치명적인 오류 발생", "알 수 없는 오류가 발생했습니다.\n 마지막으로 생성된 log 파일을 피드백 사이트에 보고해주세요")

        if not TAPI.boo:     
            csv_error_log = [(st + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")] + ['error']*17

            f_clips = open(Clip_file,'a', encoding='UTF8',newline="")       
            wr = csv.writer(f_clips)
            wr.writerow(csv_error_log)
            f_clips.close()
        
