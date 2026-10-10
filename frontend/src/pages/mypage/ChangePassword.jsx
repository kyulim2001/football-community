import React, { useState } from 'react';
import api from '../../api/axios';
import { useNavigate } from 'react-router-dom';
import styles from '../../styles/ChangePassword.module.scss';

 
const ChangePassword = () => { // 비밀번호 변경 UI를 나타내는 리액트 함수형 컴포넌트
    const [oldPassword, setOldPassword] = useState(''); // 현재 비번
    const [newPassword1, setNewPassword1] = useState(''); // 새 비번 입력
    const [newPassword2, setNewPassword2] = useState(''); // 새 비번 확인 입력
    const [message, setMessage] = useState('');

    const navigate = useNavigate();
    
    const handleChangePassword = () => { // 비밀번호 변경 요청을 처리할 함수 정의
        if (newPassword1 !== newPassword2) {
            setMessage('새 비밀번호가 일치하지 않습니다.');
            return;
        }
        // api.patch('/accounts/change_password/',
        api.post('/api/mypage/change-password/', {
            old_password: oldPassword,
            new_password1: newPassword1,
            new_password2: newPassword2
        })
            .then(() => {
              setMessage('비밀번호가 성공적으로 변경되었습니다.');
              setTimeout(() => {
                navigate('/');
              }, 1000);
            })
              
            .catch((err) => {
                console.error(err);
                setMessage('비밀번호 변경에 실패했습니다.');
            });
    };
  return (
    <div className={styles.container}>
      <h3 className={styles.heading}>비밀번호 변경</h3>
      <input
        type="password"
        placeholder="현재 비밀번호"
        value={oldPassword}
        onChange={(e) => setOldPassword(e.target.value)}
        className={styles.input}
      />
      <input
        type="password"
        placeholder="새 비밀번호"
        value={newPassword1}
        onChange={(e) => setNewPassword1(e.target.value)}
        className={styles.input}
      />
      <input
        type="password"
        placeholder="새 비밀번호 확인"
        value={newPassword2}
        onChange={(e) => setNewPassword2(e.target.value)}
        className={styles.input}
      />
      <button onClick={handleChangePassword} className={styles.button}>
        변경
      </button>
      {message && <p className={styles.message}>{message}</p>}
    </div>
  );
};
export default ChangePassword;