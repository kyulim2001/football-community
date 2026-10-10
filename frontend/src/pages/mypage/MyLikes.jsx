import React, { useEffect, useState } from 'react'; // useeffect(컴포넌트가 화면에 처음 나타났을 때 실행되는 코드 작성용), usestate(화면에 보여줄 데이터를 저장하고 업뎃)
import api from '../../api/axios'; // api 호출을 위해 커스텀 api 인스턴스를 불러옴
import { Link } from 'react-router-dom';
import styles from '../../styles/MyLikes.module.scss';

const MyLikes = () => {
    const [likedPosts, setLikedPosts] = useState([]);

    useEffect(() => {
        // api.get('/api/accounts/liked_posts/')
        api.get('/api/mypage/liked-posts/')
        .then(res => setLikedPosts(res.data))
        .catch(err => console.error('좋아요한 글을 불러오는데 실패했습니다:', err))
    }, []);

    return (
        <div className={styles.container}>
        <h3 className={styles.heading}>좋아요한 글</h3>
        <ul className={styles.postList}>
            {likedPosts.map((post) => (
            <li key={post.id}>
                <Link to={`/posts/${post.id}`} className={styles.postItem}>
                <div className={styles.title}>{post.title}</div>
                <div className={styles.meta}>
                    {post.created_at.slice(0, 10)} · 조회수 {post.views}
                </div>
                </Link>
            </li>
            ))}
        </ul>
        </div>
    );
    };
export default MyLikes;