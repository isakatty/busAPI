# busAPI
---

## 작업 사유

버스정류장을 검색했을때 View에 보여질 데이터는 3가지가 필요하다.
| view | 필요한 데이터 |
| -- | -- |
|<img width="294" alt="스크린샷 2024-03-02 오후 7 04 28" src="https://github.com/isakatty/busAPI/assets/133845468/90fff4bf-1b0a-4436-8bf6-962fd6d191f7"> | 1. 버스정류장 이름 <br> 2. 버스정류장 번호 <br> 3. 다음 정류장 - 방면 |

하지만 가지고 있던 버스정류장에 대한 **json 파일에는 다음 정류장에 대한 정보가 없고**, 그렇다고 **API통신**을 하여 값을 가져와서 넣어주기엔 **일일 api 통신 트래픽이 한정적**이다. ( 일일 트래픽 1000회 )

그렇다면 다음 정류장에 대한 데이터를 받을 수 있는 api를 선택하고 정류장 넘버를 넣어 다음 정거장 이름 값을 추출하는게 좋겠다고 생각이 들었다. ( 그리고 다음 정거장 데이터까지 있는 json 파일을 구하려고 해봤지만 못찾았다. )

팀에서 선택한 api로는 내 뷰에서 사용될 다음 정류장에 대한 값도 없었기 때문에 여러 공공 api를 찾다가 **다음 정류장 값을 주는 api**를 찾았다.

| [nxtStn값을 주는 api](https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15000303) |
| --- |
| ![스크린샷 2024-03-02 오후 7 37 29](https://github.com/isakatty/busAPI/assets/133845468/b48c57dc-7c05-4010-b04e-9d462ff8145c) |


## 작업 내용

1. json을 읽어서 ['DATA']를 반복문을 타면서 stop_no를 뽑아내기
2. api 통신하는 함수 만들기
    1. api 통신 필수 파라미터인 arsId에 stop_no 넣어주기
    2. 통신 결과 데이터 형태는 xml이고 xml을 문자열로 변경하여 트리구조로 변경
    3. ElementTree의 find() 매서드를 통해 msgHeader와 itemList가 있는지 확인하고, 있을 경우 모든 itemList를 추출
    4. 추출한 itemList를 반복문을 통해 nxtStn값이 있으면 반환
    5. 기타 예외 처리 - 파싱에러, msgHeader, itemList 유무, itemList의 nxtStn에 값 유무에 대한
3. stop_no를 api 통신 함수의 input 인자로 넣어 json 파일에 stop_no와 nxtStn를 각 요소는 딕셔너리로, 리스트로 만들어 새 json 파일에 추가하고 저장함.


<img width="979" alt="스크린샷 2024-03-02 오후 7 43 18" src="https://github.com/isakatty/busAPI/assets/133845468/ad8022ae-ea8c-4c6d-a368-d6401ca5008a">

## 트러블 슈팅

### 아이디어 : **itemList의 0번째 배열에 접근, dictionary의 key를 통해 value 값을 추출** 

처음엔 nxtStn 값을 잘 배출하더니 특정 값들에서 **0번째 배열을 찾을 수 없다**는 에러를 보내면서 함수 동작을 멈췄고, 예외처리를 해주고 다시 돌려봐도 이상하게 0번 배열의 값을 가져올 수 없는 것들이 너무 많이 나왔다.

#### Error [0] 접근 불가 - itemList의 item의 type 확인
postman으로 0번 배열을 찾을 수 없었던 stop_no를 넣어서 통신 결과를 확인했지만 itemList가 있었다. 

근데 왜 0번 배열에 접근할 수 없었을까.

한참을 검색도 해보고 first()이런 매소드가 있나 찾아봤지만 어디에도 해결할 방법을 못찾던 와중에, **프린트문으로 타입을 찍어봐야겠다는 생각**이 들었다.

![스크린샷 2024-03-02 오후 8 27 53](https://github.com/isakatty/busAPI/assets/133845468/8ff2ce0b-da25-458e-b936-7b102caab0be)

그 결과, 0번 배열을 찾을 수 없다는 에러를 보냈던 문제의 stop_no들은 for문을 통해 돌린 itemList의 item은 dictionary type이 아닌 **str type**이었던 것이었다.

에러를 보냈던 stop_no들을 메모해놨고 5개 정도 postman으로 쏴본 결과 itemList가 1개였다. 짐작하는거지만, itemList가 1개인 것들은 str인게 아닌가.. ! .. 확실하지 않다.

그래서 dictionary 일때랑 str일때, 그 외 이렇게 예외처리해서 nxtStn 값을 가져오려고 했는데, str일때 nxtStn 값을 어떻게 가져와야할지 모르겠어서 다시 구글링을 해보았다.

#### Solve - xml.etree.ElementTree 모듈 사용 '전체를 str으로'
그랬더니, xml.etree.ElementTree 모듈을 사용해서 전체 파싱한 결과를 str로 변경하고, 트리구조로 변경해서 find()와 findall() 매소들를 통해 원하는 값을 추출하면 된다는 것을 확인했다.
dictionary랑 str일때를 나눠서 값을 빼오는 것보다 차라리 전체를 str로 두고 원하는 값을 가져오는게 훨씬 효율적일 것 같아서 빠르게 적용해보기로 했다.

###그 결과는 성공 - 현재 코드 : [링크](https://github.com/isakatty/busAPI/blob/main/newCode.py)



## 결과물

그 결과, 그렇게 바라고 바라던 nxtStn 값을 추출할 수 있었다.
하지만 일일 트래픽량이 1000이기 때문에 1만개가 넘는 데이터를 전체 가져오기엔 3일정도 더 걸릴 것 같다 😂 ..

이렇게 데이터를 뽑아낸거는 좋은거같진 않다. 이렇게 데이터를 뽑아내면 stationList.json (위의 json 캡쳐본)에 넣어주기 위해서 이리저리 또 가공 후 사용해야하기 때문에 번거롭다.
( 사실 이렇게 받은 json 파일을 excel로 변환하고, 하나로 만들 json 파일도 excel로 변환해서 stop_no에 맞춰 값을 넣어주고 있기 때문에.. 굉장히 어렵게 일을 하고 있다는 생각이 들긴 하다. )

그리고 stationList가 업데이트될때를 대비해야하는데, 이때 이런 과정을 다시 해야한다고 생각하면 이 방법이 지금 현재 어떻게 값을 가져다 쓰기 위한 일시적인 방법일뿐이지 않나..싶다.

좋은 방법이 있으시다면 myuniverse8@naver.com으로 연락주시면 정말 감사할 것 같습니다. 

<img width="712" alt="스크린샷 2024-03-02 오후 8 53 59" src="https://github.com/isakatty/busAPI/assets/133845468/483ca6b3-930c-43c3-a889-b830657e72dd">


#### 소감
ㅎㅎ.. python 어렵다 .. ㅎㅎ.. xcode만 쓰다가 vsCode + vbenv? 가상환경 + python 등 막막함이 너무 앞섰다.
python 자체가 어려웠다기 보다는 알지 모르는 모듈을 가져다 쓰려니 내가 원하는 작동을 하는 모듈이 맞는지 찾는것에 시간이 좀 많이 걸렸던게 어려웠다.

총 걸린 시간은 4일정도..? index error를 해결하는데에 시간을 꽤나 보냈지만 뿌듯하다.. 남들은 엥? 너무 쉬운거 아냐?!라고 할수도 있지만 파이썬을 모르는 내 입장에서는 선방했다. 프로젝트 끝날때까지 가져가는걸로 팀원들이랑 이야기 했는데 그 다음날 바로 해결 완!