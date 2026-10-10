// 매 요청마다 accesstoken을 자동으로 헤더에 붙이고, 토큰이 만료됐을 때 자동으로 재발급
import axios from 'axios';

const instance = axios.create({
  baseURL: (process.env.REACT_APP_API_URL || '').replace(/\/$/, '')  // 슬래시 끝에 제거
}); // 이 인스턴스는 모든 요청의 기본 주소를 여기로 한다.

console.log("✅ BASE_URL:", process.env.REACT_APP_API_URL);
// 모든 요청을 보내기 전에 가로채서 authorization 헤더에 토큰을 자동으로 붙임
// 이렇게 하면 매번 요청할 때 헤더를 넣을 필요가 없음
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 에러 시 토큰 재발급 처리
instance.interceptors.response.use(
  response => response,  // 응답이 성공적일때 그대로 리턴
  async error => {
    const originalRequest = error.config; // 에러가 발생했을 때 처리

    if (
      error.response?.status === 401 &&
      error.response?.data?.code === 'token_not_valid' &&
      !originalRequest._retry  // retry한 요청인지 확인(중복요청 확인)
    ) {
      originalRequest._retry = true; // retry 했다는 플래그를 설정

      try {
        const refresh = localStorage.getItem('refreshToken');
        // const res = await axios.post(`/api/accounts/refresh/`, { refresh }); // refresh token을 localstroage에서 꺼내서, 새 access token을 요청함
        const res = await instance.post(`/api/token/refresh/`, { refresh });

        const newAccess = res.data.access;
        localStorage.setItem('accessToken', newAccess); // 새 access token을 받아서 다시 저장함

        originalRequest.headers.Authorization = `Bearer ${newAccess}`; // 실패했던 요청에 새 토큰을 붙여서 다시 요청 보냄
        return instance(originalRequest); // retry 요청 재시도
      } catch (err) { // refresh 요청이 실패하면
        console.error('❌ Refresh Token 요청 실패:', err.response || err);
        localStorage.removeItem('accessToken'); 
        localStorage.removeItem('refreshToken'); // 저장한 토큰들 다 삭제
        window.location.href = '/login'; // 로그인 페이지로 강제이동
        return Promise.reject(err); // 에러 그대로 던짐
      }
    }

    return Promise.reject(error);
  }
);

export default instance;
