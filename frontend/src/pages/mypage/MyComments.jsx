import React, { useEffect, useState } from 'react';
import api from '../../api/axios';
import { Link } from 'react-router-dom'; // 게시글 상세 페이지로 이동할 수 있게끔 Link를 가져온다
import styles from '../../styles/MyComments.module.scss';

const MyComments = () => {
    const [comments, setComments] = useState([]);

    useEffect(() => {
        // api.get('/api/accounts/my_comments/')
        api.get('api/mypage/my-comments/')
        .then(res => {
            setComments(res.data); })
        .catch(err => console.error('내 댓글을 불러오는데 실패했습니다:', err));
    }, []);

  return (
    <div className={styles.container}>
      <h3 className={styles.heading}>작성 댓글</h3>
      <ul className={styles.commentList}>
        {comments.map(comment => (
          <li key={comment.id}>
        <Link to={`/posts/${comment.post}`} className={styles.commentItem}>
        <div className={styles.content}>{comment.content}</div>
        <div className={styles.meta}>
            <div className={styles.meta}> {comment.created_at.slice(0, 10)} 게시글: {comment.post_title}</div>
        </div>
        </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MyComments;
