import os
from flask import logging, Flask, render_template, request, flash, redirect, jsonify
import urllib.request, json
from app.main import bp
from config import Config
import time
import speech_recognition as sr
from random import randint
from elevenlabs import generate, play, save, set_api_key

becomeNew ={
    'id': 19,
    'channel_id': 'UCuDv5y3cjLSvZOecE77Gkfw',
    'channel_title': 'Become New',
    'channel_name': '@BecomeNew',
    'videos_count': 700,
    'link': 'https://www.youtube.com/@BecomeNew/videos',
    'channel_logo': 'https://yt3.ggpht.com/Rku879D5puL4rcGkWjNJRNjlxOSAvfIfG37cxOM12rL5Hjk9ZFmd_oBwbWZh-lc3t0PSv8R4ww=s88-c-k-c0xffffffff-no-rj-mo',
    'channel_description': 'Join John Ortberg for a series of devotional thoughts on the person we become. Sign up here for free supporting resources',
}
menloChurch ={
    'id': 5,
    'channel_id': 'UCtsi33WCfZd0n9CmK_rUAfA',
    'channel_title': 'Menlo Church',
    'channel_name': '@MenloChurch',
    'videos_count': 900,
    'link': 'https://www.youtube.com/@MenloChurch/streams',
    'channel_logo': 'https://yt3.ggpht.com/9QmAeD0tZRCBga4XKFFfb3y2c6veCKqaq5IZgHQNHMBk03MJj04vdOAIx5NK8IyMporGYJTqcg=s88-c-k-c0xffffffff-no-rj-mo',
    'channel_description': 'Our vision is to lead our generation into a transforming relationship with Jesus and authentic community with each other',
}
channels = []
channels.append(becomeNew)
channels.append(menloChurch)

def getChannelsList():
    url = Config.LIVE_DOMAIN+"/channelsList"
    response = urllib.request.urlopen(url)
    data = response.read()
    clist = json.loads(data)
    return clist

def getChannelDetails(channelName):
    url = Config.LIVE_DOMAIN+"/channelDetail/"+channelName
    response = urllib.request.urlopen(url)
    data = response.read()
    detail = json.loads(data)
    return detail

@bp.route('/')
def index():
    data = getChannelsList()
    channelsList = []
    if data['status']:
        channelsList = json.loads(data["list"])
        # print(channelsList)
    return render_template('index.html', channels=channelsList)

@bp.route('/<name>')
def chat(name):
    data = getChannelDetails(name)
    liveURL = Config.LIVE_DOMAIN
    if data['status']:
        channelDetail = json.loads(data["result"])
        preQuestions = json.loads(data['preQuestions'])
        return render_template('chat.html', channel = channelDetail, preQuestions = preQuestions, liveURL = liveURL)
    else:
        return redirect('/')

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

@bp.route('/record/<name>')
def record(name):
    liveURL = Config.LIVE_DOMAIN
    # return render_template('audio_to_text.html', liveURL = liveURL)
    return render_template('record.html', liveURL = liveURL)
    # data = getChannelDetails(name)
    # if data['status']:
    #     channelDetail = json.loads(data["result"])
    #     preQuestions = json.loads(data['preQuestions'])
    #     return render_template('record.html', channel = channelDetail, preQuestions = preQuestions, liveURL = liveURL)
    #     return render_template('record.html', channel = channelDetail, preQuestions = preQuestions, liveURL = liveURL)
    # else:
    #     return redirect('/')


@bp.route('/record2/<name>')
def record2(name):
    newPage = True
    liveURL = Config.LIVE_DOMAIN
    return render_template('record2.html', liveURL = liveURL, newPage=newPage)

@bp.route('/audio', methods=['POST'])
def audio():
    # print('*****************************************')
    # print(request.data)
    # print('*****************************************')
    audioFileName = str(random_with_N_digits(10)) + '.wav'
    audioFileFolderPath = os.path.join(Config.ANSWER_AUDIO_FOLDER, audioFileName)
    r = sr.Recognizer()
    with open(audioFileFolderPath, 'wb') as f:
        f.write(request.data)
    with sr.AudioFile(audioFileFolderPath) as source:
        audio_data = r.record(source)
        # text = r.recognize_google(audio_data, language='en-IN', show_all=True)
        text = r.recognize_google(audio_data, language='en-IN', show_all=False)
        print(text)
        return_text = text
        fileName = textToAudio(text, audioFileName)
        # try:
        #     for num, texts in enumerate(text['alternative']):
        #         return_text += str(num+1) +") " + texts['transcript']  + " <br> "
        # except:
        #     return_text = " Sorry!!!! Voice not Detected "
    # return str(return_text)
    return {"audio": fileName, "text": str(text), 'status': True}

def textToAudio(text, audioFileName):
    try:
        set_api_key(Config.ELEVENLABS_API_KEY)
        audioFileFolderPath = os.path.join(Config.QUESTION_AUDIO_FOLDER, audioFileName)
        audio = generate(
            text=text,
            voice="29cwSzDzWESPbIisY3Bi",
            model="eleven_monolingual_v1"
        )
        save(audio, audioFileFolderPath)
        return audioFileName
    except Exception as e:
        print('textToAudio Exception = ', e)
        return ''

# @bp.route("/answer_voice", methods=["POST"])
# def get_video_answer_voice():
#     try:
#         set_api_key(Config.ELEVENLABS_API_KEY)
#         answer = request.json['answer']
#         questionId = request.json['questionId']
#         channelId = request.json['channelId']
#         fAnswer = cleanhtml(answer)
#         # fAnswer = (answer[:300]) if len(answer) > 300 else answer
#         print('fAnswer = ', fAnswer)
#         audioFileName = str(channelId) + '_' + str(questionId) + '_answer.wav'
#         answerAudioPath = current_app.config['ANSWER_AUDIO_FOLDER'] + '/' + audioFileName
#         question = Question.query.filter(Question.id == questionId).first()
#         if not os.path.exists(answerAudioPath):
#             audio = generate(
#                 text=fAnswer,
#                 voice="29cwSzDzWESPbIisY3Bi",
#                 model="eleven_monolingual_v1"
#             )
#             save(audio, answerAudioPath)
#             question.audio = audioFileName
#             db.session.commit()
#         print('audioFileName = ', audioFileName)    
#         return jsonify({"audio": audioFileName, 'status': True})
#     except Exception as e:
#         print('get_video_answer_voice Exception = ', e)
#         return jsonify({"audio": '', 'status': False})