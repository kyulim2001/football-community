import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import UserPosts from './UserPosts';
import UserComments from './UserComments';
import styles from '../../styles/UserProfile.module.scss';
import api from '../../api/axios';
import { useRecoilValue } from 'recoil';
import { userState } from '../../recoil/atoms';
import { useSetRecoilState } from 'recoil';
import { blockedUserIdState } from '../../recoil/atoms';
import { useNavigate } from 'react-router-dom';

function UserProfile() {
  const { userId } = useParams(); // userId는 실제로는 nickname
  const [tab, setTab] = useState('posts');
  const [targetUser, setTargetUser] = useState(null);
  const [blockId, setBlockId] = useState(null);
  const loggedInUser = useRecoilValue(userState);
  const setBlockedUserIds = useSetRecoilState(blockedUserIdState);
  const navigate = useNavigate();

  useEffect(() => {
    api.get(`/api/accounts/nickname/${userId}/`)
      .then(res => {
        console.log("res.data:", res.data);
        setTargetUser(res.data);
      });
  }, [userId]);

  useEffect(() => {
    if (!targetUser || !loggedInUser?.isLoggedIn) return;

    api.get('/api/accounts/blocks/')
      .then(res => {
        const blocks = res.data.results || [];
        const found = blocks.find(b => b.blocked === targetUser.id);
        if (found) setBlockId(found.id);
        else setBlockId(null);
      });
  });

  const handleBlock = async () => {
    if (!window.confirm("정말로 차단하시겠습니까?")) return;
    try {
      await api.post('/api/accounts/blocks/', { blocked: targetUser.id });
      alert('차단 완료');

      setBlockedUserIds(prev => [...prev, targetUser.id]);
      setBlockId(true);
      navigate("/");
    } catch(err) {
      alert(err.response?.data?.detail || "차단 실패");
    }
  };

  const handleUnblock = async () => {
    if(!window.confirm("차단을 해제하시겠습니까?")) return;
    try {
      await api.delete(`/api/accounts/blocks/${blockId}/`);
      alert('차단 해제 완료');

      setBlockedUserIds(prev => prev.filter(id => id !== targetUser.id));
      setBlockId(null);
      navigate("/");
    } catch (err) {
      alert(err.response?.data?.detail || "차단 해제 실패"); 
    }
  };

    return (
    <div className={styles.profileContainer}>
      <h1 className={styles.profileTitle}>
        {targetUser?.is_active ? `${userId}님의 프로필` : '탈퇴한 회원'}
      </h1>
      {loggedInUser?.isLoggedIn &&
        targetUser &&
        loggedInUser.username !== targetUser.username && 
        targetUser.is_active && (
          <div className={styles.blockButtonWrapper}>
            {blockId === null ? (
              <button onClick={handleBlock} className={styles.blockButton}>차단하기</button>
            ) : (
              <button onClick={handleUnblock} className={styles.unblockButton}>차단 해제</button>
            )}
          </div>
        )
      }

      <div className={styles.tabButtons}>
        <button
          onClick={() => setTab('posts')}
          className={tab === 'posts' ? styles.active : ''}
        >
          작성한 글
        </button>
        <button
          onClick={() => setTab('comments')}
          className={tab === 'comments' ? styles.active : ''}
        >
          작성한 댓글
        </button>
      </div>

      {tab === 'posts' && <UserPosts nickname={userId} />}
      {tab === 'comments' && <UserComments nickname={userId} />}
    </div>
  );
}



export default UserProfile;
