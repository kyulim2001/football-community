# Football Community

해외 축구 리그별 게시판과 실시간 채팅을 제공하는 커뮤니티 웹 서비스입니다.

## 기술 스택

| 영역 | 기술 |
|---|---|
| Frontend | React 18, Recoil, React Router, SCSS |
| Backend | Django 5.2, Django REST Framework, SimpleJWT, Django Channels (WebSocket) |
| Database / Cache | MySQL 8.0, Redis 7 (Channels layer) |
| Infra | Docker, Docker Compose, Nginx (reverse proxy), Daphne (ASGI) |

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

## 디렉터리 구조

```
.
├── backend/            Django 프로젝트 (config, accounts, posts, chat, notifications, report)
│   ├── Dockerfile
│   └── entrypoint.sh   migrate, collectstatic 후 Daphne 실행
├── frontend/           React 프로젝트
│   ├── Dockerfile      Node로 빌드 후 Nginx 이미지에 결과물 복사 (multi-stage)
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```

## 주요 기능

- 리그별 게시판 (프리미어리그, 라리가, 분데스리가, 세리에A)
- 게시글, 댓글, 대댓글, 좋아요, 이미지·영상 첨부
- JWT 로그인, 이메일 인증 회원가입, 아이디·비밀번호 찾기
- WebSocket 실시간 채팅
- 알림, 신고, 사용자 차단
