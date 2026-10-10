import React, { useEffect, useState } from 'react';
import api from '../../api/axios'; // 백엔드에 요청을 보내기 위한 http 클라이언트
import {Link} from 'react-router-dom';
import styles from '../../styles/MyPosts.module.scss';

const MyPosts = () => {
    const [posts, setPosts] = useState([]);

    useEffect(() => {
        // api.get('/api/accounts/my_posts/')
        api.get('api/mypage/my-posts/')
            .then(res => {
                setPosts(res.data); })
            .catch(err => console.error("글을 불러오는데 실패했습니다:", err))
    }, []);
    return (
    <div className={styles.container}>
        <h3 className={styles.heading}>작성글</h3>
        <ul className={styles.postList}>
        {posts.map((post) => (
            <li key={post.id} className={styles.postItem}>
            <Link to={`/posts/${post.id}`}>
                <div className={styles.title}>{post.title}</div>
                <div className={styles.meta}>
                {post.created_at.slice(0, 10)} 조회수: {post.views}
                </div>
            </Link>
            </li>
        ))}
        </ul>
    </div>
    );
};

export default MyPosts;