import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import styles from '../../styles/UserPosts.module.scss';

function UserPosts({ nickname }) {
  const [posts, setPosts] = useState([]);

useEffect(() => {
  const encodedNickname = encodeURIComponent(nickname);
  api.get(`/api/accounts/nickname/${encodedNickname}/posts`)
    .then(res => setPosts(res.data.posts))
    .catch(err => console.error(err));
}, [nickname]);

  return (
    <div>
      {posts.map(post => (
        <div key={post.id} className={styles.postItem}>
          <Link to={`/posts/${post.id}`} className={styles.postTitle}>
            {post.title}
          </Link>
          <p className={styles.postDate}>
            작성일: {new Date(post.created_at).toLocaleString('ko-KR')}
          </p>
        </div>
      ))}
    </div>
  );
}

export default UserPosts;
