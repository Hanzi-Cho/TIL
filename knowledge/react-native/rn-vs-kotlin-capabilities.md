# React Native — 할 수 있는 것 vs 없는 것 (Kotlin 비교)

> RN의 한계가 정확히 "플랫폼 레이어"의 경계와 일치한다

## RN이 할 수 있는 것

- UI 렌더링 / 상태관리 (useState, Redux, Zustand)
- 네트워크 요청 (fetch, axios)
- 간단한 로컬 저장 (AsyncStorage, MMKV)
- 화면 전환 / 딥링크 (React Navigation)
- AppState 감지 (포그라운드/백그라운드 전환)

---

## RN이 할 수 없는 것 — Kotlin 비교

### 1. 백그라운드 장시간 작업

```javascript
// RN — 백그라운드 진입 시 JS 엔진 정지, 작업 중단
AppState.addEventListener('change', (state) => {
    if (state === 'background') {
        startLongTask(); // 언제 멈출지 보장 없음
    }
});
```

```kotlin
// Kotlin — Service로 백그라운드 실행 보장
class SyncService : Service() {
    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        CoroutineScope(Dispatchers.IO).launch {
            while (true) {
                syncData()
                delay(30_000)
            }
        }
        return START_STICKY // 시스템이 죽여도 재시작
    }
}
```

### 2. Foreground Service + 알림 세밀 제어

```javascript
// RN — 라이브러리 경유 필요 (내부적으로 Kotlin 호출)
import ForegroundService from 'react-native-foreground-service';
await ForegroundService.start({ id: 1, title: '동기화 중' });
```

```kotlin
// Kotlin — 직접 완전한 제어
class MusicService : Service() {
    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("재생 중")
            .setSmallIcon(R.drawable.ic_music)
            .addAction(R.drawable.ic_pause, "일시정지", pausePendingIntent)
            .setStyle(MediaStyle().setMediaSession(mediaSession.sessionToken))
            .build()
        startForeground(1, notification)
        return START_NOT_STICKY
    }
}
```

### 3. 메모리 단계별 대응

```javascript
// RN — 백그라운드 진입만 감지, 레벨 구분 불가
AppState.addEventListener('change', (state) => {
    if (state === 'background') {
        cache.clear(); // 무조건 전체 클리어
    }
});
```

```kotlin
// Kotlin — 압박 수준별 단계적 대응
override fun onTrimMemory(level: Int) {
    when (level) {
        TRIM_MEMORY_RUNNING_MODERATE -> {
            thumbnailCache.trimToSize(thumbnailCache.size() / 2)
        }
        TRIM_MEMORY_RUNNING_CRITICAL -> {
            thumbnailCache.evictAll()
        }
        TRIM_MEMORY_UI_HIDDEN -> {
            fullImageCache.evictAll()
            releaseMediaPlayer()
        }
    }
}
```

### 4. 시스템 서비스 직접 접근

```javascript
// RN — 네이티브 모듈 없이 불가
```

```kotlin
// Kotlin — getSystemService로 직접 접근
val batteryManager = getSystemService(BATTERY_SERVICE) as BatteryManager
val level = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)

val sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_GAME)
```

### 5. ViewModel 생명주기 자동 관리

```javascript
// RN — 화면 이탈 시 상태 소멸, 직접 영속화 필요
const [orderData, setOrderData] = useState(null);
useEffect(() => {
    return () => {
        AsyncStorage.setItem('orderData', JSON.stringify(orderData));
    };
}, [orderData]);
```

```kotlin
// Kotlin — 플랫폼이 자동으로 생명주기 관리
class OrderViewModel : ViewModel() {
    val orderData = MutableStateFlow<Order?>(null)
    // 화면 회전, 백스택에서 자동 유지
    // onCleared()는 완전히 종료될 때만 호출
}
val viewModel: OrderViewModel by viewModels()
```

---

## 한눈에 비교

| 기능 | RN | Kotlin |
|---|---|---|
| UI / 상태관리 | ✅ 완전 가능 | ✅ |
| 네트워크 요청 | ✅ 완전 가능 | ✅ |
| 백그라운드 장시간 작업 | ❌ JS 엔진 정지 | ✅ Service |
| Foreground Service 세밀 제어 | ❌ 라이브러리 경유 | ✅ 직접 |
| 메모리 단계별 대응 | ❌ 레벨 구분 불가 | ✅ onTrimMemory |
| 시스템 서비스 직접 접근 | ❌ 네이티브 모듈 필요 | ✅ getSystemService |
| ViewModel 자동 생명주기 | ❌ 직접 설계 | ✅ 플랫폼 제공 |
| Binder IPC | ❌ | ✅ AIDL |

---

## 핵심 인사이트

> RN의 한계에 부딪히는 지점이 정확히 "플랫폼 레이어"다.
> 그 경계를 아는 개발자가 네이티브 모듈 설계도 올바르게 할 수 있다.
>
> RN 라이브러리들은 대부분 이 한계를 네이티브 코드로 우회하는 래퍼다.
> 라이브러리가 없거나 커스터마이징이 필요하면 결국 Kotlin/Java를 알아야 한다.

## 관련 개념
- NativeModule, TurboModule
- Headless JS Task
- START_STICKY vs START_NOT_STICKY
- LMK, onTrimMemory

---
*2026-06-24*
