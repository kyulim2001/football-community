import React, { useState } from 'react';
import api from '../../api/axios'; // 장고 서버로 http 요청을 보내기 위한 라이브러리
import { useSetRecoilState } from 'recoil';
import { userState } from '../../recoil/atoms'; // 리코일을 사용해 유저상태를 업데이트
import { useNavigate } from 'react-router-dom'; // 탈퇴후 홈페이지로 이동을 위해 navigate 함수 사용
import styles from '../../styles/DeleteAccount.module.scss';

const DeleteAccount = () => {
    const setUser = useSetRecoilState(userState);
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    
    const handleDelete = () => {
        if(!window.confirm('정말로 탈퇴하시겠습니까?')) return; // 사용자에게 확인창을 띄움

        api.delete('/api/mypage/delete-account/', {
            data: { password } // 비밀번호는 data에 포함시켜서 전달
        })
            .then(() => {
                setMessage('회원탈퇴가 완료되었습니다.'); 

                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken'); // 로컬스토리지에 저장된 jwt 토큰 삭제 -> 로그아웃 처리
                setUser({isLoggedIn: false, username: '', nickname: ''}); // 리코일 userstate 초기화
                localStorage.removeItem('userState'); // 로컬스토리지에 userstate 저장되어있으면 그거도 삭제
                setTimeout(() => {
                    navigate('/'); // 2초 후 홈페이지로 이동
                }, 2000);
            })
            .catch(err => {
                console.error(err);
                setMessage("비밀번호가 틀렸습니다.");
            });
    };
  return (
    <div className={styles.container}>
      <h3 className={styles.heading}>회원 탈퇴</h3>
      <input
        type="password"
        placeholder="비밀번호를 입력하세요"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className={styles.input}
      />
      <button onClick={handleDelete} className={styles.button}>
        탈퇴하기
      </button>
      {message && <p className={styles.message}>{message}</p>}
    </div>
  );
};
export default DeleteAccount;