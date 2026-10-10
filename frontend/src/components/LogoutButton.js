// src/components/LogoutButton.js
import { useNavigate } from 'react-router-dom';
import { useResetRecoilState } from 'recoil'; // 리코일에서 전역 상태를 초기값으로 되돌리는 함수를 가져옴
import { userState } from '../recoil/atoms';
import styles from '../styles/LogoutButton.module.scss';

function LogoutButton() {
  const navigate = useNavigate(); // 로그인 페이지로 이동할 때 사용할 함수
  const resetUser = useResetRecoilState(userState); // userState를 초기값으로 리셋하는 함수
  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userState');
    resetUser(); // 리코일 상태 초기화
    navigate('/login');
  };

  return <button className={styles.button} onClick={handleLogout}>로그아웃</button>;
}

export default LogoutButton;
