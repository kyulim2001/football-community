// src/components/PopularPosts.js
import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from '../api/axios';
import styles from '../styles/PopularPosts.module.scss';

export default function PopularPosts() {
  const { league } = useParams();  // 게시판일 경우 리그를 가져옴
  const leagueToId = {
    "premier-league": 3,
    "la-liga": 4,
    "bundesliga": 5,
    "serie-a": 6,
    "ligue-1": 7,
  };
  const boardId = leagueToId[league];

  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const url = boardId
      ? `/api/posts/popular/?board=${boardId}`
      : `/api/posts/popular/`;

    api.get(url)
      .then(res => setPosts(res.data))
      .catch(err => console.error("🔥 인기글 불러오기 실패:", err));
  }, [boardId]);

  return (
    <div className={styles.container}>
      <h3>{boardId ? "이 게시판의 인기글 👑" : "전체 인기글 👑"}</h3>
      <ul>
        {posts.map((post) => (
          <li key={post.id}>
            <Link to={`/posts/${post.id}`}>{post.title}</Link>{" "}
            <small>({post.like_count}❤)</small>
          </li>
        ))}
      </ul>
    </div>
  );
}
