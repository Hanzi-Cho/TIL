# 커널 레벨 vs 앱 레벨 보안

> 어디가 더 좋은가 — 상황에 따라 다르고, 실제로는 두 레이어를 같이 쓴다

## 앱 레벨 보안

```
프로세스 A → 소켓 → 프로세스 B
                      │
                      ▼
                "uid가 맞나 확인" ← 앱 코드
```

보안 로직이 앱 코드 안에 있다.

**문제점:**
- 앱 크래시 시 보안 검사도 같이 죽음
- 앱 코드는 디컴파일/후킹 가능 (Frida 등)
- UID 스푸핑 — 소켓은 상대방이 누군지 커널이 보장 안 함
- 개발자가 실수로 검사 빠뜨리면 그냥 뚫림

---

## 커널 레벨 보안 (Binder)

```
프로세스 A → Binder 드라이버 → 프로세스 B
                  │
                  ▼
            UID/PID 자동 태깅 (앱 코드 개입 불가)
```

```kotlin
// 앱이 조작 불가, 커널이 보장
val callingUid = Binder.getCallingUid()
val callingPid = Binder.getCallingPid()
```

Binder 드라이버가 메시지에 발신자 UID/PID를 강제 태깅.  
루팅 없이는 위조 불가능.

---

## 어디가 더 좋은가

### 커널 레벨이 유리한 상황
- 신뢰 경계가 명확해야 할 때
- 시스템 서비스 ↔ 앱 통신
- 결제, 권한, 인증 관련
- "이 호출이 정말 해당 앱에서 왔는가" 보장 필요

### 앱 레벨로 충분한 상황
- 같은 신뢰 도메인 안에서 통신
- 내 서버 ↔ 내 앱 (TLS + JWT)
- 마이크로서비스 간 내부 통신
- 네트워크 경계가 이미 신뢰 보장

커널 레벨 보안을 모든 곳에 적용하면 오버엔지니어링.

---

## 실제 Android — 두 레이어를 같이 쓴다

```
레이어 1 — 커널 (Binder UID/PID):
"이 앱이 CAMERA 권한을 가진 앱인가" → 위조 불가

레이어 2 — 앱 (Permission Check):
"이 앱이 런타임에 카메라 권한을 허용받았는가" → 추가 검증
```

```kotlin
fun openCamera() {
    // 레이어 1: 커널이 보장한 UID
    val callingUid = Binder.getCallingUid()

    // 레이어 2: 앱 레벨 권한 확인
    if (checkPermission(CAMERA, callingUid) != PERMISSION_GRANTED) {
        throw SecurityException("No camera permission")
    }
}
```

---

## 비교표

| | 커널 레벨 | 앱 레벨 |
|---|---|---|
| 위조 가능성 | ✅ 불가 | ❌ 가능 (후킹) |
| 개발자 실수 | ✅ 여지 없음 | ❌ 취약 |
| 유연성 | ❌ 특수 인프라 필요 | ✅ 어디서나 구현 |
| 비즈니스 로직 결합 | ❌ 어려움 | ✅ 쉬움 |

## 핵심 인사이트

> 정답은 레이어를 나눠서 같이 쓰는 것.
> 커널이 신원을 보장하고, 앱이 비즈니스 권한을 검증.
>
> "커널이 무조건 좋다"가 아니라
> 신뢰 경계가 필요한 곳에 커널 레벨,
> 비즈니스 로직은 앱 레벨로 분리하는 것이 올바른 설계.

## 관련 개념
- Binder UID/PID 태깅
- Android Permission Model (install-time / runtime)
- SELinux (커널 레벨 MAC)
- Frida, 앱 후킹

---
*2026-06-24*
