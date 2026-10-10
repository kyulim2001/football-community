import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useRecoilValue, useSetRecoilState } from 'recoil'; // 1. userstate 값을 읽기 전용으로 사용, 2. userstate 값을 직접 수정할 때 사용
import { userState } from '../recoil/atoms'; // atoms.js에서 정의한 전역상태
import styles from '../styles/Header.module.scss';
import NotificationDropdown from './NotificationDropdown';
import { notificationReloadState } from '../recoil/notificationAtom';

function Header() {
  const user = useRecoilValue(userState); // 현재 로그인된 사용자 정보 객체
  const setUser = useSetRecoilState(userState); // 로그아웃 시 이 값을 초기화함
  const navigate = useNavigate(); 
  const reloadTrigger = useRecoilValue(notificationReloadState);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userState'); // 브라우저에 저장된 토큰 및 유저 정보를 갖고옴

    setUser({
      isLoggedIn: false,
      username: '',
      nickname: '',
    }); // 리코일 상태도 초기화하여 화면 상에서도 로그아웃 상태로 전환

    navigate('/login');
  };

return (
  <header className={styles.header}>
    <div className={styles.container}>
      <div className={styles.left}>
      <Link to="/" className={styles.logo}>
        <img src="/assets/logo.png" alt="로고" className={styles.logoImg} />
        해외축구
      </Link>
      </div>

      <nav className={styles.center}>
        <Link to="/board/premier-league">프리미어리그</Link>
        <Link to="/board/la-liga">라리가</Link>
        <Link to="/board/bundesliga">분데스리가</Link>
        <Link to="/board/serie-a">세리에A</Link>
        <Link to="/board/ligue-1">리그앙</Link>
        <Link to="/chat">채팅</Link>
      </nav>

      <div className={styles.right}>
        {user.isLoggedIn ? (
          <>
            <NotificationDropdown reloadTrigger={reloadTrigger} />
            <Link to="/mypage" className={styles.nickname}>{user.nickname}님</Link>
            <button onClick={handleLogout} className={styles.logoutButton}>로그아웃</button>
          </>
        ) : (
          <>
            <Link to="/login" className={styles.authButton}>로그인</Link>
            <Link to="/signup" className={styles.authButton}>회원가입</Link>
          </>
        )}
      </div>
    </div>
  </header>
);
}

export default Header;
