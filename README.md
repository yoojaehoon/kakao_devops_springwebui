# 웹서버를 도커로 CI 구축 및 무중단 배포하기 (Jenkins + Slack + Gradle + Docker)

### 스프링부트 프로젝트 생성

springboot_webui를 clone 받아주세요.
https://github.com/yoojaehoon/kakao_devops_springwebui.git

빌드 테스트는 springboot-web-ui를 소스코드로 사용했습니다.
빌드도구는 ```Gradle```을 사용합니다.  
본인의 서버에서 Gradle을 다운로드 받으시고 (https://gradle.org/install/) 프로젝트를 생성 해주세요.
Task 실행 테스트를 위해 간단한 Task만 ```build.gradle```에 추가하겠습니다.
저는 빌드후 print와 jar를 넣어주는 plant_jar를 추가했습니다.

```./gradlew build plang_jar``` 를 실행해 주세요
![build.gradle](./images/buid.gradle.png)

### 도커 인스톨
컨테이너 기반의 웹서버를 돌리기 위해 docker 엔진을 설치합니다.

```
# 의존성 설치
$ sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# yum config manager를 통한 docker engine repo 추가
$ sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# yum 패키지 색인
$ sudo yum makecache fast

# docker engine community edition 설치
$ sudo yum -y install docker-ce

# docker engine 시작
$ sudo systemctl start docker
```

### 도커 컴포즈 설치
```
curl -L https://github.com/docker/compose/releases/download/버전/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
(버전은 https://github.com/docker/compose/releases 여기에서 참고하였습니다. 본 문서는 1.24.0-rc1 버전을 사용하였습니다)
sudo chmod +x /usr/local/bin/docker-compose
```

### jenkins 설치
빌드후 배포할수 있도록 jenkins를 설치후 git과 연동할 것이다.
이를 위해 물리호스트에 설치할수도 있지만 docker는 한줄이면 jenkins_ci를 사용할수 있다.
https://github.com/jenkinsci/docker 에서 제공하는 이미지를 사용하면 한줄이면 올릴수 있다

```
docker run -d -v jenkins_home:/var/jenkins_home -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts
```
jenkins의 볼륨을 로컬과 연결해야 데이터가 사라지지 않으니 -v jenkins_home:/var/jenkins_home은 맞춰주도록 하자

![jenkins_1](./images/jenkins_1)
패스워드는 docker 안에 들어있다.
```docker exec -i -t jenkins /bin/bash
cat /var/jenkins_home/secrets/initialAdminPassword
```
콘솔에서 한번 패스워드를 넣어주고 설정하게 되면 파일은 사라지므로 일부러 삭제하지 않아도 된다

![jenkins_2](./images/jenkins_2)
필자는 install suggested plugins를 선택했다. git 플러그인이 포함되서 따로 수동설치 안해도 된다.

![jenkins_3](./images/jenkins_3)
FreeStyle Project를 선택하고 프로젝트이름 "springboot_project (마음대로 지정해줘도 된다)"를 넣어준다

![jenkins_4](./images/jenkins_4)
Items 설정화면에서 ```소스 코드 관리``` 메뉴의 Repository URL에 git 저장소를 등록해준다
아래 Credential 항목에 유저를 등록해준다. github에서 사용하는 계정과 패스워드를 넣어준다

branch는 관리할 브랜치선택을 하는건데 master로 선택했다. 브랜치를 선택한것에 따라 빌드가 유발된다
빌드 유발은 체크박스 ```GitHub hook trigger for GITScm polling``` 를 선택한다
![jenkins_5](./images/jenkins_5)

![jenkins_6](./images/jenkins_6)
Add build step에서 빌드하는 스크립트를 넣을수 있도록 선택해준다. git에서는 gradle build가 필요 없다고 생각했다. gradle clean를 넣는다

## Github과 jenkin 연동하기
빌드할때 성공했는지 실패했는지 메시지 받을수 있도록 을 연결한다. 옛날에는 Integrations & services에서 지원되었는데 어느순간 Webhooks로 옮겨갔다

![jenkins_7](./images/jenkins_7)
만들어져있는 jenkins url 웹훅 주소를 넣으면 이제부터 git이 push할때마다 빌드를 알아서 하게 될것이다


