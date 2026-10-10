import React, { useEffect, useState } from "react";
import api from "../../api/axios";
import { useRecoilState } from 'recoil';
import { userState } from '../../recoil/atoms';
import styles from '../../styles/MyInfo.module.scss';

function MyInfo() {
    const [userInfo, setUserInfo] = useState(null);
    const [user, setUser] = useRecoilState(userState);
    const [nickname, setNickname] = useState(user.nickname);
    const [editing, setEditing] = useState(false);

    const handleUpdateNickname = async () => {
    try {
      const res = await api.patch('/api/mypage/update-nickname/', { nickname });
      alert('닉네임이 변경되었습니다.');
      const updatedUser = { ...user, nickname: res.data.nickname };
      setUser(updatedUser);
      localStorage.setItem('userState', JSON.stringify(updatedUser));
      setEditing(false);
    } catch (err) {
      alert(err.response?.data?.error || '닉네임 변경 실패');
    }
  };

    useEffect(() => {
        const token = localStorage.getItem("accessToken");

        //api.get("/api/accounts/me/",
        api.get('api/mypage/me/', {
            headers: {
                Authorization: `Bearer ${token}`, // 요청의 헤더에 authorization을 추가해서 jwt 토큰을 같이 보냄
            },
        })
        .then((res) => {
            setUserInfo(res.data);
        })
        .catch((err) => {
            console.error("유저 정보 불러오기 실패:", err);
        });
    }, []);

    if (!userInfo) return <div>불러오는 중...</div>;

    return (
    <div className={styles.container}>
      <h3>내 정보</h3>
      <p><strong>아이디:</strong> {userInfo.username}</p>
      <p className={styles.nicknameRow}>
        닉네임:{' '}
        {editing ? (
          <>
            <input value={nickname} onChange={(e) => setNickname(e.target.value)} />
            <button onClick={handleUpdateNickname}>저장</button>
            <button className={styles.cancel} onClick={() => setEditing(false)}>취소</button>
          </>
        ) : (
          <>
            {user.nickname}
            <button onClick={() => setEditing(true)} style={{ marginLeft: '10px' }}>
              수정
            </button>
          </>
        )}
      </p>
      {userInfo.email && <p><strong>이메일:</strong> {userInfo.email}</p>}
    </div>
    );
}

export default MyInfo;
