import React, { useState } from 'react';
import api from '../api/axios'; // 서버에 댓글 작성 요청을 보낼 때 사용할 axios 인스턴스를 import
import { useRecoilValue } from 'recoil'; // 리코일 상태에서 현재 로그인한 사용자 정보를 읽기 위해 사용
import { userState } from '../recoil/atoms'; 
import styles from '../styles/CommentForm.module.scss';
import { useSetRecoilState } from 'recoil';
import { notificationReloadState } from '../recoil/notificationAtom';

function CommentForm({ postId, onCommentAdded }) { // 현재 작성하는 id, 댓글 작성 후 부모 컴포넌트에 새 댓글 전달하기 위한 함수
  const [content, setContent] = useState(''); // 사용자가 입력한 댓글 내용 저장하는 상태값
  const user = useRecoilValue(userState); // 로그인된 사용자의 정보를 리코일 전역 상태에서 읽어옴

  const setReload = useSetRecoilState(notificationReloadState);

  const handleSubmit = async (e) => {
    e.preventDefault(); // 폼 제출 시 기본 새로고침 동작 방지

    if (!user.isLoggedIn) {
      alert('로그인이 필요합니다.');
      return;
    }

    if (!content.trim()) {
      alert('댓글을 입력해주세요.');
      return; // 댓글에 공백만 입력하거나 아무거도 입력 안했으면 경고
    }

    try {
      const res = await api.post(`/api/posts/${postId}/comments/`, { // 장고 서버로 포스트 요청 보냄
        post: postId,
        content,
      });

      setContent('');
      onCommentAdded(res.data); // 새로운 댓글을 부모 컴포넌트에 전달
      setReload(prev => prev + 1);
    } catch (err) {
      console.error(err);
      alert('댓글 작성 실패');
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <textarea
        placeholder="댓글을 입력하세요"
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <button type="submit">작성</button>
    </form>
  );
}

export default CommentForm;
