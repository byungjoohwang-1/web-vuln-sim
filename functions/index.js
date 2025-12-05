/**
 * Web Security Simulator - Backend Entry Point
 *
 * 현재 시뮬레이터는 교육 목적의 정적 웹사이트(Static Website)로 설계되어 있어,
 * 대부분의 취약점 시뮬레이션 로직이 브라우저(Client-side)의 iframe 내에서 동작합니다.
 *
 * 이 파일은 Firebase Cloud Functions의 진입점으로, 향후 서버 사이드 로직
 * (예: 실제 DB 연동, 공격 로그 수집, 사용자 인증 검증 등)이 필요할 때 
 * 확장할 수 있도록 준비된 기본 템플릿입니다.
 */

const { onRequest } = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");

// -------------------------------------------------------------------------
// 1. 기본 헬스 체크 API (Health Check)
// -------------------------------------------------------------------------
// 배포 후 접속 주소 예시: https://<project-id>.web.app/api/hello (설정에 따라 다름)
// 또는 Firebase Console의 Functions 탭에서 제공하는 URL로 직접 접속 가능
exports.hello = onRequest((request, response) => {
  // Cloud Functions 로그에 기록 (Firebase Console에서 확인 가능)
  logger.info("Health Check Invoked", {structuredData: true});
  
  // 클라이언트에 JSON 응답 반환
  response.json({
    status: "online",
    message: "SecSim Backend is running successfully.",
    serverTime: new Date().toISOString(),
    version: "2.0.0"
  });
});

// -------------------------------------------------------------------------
// 2. (예시) 간단한 에코 서버 (Echo Server)
// -------------------------------------------------------------------------
// 클라이언트가 보낸 데이터를 그대로 반환하여 통신 테스트를 할 수 있는 함수입니다.
exports.echo = onRequest((request, response) => {
  const data = request.query.msg || request.body.msg || "No message received";
  
  logger.info(`Echo request: ${data}`, {structuredData: true});

  response.json({
    received: data,
    length: data.length
  });
});