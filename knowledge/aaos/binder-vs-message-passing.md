# Binder mmap vs 메시지패싱 (Go/Elixir) 설계 철학

> "Go/Elixir 채널이 더 현대적이고 Binder가 레거시처럼 느껴진다"는 직관에 대한 분석

## 비교 대상이 다른 레이어

Go/Elixir의 채널·메시지패싱과 Binder는 해결하려는 문제 자체가 다르다.

```
Go / Elixir 채널  → 동일 시스템 내 동시성 제어
Binder            → 프로세스 간 신뢰 경계 통신 + 보안
```

---

## 동시성 해결 철학 비교

### Go/Elixir — 메시지패싱

```
"공유 메모리 쓰지 마, 메시지로 통신해"
→ 같은 프로세스 안에서 race condition 원천 차단
→ 내부적으로는 큐 + 복사 구조
→ 소켓과 유사한 방향
```

### Binder — 프로세스 격리 + 커널 중재

```
"프로세스 자체를 분리해, 공유 메모리가 애초에 없어"
→ 프로세스 경계 = 격리
→ Android에서 앱 A가 앱 B 메모리를 건드리는 건 원천 불가
→ Binder는 그 경계를 넘을 때만 쓰는 통로
```

---

## Binder mmap이 위험한 공유 메모리가 아닌 이유

```
위험한 공유 메모리 (race condition 발생):
  스레드 A ─┐
            ├─→ 같은 변수를 동시에 읽고 씀
  스레드 B ─┘

Binder의 mmap (안전):
  프로세스 A → 데이터 씀
              (커널이 복사 완료 보장)
                              → 프로세스 B가 읽음
```

Binder mmap은 **단방향, 커널이 중재, 동시 접근 없음** → race condition 구조 자체가 아님.

---

## 진짜 트레이드오프

| | 메시지패싱 (Go/Elixir/소켓) | 공유 메모리 (mmap) | Binder |
|---|---|---|---|
| race condition | ✅ 원천 차단 | ❌ 개발자 책임 | ✅ 커널 중재 |
| 복사 오버헤드 | ❌ 있음 | ✅ 없음 | ✅ 1회만 |
| 보안 (신원 확인) | ❌ 없음 | ❌ 없음 | ✅ UID/PID 커널 보장 |
| 설계 명확성 | ✅ 높음 | ❌ 낮음 | 중간 |

Binder는 mmap으로 속도를 얻되, 커널이 접근을 중재해서 race condition을 막는 절충안.

---

## 핵심 인사이트

> Go/Elixir는 "복사해서 안전하게"
> Binder는 "커널이 중재해서 안전하게 + 빠르게"
>
> Go/Elixir가 더 현대적인 건 맞다.
> 다만 Binder는 OS 보안 모델과 성능을 동시에 잡아야 하는
> Android의 제약 안에서 나온 설계라 단순히 레거시로 보기 어렵다.
>
> 해결하는 문제의 레이어가 다르다.

## 관련 개념
- Go channel, Elixir GenServer
- mmap, 공유 메모리 (POSIX SHM)
- Android Binder 트랜잭션, Parcel
- race condition, mutex, lock-free

---
*2026-06-24*
