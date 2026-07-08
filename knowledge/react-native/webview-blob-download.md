# WebView 환경에서의 Blob 객체 다운로드 우회 패턴

> **Context**: `blaster-launcher` 프로젝트에서 `REPORT DOWNLOAD PDF` 기능 구현 중, 웹 브라우저 환경에서는 정상적으로 다운로드되던 기능이 Android WebView(런처) 환경에서 작동하지 않는 현상을 해결하기 위해 정립한 연동 규격.
> 서버 API가 Bearer 토큰 인증을 요구하므로 단순 URL 이동이 불가하고, Axios를 통해 메모리(Blob)로 가져온 바이너리를 네이티브 브릿지(`postMessage`)를 거쳐 디바이스 물리 저장소에 안전하게 기록한다.

---

## 1. 핵심 개념 정의

### Blob (Binary Large Object)
- **정의**: 이미지, PDF, 오디오, 비디오 등 대용량 이진(Binary) 데이터를 브라우저 메모리 안에서 다루기 위해 설계된 불변(Immutable)의 자바스크립트 객체.
- **물리적 특성**: 파일의 가공되지 않은 원바이트 데이터를 담고 있으며, 디스크의 실제 파일 시스템에 저장하기 전 브라우저 탭의 할당 메모리 힙(Heap) 영역 내에 상주한다.

### Bearer 토큰 인증과 Axios 다운로드의 필연성
- **일반 다운로드의 한계**: `<a href="download_url">` 링크 클릭이나 `window.location.href` 이동 방식은 브라우저의 기본 GET 내비게이션을 수행하므로, HTTP Request Header에 `Authorization: Bearer <Token>`을 실어 보낼 수 없다.
- **해결 기법**: 클라이언트 측에서 `axios` 또는 `fetch` API를 사용해 헤더를 주입한 비동기 요청을 직접 보내고, 응답 페이로드를 바이너리 형식(`responseType: 'blob'`)으로 수신하여 가상의 Blob 객체로 재조합한다.

---

## 2. 발생 문제 및 한계 분석

### 임시 Blob URL (`blob:`)의 가상성
- 브라우저 환경에서는 Blob 데이터에 접근하기 위해 `URL.createObjectURL(blob)`을 호출하여 가상 URL을 생성한다.
  - 예: `blob:https://yourdomain.com/3f82b0e4-b77e-49b0-9883-fa3495d4812a`
- 이 주소는 **실제 서버의 물리 주소가 아니며**, 오직 해당 브라우저 탭의 메모리 주소 영역을 가리키는 가짜 임시 포인터다. 따라서 탭이 닫히거나 메모리에서 해제(Revoke)되면 해당 주소는 소멸한다.

### Android WebView 및 DownloadManager의 거부
- **동작 방식**: Android의 `WebView` 내부에서 다운로드 이벤트가 감지되면, 이를 운영체제 레벨의 `DownloadManager`에 위임한다.
- **한계점**: `DownloadManager`는 별도의 백그라운드 OS 스레드에서 해당 주소로 HTTP GET 요청을 날려 파일을 직접 새로 받는 구조다. 따라서 브라우저 탭 내부 메모리에만 존재하는 `blob:` 가짜 URL은 OS 네트워크 스택이 인식할 수 없기 때문에 다운로드 요청이 **거부되거나 중단**된다.

```
[WebView Browser Tab Memory]              [Android System (OS)]
┌───────────────────────────┐             ┌─────────────────────┐
│ Axios GET (with Auth)     │             │                     │
│   └─► PDF Binary (Blob)   │             │                     │
│        └─► blob:temp_url  │             │                     │
│              │            │             │                     │
│              └─(Click)───┼─►[OS DownloadManager]              │
│                           │         │                         │
│                           │         └─► HTTP GET blob:temp_url│
│                           │             (URL 해석 불가능 ➔ 실패)│
└───────────────────────────┘             └─────────────────────┘
```

---

## 3. 해결 설계: Base64 포스트메시지 브릿지 패턴

WebView 내에 있는 가상 바이너리(Blob) 데이터를 데이터 스트림 형식으로 변환하여 React Native(Native) 영역으로 직접 전송하는 브릿지 아키텍처를 도입하여 이 문제를 우회한다.

```
[WebView (Web Content)]                      [React Native (Native)]
┌─────────────────────────────────┐          ┌───────────────────────────────────┐
│ 1. Axios (Bearer Auth)          │          │                                   │
│ 2. Blob Binary 수신             │          │                                   │
│ 3. FileReader (Blob ➔ Base64)   │          │                                   │
│ 4. postMessage(base64Payload) ──┼─────────┼──► onMessage(event) 수신           │
│                                 │          │    5. Base64 ➔ Binary 변환        │
│                                 │          │    6. RNFS로 로컬 물리 디스크 저장│
└─────────────────────────────────┘          └───────────────────────────────────┘
```

### 1) Web-side 구현 (프론트엔드 컴포넌트)

Blob을 텍스트 데이터 포맷인 **Base64 String**으로 인코딩한 뒤, 웹뷰 브릿지(`window.ReactNativeWebView.postMessage`)를 통해 네이티브 단으로 직렬화해 전달한다.

```javascript
import axios from 'axios';

/**
 * PDF 보고서를 요청하고 다운로드 이벤트를 처리하는 함수
 */
export const downloadReportPdf = async (reportId, token) => {
  try {
    // 1. Authorization 헤더를 실어 이진 데이터(Blob) 요청
    const response = await axios.get(`/api/v1/reports/${reportId}/pdf`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      responseType: 'blob', // 바이너리 데이터를 받도록 설정
    });

    const blob = response.data;
    const fileName = `Report_${reportId}_${new Date().getTime()}.pdf`;

    // 2. 브라우저가 WebView 내부 환경인지 일반 PC 브라우저인지 감지
    const isApp = window.ReactNativeWebView !== undefined;

    if (isApp) {
      // 3. Android WebView 환경 대응: FileReader를 통해 Base64 변환
      const reader = new FileReader();
      reader.readAsDataURL(blob); // Data URL 포맷 (data:application/pdf;base64,...)
      
      reader.onloadend = () => {
        const base64Url = reader.result;
        // 접두어 (data:application/pdf;base64,) 제거하고 순수 데이터 본문만 추출
        const pureBase64 = base64Url.split(',')[1];

        // 4. 네이티브 단으로 Base64 데이터 및 메타데이터 전송
        window.ReactNativeWebView.postMessage(
          JSON.stringify({
            event: 'DOWNLOAD_PDF',
            payload: {
              base64Data: pureBase64,
              fileName: fileName,
              mimeType: 'application/pdf',
            },
          })
        );
      };
    } else {
      // 5. 일반 웹 브라우저 환경 대응 (Fallback)
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      
      // 가상 돔 정리 및 메모리 누수 방지
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }
  } catch (error) {
    console.error('PDF 다운로드 처리 중 에러 발생:', error);
    throw error;
  }
};
```

### 2) Native-side 구현 (React Native WebView 컴포넌트)

웹으로부터 들어온 메시지를 리스닝하여, Base64 문자열을 원천 바이너리 스트림으로 디코딩해 기기 내부 물리 파일 시스템에 안전하게 기록한다.

```typescript
import React from 'react';
import { StyleSheet, Alert } from 'react-native';
import { WebView } from 'react-native-webview';
import RNFS from 'react-native-fs';
import FileViewer from 'react-native-file-viewer';

export const ServiceScreen = () => {
  const handleWebViewMessage = async (event: any) => {
    try {
      const messageData = JSON.parse(event.nativeEvent.data);

      if (messageData.event === 'DOWNLOAD_PDF') {
        const { base64Data, fileName, mimeType } = messageData.payload;

        // 1. 앱 내부 전용 물리적 저장 경로 확보
        // Android: /data/user/0/com.hanwha.blaster.launcher/files
        const targetPath = `${RNFS.DocumentDirectoryPath}/${fileName}`;

        // 2. Base64 인코딩 스트림을 바이너리 파일로 복원하여 디스크에 작성
        await RNFS.writeFile(targetPath, base64Data, 'base64');
        
        Alert.alert(
          '다운로드 완료',
          '보고서 파일이 다운로드 폴더에 안전하게 저장되었습니다.',
          [
            {
              text: '열기',
              onPress: async () => {
                try {
                  // 3. 다운로드 완료 후 OS Viewer 어플리케이션으로 바로 연계
                  await FileViewer.open(targetPath, { showOpenWithDialog: true });
                } catch (viewError) {
                  Alert.alert('파일 열기 실패', '지원하는 파일 뷰어가 기기에 설치되어 있지 않습니다.');
                }
              },
            },
            { text: '확인', style: 'cancel' },
          ]
        );
      }
    } catch (error) {
      console.error('Native PDF Save Failure:', error);
      Alert.alert('오류', '런처 파일 저장 중 예외가 발생했습니다.');
    }
  };

  return (
    <WebView
      source={{ uri: 'https://yourdomain.com/service/report' }}
      onMessage={handleWebViewMessage}
      style={styles.container}
    />
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
```

---

## 4. 고려 사항 및 베스트 프랙티스

1. **메모리 오버헤드 방지**: 
   - Base64 변환은 약 33%의 크기 오버헤드를 발생시킨다. 수십 메가바이트(MB) 이상의 기가급 파일 다운로드 시 모바일 WebView 및 JS 엔진의 OOM(Out of Memory)을 유발할 수 있으므로, 해당 방식은 보고서(PDF), 티켓 이미지 등 **수십 MB 미만의 가벼운 바이너리 파일 스펙에 최적화**된다.
2. **권한 처리**:
   - Android 10 (API 29) 이상에서는 Scoped Storage가 적용되므로 `RNFS.DocumentDirectoryPath`와 같이 앱 전용 디렉토리에 저장할 때는 런타임 저장소 쓰기 권한(`WRITE_EXTERNAL_STORAGE`)이 필요 없다. 단, 공용 다운로드 폴더(`Download/`)에 저장하기를 희망할 경우 별도의 권한 관리 및 Android Content Resolver 연동이 필수적이다.
3. **파일 뷰어 연동성**:
   - 파일을 다운로드한 즉시 사용자가 즉각적으로 내용을 확인할 수 있도록 `react-native-file-viewer` 또는 Android Intent 연동을 가미하여 열기 편의성을 대폭 보완하는 것이 UX 품질 측면에서 추천된다.
