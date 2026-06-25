# ViewModel 생명주기 범위

> 싱글 액티비티 멀티 프래그먼트 구조에서 ViewModel 범위를 잘못 잡으면 생기는 문제

## 핵심 요약

| 선언 방식 | 생명주기 범위 | 사용 시점 |
|---|---|---|
| `viewModels()` | Fragment 자신 | Fragment 단독 상태 |
| `activityViewModels()` | Activity 전체 | 앱 전역 공유 데이터 |
| `navGraphViewModels(R.id.xxx)` | Navigation Graph | 플로우 단위 공유 데이터 |

---

## 문제 상황

```
Activity (살아있음)
├── Fragment A (pop되어 사라짐)
├── Fragment B (현재 화면)
└── SharedViewModel (Activity에 묶임 → 여전히 살아있음)
```

`activityViewModels()`로 만든 ViewModel은 **Activity가 살아있는 한 메모리에 유지**.  
Fragment가 backstack에서 pop되어도 ViewModel은 소멸되지 않는다.

```kotlin
// Fragment A에서
val viewModel: OrderViewModel by activityViewModels()

// Fragment A가 pop되어도 OrderViewModel은 살아있음
// → Fragment B에서 같은 ViewModel 접근 시 오염된 상태를 볼 수 있음
```

---

## 해결 방법

### ① navGraphViewModels() — 가장 권장

```kotlin
// Fragment A, B가 같은 nav graph 안에 있을 때
val viewModel: CheckoutViewModel by navGraphViewModels(R.id.checkout_graph)
// checkout_graph 플로우를 벗어나면 자동 소멸
```

플로우(체크아웃, 온보딩 등) 단위로 생명주기를 묶는 패턴.  
Activity 전체가 아닌 **의미 단위로 범위를 최소화**하는 것이 핵심.

### ② 명시적 초기화

```kotlin
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    viewModel.reset() // Fragment 진입 시점에 상태 클리어
}
```

임시방편. 근본적인 해결은 아님.

### ③ activityViewModels() 남용하지 않기

진짜로 Activity 전체 생명주기가 필요한 데이터(로그인 상태, 유저 세션 등)에만 한정.

---

## 핵심 인사이트

> Context/ViewModel 선택 문제는 결국
> **생명주기 범위를 얼마나 정밀하게 제어하느냐**의 문제다.
>
> 싱글 액티비티 구조에서 Activity Context를 남용하면
> 메모리 누수와 상태 오염이 발생한다.

## 관련 개념
- Navigation Graph, BackStack
- ViewModel Factory, SavedStateHandle
- Fragment lifecycle vs View lifecycle

---
*2026-06-24*
