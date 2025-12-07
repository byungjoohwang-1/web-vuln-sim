/**
 * Import function triggers from their respective submodules:
 *
 * const {onCall} = require("firebase-functions/v2/https");
 * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const { onRequest } = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");

// 기본 Hello World 함수 (필요 시 사용)
// 실제 정적 호스팅(html 파일들)은 이 함수를 거치지 않고 public 폴더에서 바로 서빙됩니다.
exports.helloWorld = onRequest((request, response) => {
  logger.info("Hello logs!", {structuredData: true});
  response.send("WEB-VULN-SIM Backend is Running!");
});