# Binder IPC vs 파이프 vs 소켓

> Android가 Binder를 선택한 설계 철학

## 파이프 (Pipe)

```
프로세스 A  →→→→→→→→→→  프로세스 B
           단방향 스트림
```

- 단방향 — 양방향 통신하려면 파이프 두 개 필요
- 부모-자식 프로세스 간에만 사용 가능
- 스트림 기반이라 구조화된 메시지 전달 부적합
- 가장 원시적인 IPC

---

## 소켓 (Socket)

```
프로세스 A                    프로세스 B
   │                              │
send buffer  →→ 커널 →→  recv buffer
              (2회 복사)
```

- 양방향, 네트워크까지 확장 가능
- 커널을 두 번 거침 (send buffer → recv buffer) → 오버헤드
- 신원 확인 없음 — 앱 레벨에서 직접 구현해야 함

---

## Binder

```
프로세스 A                         프로세스 B
   │                                   │
   └──→  커널 mmap 공유 영역  ──→──────┘
              (1회 복사)
         + UID/PID 커널 보장
         + IBinder 객체 레퍼런스 전달
```

### Android가 Binder를 선택한 핵심 이유 3가지

**① 복사 횟수**
```
소켓   → 2회 복사 (send buffer → recv buffer)
Binder → 1회 복사 (mmap 기반 공유 메모리)
```

**② 신원 보장 (커널 레벨)**
```kotlin
val callingUid = Binder.getCallingUid()  // 위조 불가, 커널이 보장
val callingPid = Binder.getCallingPid()
if (callingUid != allowedUid) throw SecurityException("Unauthorized")
```

Android는 앱마다 신뢰 경계가 다른 구조 → "이 호출이 어떤 권한의 앱에서 왔는가"를 커널 레벨에서 보장해야 했음. 소켓으로는 불가능.

**③ 객체 전달**
```
소켓   → 바이트 스트림만 전달 가능
Binder → IBinder 레퍼런스 전달 가능 (원격 객체 메서드 호출처럼 사용)
```

---

## 한눈에 비교

| | 파이프 | 소켓 | Binder |
|---|---|---|---|
| 방향 | 단방향 | 양방향 | 양방향 |
| 복사 횟수 | 1회 | **2회** | **1회** |
| 신원 확인 | 없음 | 없음 | **커널 보장** |
| 객체 전달 | 불가 | 불가 | **IBinder 가능** |
| 사용 범위 | 부모-자식 | 네트워크까지 | Android 프로세스 간 |
| 보안 모델 | 없음 | 앱 레벨 | **커널 레벨** |

---

## 설계 철학

> 파이프는 단순 스트림,
> 소켓은 범용 통신,
> Binder는 **Android 보안 모델을 커널이 강제하는 구조화된 IPC**

## 관련 개념
- AIDL, HIDL → IDL 파일로 Binder 인터페이스 정의
- Android Treble — HAL을 별도 프로세스로 분리, Binder로 통신
- mmap, 공유 메모리

---
*2026-06-24*
