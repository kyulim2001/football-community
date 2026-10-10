import React, { useState } from 'react';
import api from '../api/axios';
import styles from '../styles/FindIDPage.module.scss';

const FindIDPage = () => {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState(1); // 1단계: 이메일 입력 → 2단계: 인증코드 입력
  const [username, setUsername] = useState('');

  const handleSendCode = async () => {
    try {
      const res = await api.post('/api/find-id/send-code/', { email });
      alert(res.data.detail || '인증 코드가 전송되었습니다.');
      setStep(2);
    } catch (err) {
      alert(err.response?.data?.detail || '인증 코드 전송 실패');
    }
  };

  const handleVerifyCode = async () => {
    try {
      const res = await api.post('/api/find-id/verify/', { email, code });
      setUsername(res.data.username);
      setStep(3);
    } catch (err) {
        alert(err.response?.data?.detail || '인증 실패');
    }
  };


  return (
    <div className={styles.findContainer}>
      <h2>아이디 찾기</h2>

      {step === 1 && (
        <>
          <input
            type="email"
            placeholder="가입한 이메일 주소 입력"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <button onClick={handleSendCode}>인증 코드 전송</button>
        </>
      )}

      {step === 2 && (
        <>
          <p>입력하신 이메일로 인증 코드가 전송되었습니다.</p>
          <input
            type="text"
            placeholder="인증 코드 입력"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
          <button onClick={handleVerifyCode}>확인</button>
        </>
      )}

      {step === 3 && (
        <p>
          해당 이메일로 가입된 아이디는 <strong>{username}</strong> 입니다.
        </p>
      )}
    </div>
  );
};

export default FindIDPage;
