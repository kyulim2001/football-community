import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import styles from '../../styles/UserComments.module.scss';

function UserComments({ nickname }) {
  const [comments, setComments] = useState([]);

    useEffect(() => {
    const encodedNickname = encodeURIComponent(nickname);
    api.get(`/api/accounts/nickname/${encodedNickname}/comments`)
        .then(res => setComments(res.data.comments))
        .catch(err => console.error(err));
    }, [nickname]);

    return (
    <div>
        {comments.map(comment => (
        <div key={comment.id} className={styles.commentItem}>
            {comment.is_deleted ? (
            <span className={styles.deleted}>삭제된 댓글입니다.</span>
            ) : (
            <Link to={`/posts/${comment.post}`} className={styles.commentContent}>
                {comment.content}
            </Link>
            )}
            <p className={styles.commentDate}>
                작성일: {new Date(comment.created_at).toLocaleString('ko-KR')}
            </p>
        </div>
        ))}
    </div>
    );
}

export default UserComments;
