import React, { useCallback, useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import styles from "../styles/PostList.module.scss";
import { Files, FileImage, FileVideo } from 'lucide-react';
import { useRecoilValue } from 'recoil';
import { blockedUserIdState } from "../recoil/atoms";


const BASE_URL = (process.env.REACT_APP_API_URL || "").replace(/\/$/, "");


function PostList() {
  const { league } = useParams();
  const blockedUserIds = useRecoilValue(blockedUserIdState);

  const leagueToId = {
    "premier-league": 3,
    "la-liga": 4,
    "bundesliga": 5,
    "serie-a": 6,
    "ligue-1": 7,
  };

  const boardId = leagueToId[league];
  const [posts, setPosts] = useState([]);
  const [popularPosts, setPopularPosts] = useState([]);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [count, setCount] = useState(0);
  const [showPopular, setShowPopular] = useState(false); // 탭 상태
  const [searchScope, setSearchScope] = useState("title");

  // 날짜 포맷
  const formatDate = (datetime) => {
    const created = new Date(datetime);
    const now = new Date();
    const isToday =
      created.getFullYear() === now.getFullYear() &&
      created.getMonth() === now.getMonth() &&
      created.getDate() === now.getDate();

    return isToday
      ? created.toLocaleTimeString("ko-KR", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        })
      : `${String(created.getMonth() + 1).padStart(2, "0")}-${String(
          created.getDate()
        ).padStart(2, "0")}`;
  };

    const init = useCallback(() => {
    if (showPopular) return;

    // let url = `${BASE_URL}/posts/?page=${page}&search=${search}`;
    let url = `${BASE_URL}/api/posts/?page=${page}&search=${search}`;
    if (boardId) url += `&board=${boardId}`;
    if (searchScope) url += `&scope=${searchScope}`;

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        setPosts(data.results);
        setCount(data.count);
      })
  }, [page, search, boardId, showPopular, searchScope])

  // 전체 게시글 불러오기
  useEffect(() => {
    init()
  }, [init]);


  // 인기글 불러오기
  useEffect(() => {
    if (!showPopular) return;

    // let url = `${BASE_URL}/posts/popular/`;
    let url = `${BASE_URL}/api/posts/popular/`;
    const queryParams = [];

    if (boardId) queryParams.push(`board=${boardId}`);
    if (search) queryParams.push(`search=${search}`);
    if (searchScope) queryParams.push(`scope=${searchScope}`);

    if (queryParams.length > 0) {
      url += `?${queryParams.join("&")}`;
    }

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        setPopularPosts(data.results);
        setCount(data.count);
      });
  }, [showPopular, boardId, search, searchScope]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    setSearch(e.target.search.value);
  };

  const postListToShow = showPopular ? popularPosts : posts;

return (
    <div className={styles.container}>
      <div className={styles.topBar}>
        <form onSubmit={handleSearch} className={styles.searchForm}>
          <select
            value={searchScope}
            onChange={(e) => setSearchScope(e.target.value)}
            className = {styles.searchScope}
          >
            <option value="title">제목</option>
            <option value="title_content">제목+내용</option>
            <option value="author">글쓴이</option>
          </select>
          <input name="search" placeholder="검색어 입력" className={styles.searchInput} />
          <button type="submit" className={styles.searchButton}>검색</button>
        </form>

  <Link to={`/board/${league}/create`}>
    <button>글쓰기</button>
  </Link>
</div>

      <div className={styles.tabs}>
        <div
          onClick={() => setShowPopular(false)}
          className={!showPopular ? styles.active : ""}
        >
          전체 글
        </div>
        <div
          onClick={() => setShowPopular(true)}
          className={showPopular ? styles.active : ""}
        >
          인기글
        </div>
      </div>

      <h2>
        {showPopular ? (
          <>
            <img src="/assets/icon.png" alt="로고" className={styles.logoImg} />
            인기글
          </>
        ) : (
          "전체 게시글"
        )}
      </h2>

      <ul className={styles.list}>
        <li className={styles.headerRow}>
          <div className={styles.title}>제목</div>
          <div className={styles.nickname}>작성자</div>
          <div className={styles.date}>작성일</div>
          <div className={styles.views}>조회수</div>
          <div className={styles.likes}>좋아요</div>
        </li>

    {postListToShow.map((post) => {
      const isBlocked = blockedUserIds.includes(post.user.id);

      return (
        <li key={post.id} className={styles.row}>
          <div className={styles.title}>
            {isBlocked ? (
              <span className={styles.blocked}>차단한 유저의 게시글입니다</span>
            ) : (
              <Link to={`/posts/${post.id}`}>{post.title}</Link>
            )}
            {(post.has_image || post.has_video) && !isBlocked && (
              <span className={styles.mediaBadge}>
                {post.has_image && post.has_video ? (
                  <Files size={14} />
                ) : post.has_image ? (
                  <FileImage size={14} />
                ) : (
                  <FileVideo size={14} />
                )}
              </span>
            )}
            {!isBlocked && <span className={styles.commentCount}>[{post.comment_count}]</span>}
          </div>

          <div className={styles.nickname}>
            <Link to={`/profile/${post.user.nickname}`}>{post.user.nickname}</Link>
          </div>
          <div className={styles.date}>{formatDate(post.created_at)}</div>
          <div className={styles.views}>{post.views}</div>
          <div className={styles.likes}>{post.like_count}</div>
        </li>
      );
    })}

      </ul>

      {!showPopular && (
        <div className={styles.pagination}>
          <button disabled={page === 1} onClick={() => setPage(page - 1)}>
            이전
          </button>
          <span>{page} 페이지</span>
          <button
            disabled={posts.length === 0 || count <= page * 10}
            onClick={() => setPage(page + 1)}
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}

export default PostList;