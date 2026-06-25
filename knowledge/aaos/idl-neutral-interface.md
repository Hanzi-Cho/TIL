# 언어 중립적 인터페이스 정의 (IDL)

> IPC/RPC 경계를 넘는 인터페이스는 왜 별도 확장자(.aidl, .proto, .thrift)로 정의하는가

## 핵심 개념

별도 확장자는 단순한 관례가 아니라 **빌드 시스템에 대한 계약 선언**이다.

"이 인터페이스는 프로세스/네트워크 경계를 넘으므로, 직렬화 코드를 자동 생성하라"는 트리거.

일반 소스 파일(.java, .kt, .py)에 섞이면:
- 어떤 인터페이스가 IPC용인지 빌드 툴이 구분 불가
- 직렬화/역직렬화(marshalling) 코드 자동 생성 불가
- 프로세스 경계 통신임을 강제하는 컴파일 타임 계약이 사라짐

---

## 1. AIDL (Android Interface Definition Language)

**사용처**: Android Binder IPC (앱 ↔ 시스템 서비스, 앱 ↔ 앱)

```
// IMyService.aidl
package com.example;

interface IMyService {
    int add(int a, int b);
    String getDeviceInfo();
}
```

**빌드 흐름**:
```
IMyService.aidl
    ↓ (aidl 컴파일러)
IMyService.java  ← Stub + Proxy 자동 생성
    ↓
Kotlin/Java에서 사용
```

- `.aidl` 자체는 Java도 Kotlin도 아닌 별도 DSL (Java 문법과 유사)
- Kotlin으로 직접 작성 불가, 생성된 Java 코드를 Kotlin에서 사용하는 건 가능
- `Stub.asInterface()`: 동일 프로세스면 직접 호출, 다른 프로세스면 Proxy 반환

---

## 2. Protocol Buffers (gRPC / .proto)

**사용처**: 언어/플랫폼 중립 네트워크 RPC

```protobuf
// calculator.proto
syntax = "proto3";

package calculator;

service CalculatorService {
    rpc Add (AddRequest) returns (AddResponse);
    rpc GetDeviceInfo (Empty) returns (DeviceInfoResponse);
}

message AddRequest {
    int32 a = 1;
    int32 b = 2;
}

message AddResponse {
    int32 result = 1;
}

message DeviceInfoResponse {
    string model = 1;
}

message Empty {}
```

**빌드 흐름**:
```
calculator.proto
    ↓ (protoc 컴파일러 + 언어별 플러그인)
calculator_pb2.py       ← Python
calculator.pb.go        ← Go
CalculatorGrpc.java     ← Java/Kotlin
calculator_pb.rb        ← Ruby
```

- **동일한 .proto → 여러 언어 코드 생성** → 언어 중립성의 핵심
- 필드 번호(= 1, = 2)가 직렬화 키 → 필드명 변경해도 하위 호환 유지
- binary 직렬화로 JSON 대비 3~10x 작은 페이로드

---

## 3. 비교 요약

| | AIDL | .proto (gRPC) | Thrift |
|---|---|---|---|
| **주 사용처** | Android IPC | 네트워크 RPC | 다언어 RPC |
| **전송 계층** | Binder (커널) | HTTP/2 | TCP |
| **언어 중립** | Android 한정 | 완전 중립 | 완전 중립 |
| **직렬화** | Parcel | Protobuf binary | Thrift binary |
| **생성 코드** | Java Stub/Proxy | 언어별 client/server | 언어별 client/server |

---

## 핵심 인사이트

> **IDL 파일 = 프로세스/네트워크 경계의 계약서**
>
> 경계를 넘는 순간 타입 시스템이 보장되지 않으므로,
> 별도 도구가 직렬화 계층을 생성해야 한다.
> 별도 확장자는 그 경계를 빌드 시스템에 명시하는 방법이다.

## 관련 개념
- Binder IPC, mmap, Parcel
- gRPC streaming (unary / server-streaming / bidirectional)
- Protobuf field number와 하위 호환성

---
*2026-06-24*
