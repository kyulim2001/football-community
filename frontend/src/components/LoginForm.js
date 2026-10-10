import React, { useState } from 'react'; // 리액트에서 상태를 관리할 수 있게 해주는 기본 훅(?)
import api from '../api/axios'; 
import { useSetRecoilState } from 'recoil'; // 리코일의 상태를 변경할 때 사용
import { userState } from '../recoil/atoms'; // 로그인 성공 시 유저 정보를 저장할 전역 상태
import { useNavigate, Link } from 'react-router-dom'; // 로그인 성공 후 다른 페이지로 이동하게 해주는 훅(리액트 라우터에서 제공)
import styles from '../styles/LoginForm.module.scss';

const LoginForm = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState(''); // 사용자가 입력한 값을 저장
    const setUser = useSetRecoilState(userState); // 로그인 성공 시 전역 상태를 업데이트하는 함수
    const navigate = useNavigate(); // 로그인 성공 후 메인화면이나 마이페이지로 이동할 때 사용

    const handleSubmit = async (e) => { // 로그인 누를때 실행되는 함수
        e.preventDefault();
        try {
            const res = await api.post('/api/auth/login/', { username, password }); // 백엔드로 요청을 보냄
            const { access, refresh, nickname, id } = res.data // 로그인 성공시 받은걸 저장
            localStorage.setItem('accessToken', access); // 토큰을 브라우저에 저장
            localStorage.setItem('refreshToken', refresh);
            const userData = {isLoggedIn:true, username, nickname, id};
            setUser(userData);
            localStorage.setItem('userState', JSON.stringify(userData));
            navigate('/'); // 로그인 후 홈 화면
        } catch (err) {
            alert(err.response?.data?.error); // 실패 시 백엔드에서 만든 메시지 띄움
        }
    };
    return (
    <>
        <form onSubmit={handleSubmit} className={styles.form}>
        <input
            type="text"
            placeholder="아이디"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
        />
        <input
            type="password"
            placeholder="비밀번호"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">로그인</button>
        </form>

        <div className={styles.links}>
        <Link to="/find-id">아이디 찾기</Link> |{" "}
        <Link to="/find-password">비밀번호 찾기</Link>
        </div>
    </>
    );
}
export default LoginForm;