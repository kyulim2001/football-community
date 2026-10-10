// 리코일 상태 라이브러리, 로그인 상태를 전역에서 관리하기 위함
import { atom } from 'recoil'; // 리코일에서 전역 상태를 만들 때 사용하는 함수

const storedUser = localStorage.getItem('userState'); // 브라우저에 저장된 로그인 상태를 localstroage에서 불러옴(문자열)
const parsedUser = storedUser ? JSON.parse(storedUser): null; // 문자열을 객체로 변환

export const userState = atom({ // 전역 상태를 선언하고 외부에서 쓸 수 있게끔 export
  key: 'userState', // 이 atom의 고유 id 역할, 리코일에서 이거로 상태 구분을 함
  default: JSON.parse(localStorage.getItem('userState')) || { // 로컬 스토리지에 저장되있는 값이 있으면 그걸 쓰고 아니면 로그아웃 상태로 시작
    isLoggedIn: false,
    username: '',
    nickname: '',
  },
effects_UNSTABLE: [ // 상태 변화에 부가동작 추가
    ({ setSelf, onSet }) => { // atom이 초기화되거나 변경될 때 실행
      const saved = localStorage.getItem('userState');
      if (saved != null) { // 저장된 값이 있으면 그걸 atom 초기값으로 설정
        setSelf(JSON.parse(saved));
      }

      onSet((newValue) => { // 상태가 바뀔때마다 자동으로 localstorage에 저장, 이걸로 새로고침이나 나갔다와도 로그인 유지
        localStorage.setItem('userState', JSON.stringify(newValue));
      });
    },
  ],
});

export const blockedUserIdState = atom({
  key: 'blockedUserIdState',
  default: [],
});
