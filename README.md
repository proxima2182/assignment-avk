
### 구현내용
간단한 CRUD를 실행하는 API 서버 어플리케이션을 Docker로 DB와 함께 실행할 수 있도록 구현

---
### 어플리케이션 실행
* 프로젝트 폴더에서 터미널 이용하여 docker 빌드 및 실행
```
docker-compose build
docker-compose up -d
```
* ocalhost의 7000 포트에서 어플리케이션 실행됨
* swagger 문서 접근 URL
  * http://localhost:7000/api-docs
---
### 테스트 파일 실행
* 프로젝트 폴더에서 터미널을 이용하여 테스트 파일 실행가능
```
python3 tests/test_fine.py
```
* ModuleNotFoundError: No module named 'requests' 에러가 뜨는 경우 'requests' 모듈 설치 필요
  * pip3 install requests