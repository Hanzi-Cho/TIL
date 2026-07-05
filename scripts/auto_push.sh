#!/bin/bash

# auto_push.sh
# 매일 작성한 TIL 문서를 자동으로 Git Commit & Push 하는 스크립트

# 1. 환경 변수 로드 (크론탭 세션에서는 일반 터미널 환경변수가 누락되므로 SSH/Git 실행에 필요한 경로 지정)
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export LANG=ko_KR.UTF-8

# 2. TIL 프로젝트 경로 설정
TIL_DIR="/home/hanzicho/workspace/til"
cd "$TIL_DIR" || exit 1

# 3. 변경 사항이 있는지 확인
if [ -z "$(git status --porcelain)" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - No changes to commit."
    exit 0
fi

# 4. 현재 날짜 구하기
TODAY=$(date "+%Y-%m-%d")

# 5. Git 작업 수행
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting auto push..."
git add .

# 로컬 커밋 수행
git commit -m "${TODAY} daily commit"

# 6. Git Push 실행
# 크론탭 환경에서 SSH 키 권한이나 인증 헬퍼 연동을 위해 필요한 경우 대비
# (사용자가 패스워드 없이 SSH 키 또는 Credential Helper를 사용 중이어야 정상 동작합니다.)
git push origin main >> auto_push.log 2>&1

if [ $? -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Successfully pushed changes."
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to push changes. Check SSH/Git credentials."
    exit 1
fi
