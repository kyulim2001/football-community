import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from '../../api/axios';
import styles from '../../styles/Home.module.scss';
import { useRecoilValue } from 'recoil';
import { blockedUserIdState } from "../../recoil/atoms";

const Home = () => {
  const [popularPosts, setPopularPosts] = useState([]);
  const [search, setSearch] = useState('');
  const [scope, setScope] = useState('title_content');
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);

  const blockedUserIds = useRecoilValue(blockedUserIdState);

  const formatDate = (datetime) => {
    const created = new Date(datetime);
    const now = new Date();
    const isToday = created.toDateString() === now.toDateString();
    return isToday
      ? created.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit", hour12: false })
      : `${created.getMonth() + 1}-${created.getDate()}`;
  };

  const fetchPopularPosts = async () => {
    try {
      const res = await api.get(`/api/posts/popular/?search=${search}&scope=${scope}&page=${page}`);
      setPopularPosts(res.data.results);
      setCount(res.data.count);
    } catch (err) {
      console.error("인기글 불러오기 실패", err);
    }
  };

  useEffect(() => {
    fetchPopularPosts();
  }, [search, scope, page]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setPage(1); // 검색하면 1페이지부터
    fetchPopularPosts();
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>
        <img src="/assets/icon.png" alt="로고" className={styles.logoImg} /> 인기글
      </h2>

      <form onSubmit={handleSubmit} className={styles.searchBar}>
        <select value={scope} onChange={(e) => setScope(e.target.value)}>
          <option value="title_content">제목+내용</option>
          <option value="title">제목</option>
          <option value="author">작성자</option>
        </select>
          <input
            type="text"
            placeholder="검색어 입력"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit">검색</button>
      </form>
      {/* 게시글 목록 */}
      <ul className={styles.postList}>
        {popularPosts.map((post) => {
          const isBlocked = blockedUserIds.includes(post.user.id);
          return (
            <li key={post.id} className={styles.postItem}>
              <div className={styles.postInfo}>
                {isBlocked ? (
                  <div className={styles.blocked}>차단한 유저의 게시글입니다</div>
                ) : (
                  <Link to={`/posts/${post.id}`} className={styles.titleLink}>
                    <span className={styles.boardTag}>{post.board_name}</span> {post.title}
                  </Link>
                )}
                <div className={styles.meta}>
                  <span className={styles.metaItem}>
                    <Link to={`/profile/${post.user.nickname}`}>{post.user.nickname}</Link>
                  </span>
                  <span className={styles.metaItem}>조회수: {post.views}</span>
                  <span className={styles.metaItem}>좋아요: {post.like_count}</span>
                  <span className={styles.metaItem}>{formatDate(post.created_at)}</span>
                </div>
              </div>
              {!isBlocked && (
                <div className={styles.thumbnailRow}>
                  {post.media?.length > 0 && (
                    <div className={styles.thumbnail}>
                      <img src={post.media[0].file} alt="썸네일" />
                    </div>
                  )}
                  <div className={styles.commentBox}>
                    <div className={styles.commentLabel}>댓글</div>
                    <div className={styles.commentCount}>{post.comment_count}</div>
                  </div>
                </div>
              )}
            </li>
          );
        })}
      </ul>

    <div className={styles.pagination}>
      <button disabled={page === 1} onClick={() => setPage(page - 1)}>
        이전
      </button>
      <span>{page} 페이지</span>
      <button
        disabled={popularPosts.length === 0 || count <= page * 10}
        onClick={() => setPage(page + 1)}
      >
        다음
      </button>
    </div>
  </div>
  );
};

export default Home;
