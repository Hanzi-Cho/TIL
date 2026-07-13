# React Native (Bridge/JSI) vs Flutter (Platform Channels) 아키텍처 비교

이 문서는 React Native(RN)와 Flutter 두 크로스 플랫폼 프레임워크가 네이티브 영역(Android/iOS)과 통신하는 메커니즘을 비교하고, 각 프레임워크가 기존의 '비동기 브릿지 병목 현상'을 서로 다른 설계 철학으로 해결한 방법과 그로 인해 발생하는 성능/구동 트레이드오프를 정리합니다.

---

## 1. React Native의 통신 아키텍처 (Bridge ➔ JSI)

### A. RN Bridge 아키텍처 (구 아키텍처)
- **비동기 메시지 패싱**: JS와 네이티브 간의 호출은 동기식(Sync)으로 실행되지 못하고, 전송될 메시지들이 비동기 큐에 쌓여 일괄 처리(Batching)되는 방식으로 동작합니다.
- **JSON 직렬화**: 두 런타임 간의 메모리가 격리되어 있어, 자바스크립트 객체를 JSON 문자열로 변환(직렬화)하여 브릿지로 넘기고, 수신부에서 이를 다시 파싱(역직렬화)해야 하므로 대량 데이터 전송 시 병목이 유발됩니다.

### B. JSI (JavaScript Interface) 아키텍처 (신 아키텍처)
- **메모리 직접 공유 (C++ Host Object)**: 자바스크립트 엔진(Hermes)이 네이티브 측의 C++로 작성된 객체를 직접 참조할 수 있어, JS에서 네이티브 메서드를 동기(Synchronous)로 즉시 호출할 수 있습니다.
- **직렬화 오버헤드 제거**: JSON 변환 과정 없이 메모리 주소를 포인터로 접근하여 초고속 통신이 가능하며, 이는 TurboModules와 Fabric의 기반이 됩니다.

---

## 2. Flutter의 네이티브 통신 아키텍처: 플랫폼 채널 (Platform Channels)

Flutter 역시 카메라, 블루투스, 배터리 등 OS 고유 기능이나 네이티브 라이브러리를 제어해야 할 때는 안드로이드(Kotlin/Java) 및 iOS(Swift/ObjC) 레이어에서 플랫폼 코드를 직접 작성해야 합니다. 이를 위해 **플랫폼 채널(Platform Channels)**이라는 메시지 패싱 메커니즘을 사용합니다.

```
+--------------------------------------------------------------+
| [ Flutter (Dart) ]                                           |
|   | (Map, List, String 등)                                   |
|   v                                                          |
| [ BinaryMessenger (바이너리 직렬화) ]                           |
|   |                                                          |
|   +=======> [ 플랫폼 채널 (Platform Channels) ] =======+     |
|                                                       |      |
| [ MethodChannel Handler (코틀린/스위프트) ] <==========+      |
|   | (자동 매핑: HashMap, ArrayList, String 등)               |
|   v                                                          |
| [ Android/iOS Native ]                                       |
+--------------------------------------------------------------+
```

### A. 주요 플랫폼 채널 종류
1. **`MethodChannel`**: Dart에서 네이티브의 특정 메서드를 호출하고, 그 결과를 비동기(`Future`)로 전달받는 가장 일반적인 방식입니다. (RN의 NativeModules 호출과 유사)
2. **`EventChannel`**: 네이티브에서 Dart 레이어로 센서 데이터, 위치 변화 등 지속적인 데이터 스트림을 전송할 때 사용합니다.

### B. 플랫폼 채널 코드 예시

#### Dart (Flutter) 측 호출 코드
```dart
import 'package:flutter/services.dart';

class NativeBridge {
  // 채널 식별자 정의 (도메인 형태로 고유하게 설정)
  static const platform = MethodChannel('com.example.app/battery');

  Future<int> getBatteryLevel() async {
    try {
      // 네이티브의 'getBatteryLevel' 이라는 메서드를 호출
      final int result = await platform.invokeMethod('getBatteryLevel');
      return result;
    } on PlatformException catch (e) {
      print("Failed to get battery level: '${e.message}'.");
      return -1;
    }
  }
}
```

#### Kotlin (Android) 측 수신 코드
```kotlin
package com.example.app

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.example.app/battery"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        // 채널을 등록하고 핸들러 설정
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            if (call.method == "getBatteryLevel") {
                val batteryLevel = getBatteryLevel() // 실제 코틀린 구현 메서드
                
                if (batteryLevel != -1) {
                    result.success(batteryLevel) // Dart로 성공 결과 반환
                } else {
                    result.error("UNAVAILABLE", "Battery level not available.", null)
                }
            } else {
                result.notImplemented()
            }
        }
    }

    private fun getBatteryLevel(): Int {
        // 안드로이드 OS 고유의 배터리 잔량 조회 로직
        return 85
    }
}
```

### C. 데이터 직렬화 및 타입 안전성: Pigeon
- **자동 바이너리 직렬화**: 플랫폼 채널을 통과하는 데이터는 자동으로 표준 코덱을 통해 바이너리 형태로 직렬화되어 전송되며, Dart의 Map/List/String/int 등은 코틀린의 HashMap/ArrayList/String/Int 등으로 매핑됩니다.
- **Pigeon (타입 안전한 코드 생성)**: MethodChannel의 문자열 기반 호출("getBatteryLevel")은 오타나 타입 불일치로 인한 런타임 에러(Type-unsafe) 위험이 존재합니다. Flutter는 **Pigeon**이라는 공식 코드 생성 툴을 통해 Dart 인터페이스 명세를 작성한 뒤, 호출부(Dart)와 수신부(Kotlin/Swift)의 프로토콜 코드를 자동으로 생성하여 완전한 **타입 안전성(Type Safety)**을 확보합니다.

---

## 3. 병목 해소 전략의 아키텍처적 차이점

두 프레임워크 모두 크로스 플랫폼의 최대 단점인 '기존 JS 브릿지 병목 현상'을 해결했지만, 접근하는 기술적 방향은 완전히 다릅니다.

```
* React Native (JSI) : "통로의 혁신" ➔ 통신 통로를 아예 헐고, 메모리 직접 참조 직통 터널 구축
* Flutter            : "통신의 제거" ➔ UI는 자체 엔진으로 직접 그리고, 채널은 데이터 셔틀로만 제한
```

### A. React Native (JSI) ➔ "통신 파이프라인의 초고속화"
- RN은 여전히 OS 표준 네이티브 컴포넌트(OEM Widgets)를 화면에 렌더링해야 하는 숙명을 갖습니다.
- 따라서 UI를 조작하기 위한 잦은 소통이 필요하며, JSI를 통해 자바스크립트 엔진과 C++ 레이어 간의 메모리를 공유함으로써 통신 속도 자체를 물리적으로 최적화했습니다.

### B. Flutter ➔ "UI 관련 통신 필요성 자체를 원천 제거"
- Flutter는 네이티브 UI 시스템(View/UIKit)을 쓰지 않고, C++ 기반의 자체 그래픽 엔진(Impeller 또는 Skia)을 앱에 내장하여 화면에 직접 픽셀을 그립니다.
- UI 렌더링 명령이 네이티브 브릿지를 건널 필요가 없어 **UI 렌더링에 관한 한 통신 비용이 0%**입니다.
- 플랫폼 채널은 오직 하드웨어/OS API 제어 시에만 사용되므로 통신 빈도 자체가 낮아 메시지 패싱 구조임에도 병목 현상이 발생하지 않습니다.

---

## 4. 아키텍처에 따른 트레이드오프 (근본적 단점 비교)

두 프레임워크의 병목 해결 전략은 각각 고유의 트레이드오프(아킬레스건)를 수반합니다.

| 비교 항목 | Flutter (자체 엔진 탑재) | React Native (JSI 직통 채널) |
| :--- | :--- | :--- |
| **초기화 및 구동 지연** | **단점 (Cold Start Latency)**:<br>앱 시작 시 그래픽 엔진(Impeller/Skia) 및 Dart VM을 메모리에 로드하는 초기 구동 단계가 필요하여 로딩 지연이 발생할 수 있음. | **장점 (Fast Startup)**:<br>엔진 초기화 오버헤드가 없으므로 첫 진입 시 구동 속도가 비교적 빠르고 가벼움. |
| **애니메이션/셰이더 버벅임**| **단점 (Shader Jank)**:<br>최초 셰이더 그래픽 효과 컴파일 시 끊김 현상이 발생할 수 있음 (현재 Impeller 엔진 전환으로 극복 중). | **장점 (OS Native)**:<br>OS의 순정 하드웨어 가속 컴파일 및 렌더링 버퍼를 즉시 이용하므로 셰이더 컴파일 버벅임이 없음. |
| **앱 용량 (APK/IPA)** | **단점 (Heavy Engine Size)**:<br>붓과 도화지(C++ 그래픽 엔진)를 항상 내장해서 배포해야 하므로 기본 빈 앱의 용량이 큼. | **장점 (Lightweight Package)**:<br>네이티브 렌더링 시스템을 빌려 쓰므로 프레임워크 코어 용량이 상대적으로 가벼움. |
| **메모리 및 런타임 관리** | **장점 (Single Runtime)**:<br>자체 엔진 내에서 단일 가상 머신(Dart VM)이 화면 픽셀과 상태를 일관되게 제어하여 런타임 오버헤드가 적음. | **단점 (Double Runtime/Memory)**:<br>JS 런타임(Virtual DOM)과 OS 네이티브 런타임(Native View)의 두 세계가 메모리에 공존하여 이중 메모리 관리가 수반됨. |
| **OS 업데이트 대응력** | **장점 (OS Independence)**:<br>화면을 직접 그리기 때문에 OS 버전 업데이트로 UI 스타일이나 생명주기가 바뀌어도 영향을 거의 받지 않음. | **단점 (OS Dependency)**:<br>안드로이드/iOS의 순정 컴포넌트를 사용하므로, OS 업데이트로 생명주기나 스타일이 바뀌면 RN 코어 플러그인도 즉각 업데이트되어야 함. |

### 요약
- **Flutter**: 처음 구동할 때 엔진을 무겁게 띄우는 오버헤드(Startup Delay & Size)를 감수하되, 실행 중에는 OS 환경에 무관하게 일관되고 완벽히 통제되는 고주사율 렌더링 성능을 얻는 접근법입니다.
- **React Native**: 켜질 때는 가볍고 빠르게 진입하지만(Light Startup), 실행 중에는 두 종류의 런타임(JS vs Native)을 항상 공존시키며 서로 동기화하고 OS 환경 변화에 계속 대응해야 하는 비용을 감당하는 접근법입니다.
