from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio
from openpibo.device import Device
from openpibo.motion import Motion
from openpibo.audio import Audio
from threading import Timer
import os, random, asyncio

audio = Audio()
motion = Motion()
device = Device()
VOLUME = 100

theme = "default" # default, dark, mint, retro, pastel
topic = "해양환경공단"
qlist = [
    "해양환경공단의 주요 역할은 무엇인가요?",
    "일반 시민이 해양환경공단과 함께 할 수 있는 활동은 무엇이 있을까요?",
    "해양환경공단은 어떻게 해양 오염을 모니터링하나요?",
    "해양환경공단은 어떤 종류의 연구를 수행하나요?",
    "해양환경공단은 오염 사고 발생 시 어떤 대응을 하나요?",
    "해양환경공단은 국제적으로 어떤 활동을 하나요?",
    "해양쓰레기를 줄이기 위한 방법은 무엇이 있나요?",
    "바다도 건강검진을 할까?",
    "갯벌에 빠졌을 때 어떻게 해야 하는지 알려줘",
    "해양환경 이동교실이 뭐야?",
    "해양환경공단에 대해 더 알고 싶다면 어디서 정보를 얻을 수 있나요?",
    "지구 온난화란 무엇인가요?",
    "지구 온난화의 주요 원인은 무엇인가요?",
    "지구 온난화는 ‘기후’에 어떤 영향을 미치나요?",
    "지구 온난화가 ‘우리에게’ 미치는 영향은 무엇인가요?",
    "지구 온난화가 ‘해양에’ 미치는 영향은 무엇인가요?",
    "지구 온난화를 막기 위해 우리가 할 수 있는 일은 무엇인가요?",
    "바다가 지구 환경에 미치는 중요한 역할은 무엇인가요?"
]

alist = [
    "해양환경공단은 대한민국의 해양 환경을 보호하고 개선하기 위해 다양한 활동을 하는 정부 기관입니다. 해양환경공단은 해양 오염 감시, 해양 생태계 보호, 해양환경 정책 개발, 오염 사고 대응 및 교육과 홍보 활동 등을 수행합니다.",
    "시민들은 해양환경공단의 다양한 캠페인에 참여할 수 있습니다. 예를 들어, 해변 청소 활동, 해양 환경 보호 교육 프로그램 참여, 플라스틱 사용 줄이기 등의 활동에 동참할 수 있습니다. 또한, 해양 오염에 대한 경각심을 가지고 환경을 보호하는 일상적인 습관을 실천하는 것도 중요한 참여입니다.",
    "해양환경공단은 해양 오염 상태를 지속적으로 모니터링하기 위해 수질 검사, 해양 생물 조사, 오염물질 배출량 측정 등을 진행합니다. 이를 바탕으로 오염 상황을 파악하고, 필요한 대책을 수립하여 실시간으로 대응합니다.",
    "해양환경공단은 해양 생태계 변화, 해양 오염 물질의 분포 및 영향, 해양 자원 관리 등에 대한 연구를 수행합니다.",
    "해양 오염 사고가 발생하면, 오염물질의 종류, 오염 범위 등을 파악하기 위한 실시간 모니터링을 실시합니다. 이후, 오일펜스, 오일 흡착재 등 다양한 장비를 동원하여 오염물질이 확산되는 것을 막고, 흡입 장비를 사용하여 오염물질을 회수하고, 회수된 오염물질은 안전한 방법으로 처리합니다.",
    "해양환경공단은 국제 해양 환경 관련 세미나, 회의, 워크숍에 참여하여 한국의 해양 환경 관리 경험과 기술을 공유합니다. 국제기구와 협력하여 해양 환경 보호를 위한 정책과 프로그램을 개발하고 지원합니다. 특히, 해양쓰레기 문제, 해양 생태계 보전 등 국제적으로 중요한 환경 이슈에 대해 다른 국가들과 협력합니다.",
    "첫 번째, 일회용 플라스틱 사용 줄이기, 두 번째, 해변 정화 활동 참여하기, 세 번째, 쓰레기 분리배출 철저히 하기, 네 번째, 교육 및 인식 증진이 있습니다.",
    "네. 해양환경공단은 '해양환경측정망'을 활용해 한국 연안의 해양환경 상태를 매년 정기적으로 조사하고 있어요. 해양환경 현황을 종합적으로 파악해 국가가 해양환경을 관리하고 보호하는 데 필요한 정책을 만드는 중요한 자료로 사용되고 있답니다.",
    "무게중심 반대쪽 다리를 빼내어 무릎을 꿇은 뒤 나머지 발도 빼내어 천천히 나와야 해요. 이탈이 어렵거나 고립된 경우, 신속히 구조 요청을 해야 합니다.",
    "해양환경공단은 유치원 및 초등학교를 대상으로 해양환경 이동교실을 운영하고 있어요. 전문 강사와 학습용 콘텐츠를 탑재한 차량이 방문해 체험 중심의 교육을 제공하고 있어요. 교육은 해양쓰레기, 해양기후변화 등 해양환경 현안에 대한 인식 증진 교육과 교육차량 내부 학습 콘텐츠 체험으로 구성되어요.",
    "해양환경공단에 대한 자세한 정보는 공식 웹사이트에서 확인할 수 있습니다. 또한, 해양환경 관련 교육이나 캠페인 일정도 홈페이지나 SNS 채널을 통해 알림을 받을 수 있습니다.",
    "지구 온난화는 지구의 평균 기온이 점차 상승하는 현상으로, 주로 대기 중 온실가스 농도가 증가하면서 발생합니다. 이로 인해 지구의 기후 패턴이 변화하고, 극단적인 날씨가 발생할 수 있어요.",
    "지구 온난화의 주요 원인은 온실가스의 증가입니다. 특히 이산화탄소, 메탄, 아산화질소 등 인간 활동으로 발생하는 온실가스가 대기 중에 축적되어 지구 온도를 상승시킵니다. 주된 원인으로는 산업 활동, 화석 연료 사용, 농업, 산림 파괴 등이 있습니다.",
    "지구 온난화는 기후 패턴에 심각한 영향을 미칩니다. 기온 상승으로 인해 폭염, 폭풍, 가뭄과 같은 극단적인 날씨가 증가하고, 해수면 상승이 발생합니다. 또한, 빙하가 녹고 생태계가 변화하는 등 자연 환경에도 큰 영향을 미칩니다.",
    "지구 온난화는 식량 생산, 물 부족, 기후 재해(홍수, 산불, 태풍 등)의 빈도와 강도를 증가시켜 인간 사회에 심각한 영향을 미칩니다. 또한, 열사병, 질병 전파 등과 같은 건강 문제와 경제적 피해도 커질 수 있습니다.",
    "지구 온난화로 인해 해양의 기온이 상승하고, 이로 인해 산호초 백화현상이나 해양 생태계 변화가 발생합니다. 또한, 해수면 상승은 저지대 국가와 섬나라에 심각한 위협을 주며, 해양 산성화는 수산물의 생산에 영향을 미칩니다.",
    "대중교통 이용, 에너지 절약, 플라스틱 사용 줄이기, 재활용을 실천하고, 지속 가능한 제품을 구매하는 등 일상에서 온실가스 배출을 줄이는 노력이 필요합니다.",
    "바다는 지구의 열을 약 90% 흡수하고, 온실가스로 인한 지구 온난화를 완화하며, 지구 산소의 70% 이상을 공급하고, 인간에게 단백질 공급원과 관광 자원을 제공합니다."
]

os.makedirs('mp3', exist_ok=True)
   
async def talk(string, filepath, actions):
    #speech.tts(string=string, filename=filepath, voice='gtts', lang='ko')
    device.eye_on(random.randint(100,255),random.randint(100,255),random.randint(100,255))
    if actions != None:
        motion_timer = Timer(0, motion.set_motion, args=(random.choice(actions),))
        motion_timer.start()
    audio.play(filepath, VOLUME, background=False)
    motion.set_motion('stop')
    device.eye_off()
    await asyncio.sleep(0.5)

app = FastAPI()

# HTML 템플릿을 위한 경로 설정
templates = Jinja2Templates(directory="templates")

# 메인 페이지 렌더링
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"theme":theme, "request": request, "qlist": qlist, "alist": alist, "initial_volume": VOLUME, "topic":topic}, )

# 버튼 클릭 시 호출되는 엔드포인트
class Question(BaseModel):
    index: int

class VolumeControl(BaseModel):
    volume: int

@app.post("/set_volume/")
async def set_volume(volume_control: VolumeControl):
    global VOLUME
    VOLUME = volume_control.volume
    print(f"Volume set to: {VOLUME}")  # 디버깅용 출력
    return {"message": f"Volume updated to {VOLUME}"}
    
@app.post("/get_answer/")
async def get_answer(question: Question):
    # talk 함수를 비동기 태스크로 실행하여 대기하지 않고 즉시 반환
    asyncio.create_task(talk(alist[question.index], f'mp3/answer_{question.index}.mp3', ["clapping1", "clapping2", "speak_r1","speak_r2", "speak_l1","speak_l2","hand1","hand2", "hand3","hand4"]))
    
    # 즉시 응답 반환
    return {"answer": alist[question.index]}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run('main:app', host='0.0.0.0', port=10001, access_log=False)
