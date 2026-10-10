import { atom } from 'recoil'; // 리코일의 아톰 기능을 가져와서 상태를 만듦

export const userState = atom({ // 다른 곳에서도 쓸 수 있게끔 export
    key: 'userState', // 전역 상태의 고유 이름(리코일 내부에서 식별용)
    default: { // 초기값 정의
        isLoggedIn: false,
        username: '',
        nickname: '',
    }
})
