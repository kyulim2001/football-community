# Football Community

배포 주소: http://3.36.130.77

해외 축구 리그별 게시판과 실시간 채팅을 제공하는 커뮤니티 웹 서비스입니다.

## 기술 스택

| 영역 | 기술 |
|---|---|
| Frontend | React 18, Recoil, React Router, SCSS |
| Backend | Django 5.2, Django REST Framework, SimpleJWT, Django Channels (WebSocket) |
| Database / Cache | MySQL 8.0, Redis 7 (Channels layer) |
| Infra | Docker, Docker Compose, Nginx (reverse proxy), Daphne (ASGI), AWS EC2 (Ubuntu 24.04) |
| Orchestration | k3s (Kubernetes), Traefik Ingress |
| Monitoring | Prometheus, Grafana, node_exporter, cAdvisor |

## 아키텍처

```
Browser
   │  :80
   ▼
Nginx (web) ── React 정적 파일 제공
   ├── /api/, /admin/, /chat/messages/ ──► Daphne + Django (backend:8000)
   ├── /ws/                              ──► WebSocket 업그레이드 후 backend로 전달
   ├── /django-static/                    ──► collectstatic 결과 (공유 볼륨)
   └── /media/                            ──► 업로드 파일 (공유 볼륨)

backend ──► MySQL (db:3306, 외부 포트 미노출)
        └─► Redis (redis:6379, 외부 포트 미노출)
```

DB와 Redis는 외부에 포트를 열지 않고 Docker 내부 네트워크에서만 접근합니다.

## 실행 방법

```bash
cp .env.example .env
docker compose up -d --build
```

`.env`의 `DJANGO_SECRET_KEY`, `DB_PASSWORD`, `DB_ROOT_PASSWORD`는 반드시 새 값으로 바꿔야 합니다.
브라우저에서 `http://localhost`로 접속합니다.

## 모니터링

`monitoring/`에 애플리케이션과 독립된 모니터링 스택이 있습니다.

```bash
cd monitoring
cp .env.example .env
docker compose up -d
```

- node_exporter: 서버 CPU, 메모리, 디스크, 네트워크 지표 수집
- cAdvisor: 컨테이너별 CPU, 메모리 지표 수집
- Prometheus: 지표 저장과 알람 규칙 평가 (대상 다운, CPU 80%, 메모리 85%, swap 50%, 디스크 80%)
- Grafana: 대시보드 자동 프로비저닝

Prometheus(9090)와 Grafana(3000)는 서버의 127.0.0.1에만 바인딩되어 외부에 노출되지 않으며, SSH 터널로 접속합니다.

```bash
ssh -i key.pem -L 3000:localhost:3000 -L 9090:localhost:9090 ubuntu@<서버 IP>
```

## Kubernetes (k3s)

`k8s/`의 매니페스트로 같은 서비스를 k3s 위에서 실행할 수 있습니다.

| 리소스 | 내용 |
|---|---|
| StatefulSet `db` | MySQL 8.0, PVC로 데이터 유지 |
| Deployment `redis`, `backend`, `web` | 각각 Service로 연결, backend는 initContainer로 DB·Redis 준비 대기 |
| PVC `static-data`, `media-data` | backend와 web(Nginx)이 공유 |
| Ingress | Traefik이 80 포트로 받아 `web`으로 전달 |
| Secret `app-env` | `.env`에서 생성, Git에 포함되지 않음 |

```bash
./k8s/deploy.sh
```

이미지를 서버에서 빌드한 뒤 k3s(containerd)로 가져오고, Secret 생성과 매니페스트 적용, 롤아웃 확인까지 수행합니다.

## 디렉터리 구조

```
.
├── backend/            Django 프로젝트 (config, accounts, posts, chat, notifications, report)
│   ├── Dockerfile
│   └── entrypoint.sh   migrate, collectstatic 후 Daphne 실행
├── frontend/           React 프로젝트
│   ├── Dockerfile      Node로 빌드 후 Nginx 이미지에 결과물 복사 (multi-stage)
│   └── nginx.conf
├── monitoring/         Prometheus, Grafana, node_exporter, cAdvisor
├── k8s/                k3s 매니페스트와 배포 스크립트
├── docker-compose.yml
└── .env.example
```

## 주요 기능

- 리그별 게시판 (프리미어리그, 라리가, 분데스리가, 세리에A)
- 게시글, 댓글, 대댓글, 좋아요, 이미지·영상 첨부
- JWT 로그인, 이메일 인증 회원가입, 아이디·비밀번호 찾기
- WebSocket 실시간 채팅
- 알림, 신고, 사용자 차단
