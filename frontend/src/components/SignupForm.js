import React, { useState } from 'react';
import api from '../api/axios';
import styles from '../styles/SignupForm.module.scss';
import { useNavigate } from 'react-router-dom';

function SignupForm() {
  const [username, setUsername] = useState('');
  const [nickname, setNickname] = useState('');
  const [email, setEmail] = useState('');
  const [emailCode, setEmailCode] = useState('');
  const [emailVerified, setEmailVerified] = useState(false);
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const navigate = useNavigate();

  const handleSendCode = async () => {
    try {
      const res = await api.post('/api/signup/send-code/', { email });
      alert(res.data.detail);
    } catch (err) {
      alert(err.response?.data?.detail || '인증 코드 전송 실패');
    }
  };

  const handleVerifyCode = async () => {
    try {
      const res = await api.post('/api/signup/verify/', { email, code: emailCode });
      alert(res.data.detail);
      setEmailVerified(true);
    } catch (err) {
      alert(err.response?.data?.detail || '인증 실패');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!emailVerified) {
      alert('이메일 인증을 완료해주세요.');
      return;
    }

    if (password !== password2) {
      alert('비밀번호가 일치하지 않습니다.');
      return;
    }

    try {
      const res = await api.post('/api/auth/signup/', {
        username,
        nickname,
        email,
        password,
        password2,
      });
      alert('회원가입 성공!');
      navigate('/');
    } catch (err) {
      console.error(err.response.data);
      alert(err.response?.data?.detail || '회원가입 실패');
    }
  };

return (
  <form className={styles.signupForm} onSubmit={handleSubmit}>
    <h2>회원가입</h2>

    <div className={styles.section}>
      <label>아이디</label>
      <input
        placeholder="아이디"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
    </div>

    <div className={styles.section}>
      <label>닉네임</label>
      <input
        placeholder="닉네임"
        value={nickname}
        onChange={(e) => setNickname(e.target.value)}
      />
    </div>

    <div className={styles.section}>
      <label>이메일</label>
      <input
        placeholder="이메일"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <div className={styles.inlineButtons}>
        <button type="button" onClick={handleSendCode}>인증코드 전송</button>
      </div>
    </div>

    <div className={styles.section}>
      <label>인증 코드</label>
      <div className={styles.verificationGroup}>
        <input
          placeholder="인증 코드"
          value={emailCode}
          onChange={(e) => setEmailCode(e.target.value)}
        />
        <button type="button" onClick={handleVerifyCode}>코드 확인</button>
      </div>
    </div>

    <div className={styles.section}>
      <label>비밀번호</label>
      <input
        type="password"
        placeholder="비밀번호"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
    </div>

    <div className={styles.section}>
      <label>비밀번호 확인</label>
      <input
        type="password"
        placeholder="비밀번호 확인"
        value={password2}
        onChange={(e) => setPassword2(e.target.value)}
      />
    </div>

    <button type="submit" className={styles.submitButton}>회원가입</button>
  </form>
);
}

export default SignupForm;
