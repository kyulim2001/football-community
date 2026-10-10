// src/pages/FindPasswordPage.js
import React, { useState } from 'react';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';
import styles from '../styles/FindPasswordPage.module.scss';

function FindPasswordPage() {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [verified, setVerified] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const navigate = useNavigate();

  const handleSendCode = async () => {
    try {
      const res = await api.post('/api/find-password/send-code/', { email });
      alert(res.data.detail);
    } catch (err) {
      alert(err.response?.data?.detail || '인증 코드 전송 실패');
    }
  };

  const handleVerify = async () => {
    try {
      const res = await api.post('/api/find-password/verify/', { email, code });
      alert(res.data.detail);
      setVerified(true);  // 성공하면 다음 단계로
    } catch (err) {
      alert(err.response?.data?.detail || '인증 실패');
    }
  };

  const handleResetPassword = async () => {
    try {
      const res = await api.post('/api/find-password/reset-password/', {
        email,
        code,
        new_password: newPassword,
      });
      alert(res.data.detail || '비밀번호 변경 완료');
      navigate('/login');
    } catch (err) {
      alert(err.response?.data?.detail || '비밀번호 변경 실패');
    }
  };

  return (
    <div className={styles.container}>
      <h2>비밀번호 찾기</h2>
      <input
        type="email"
        placeholder="가입한 이메일"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <button onClick={handleSendCode}>인증 코드 전송</button>

      <input
        type="text"
        placeholder="인증 코드"
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
      <button onClick={handleVerify}>코드 확인</button>

      {verified && (
        <>
          <input
            type="password"
            placeholder="새 비밀번호"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <button onClick={handleResetPassword}>비밀번호 재설정</button>
        </>
      )}
    </div>
  );
}

export default FindPasswordPage;
