import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import CommentForm from "../components/CommentForm";
import api from '../api/axios';
import { useRecoilValue } from 'recoil';
import { userState } from '../recoil/atoms';
import Comment from "../components/Comment";
import styles from '../styles/PostDetail.module.scss';
import { useSetRecoilState } from 'recoil';
import { notificationReloadState } from '../recoil/notificationAtom';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import voteStyles from '../styles/VoteButtons.module.scss';

function PostDetail() {
  const { id, league } = useParams();
  const navigate = useNavigate();
  const user = useRecoilValue(userState);
  const setReload = useSetRecoilState(notificationReloadState);

  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);

  const [showReportForm, setShowReportForm] = useState(false);
  const [reportReason, setReportReason] = useState('');

  const handleNewComment = (newComment) => {
    setComments([newComment, ...comments]);
  };

  const getPost = async () => {
    try {
      const res = await api.get(`/api/posts/${id}/`);
      setPost(res.data);
      console.log("게시글 데이터:", res.data);
    } catch (err) {
      console.error("게시글 정보 가져오기 실패", err);
    }
  };

  const getComments = async () => {
    try {
      const res = await api.get(`/api/posts/${id}/comments/`);
      setComments(res.data.results);
    } catch (err) {
      console.error("댓글 목록 가져오기 실패", err);
    }
  };

  const handleLike = async () => {
    try {
      const res = await api.post(`/api/posts/${id}/like/`);
      setReload(prev => prev + 1);
      alert(res.data.detail);
      await getPost();
    } catch (err) {
      console.error(err);
      alert('좋아요 실패');
    }
  };

  const handleDislike = async () => {
    try {
      const res = await api.post(`/api/posts/${id}/dislike/`);
      alert(res.data.detail);
      await getPost();
    } catch (err) {
      console.error(err);
      alert('싫어요 실패');
    }
  };

  const handleDelete = async () => {
    if (!user.isLoggedIn) {
      alert("로그인이 필요합니다.");
      return;
    }

    if (user.id !== post.user.id) {
      alert("작성자만 삭제할 수 있습니다.");
      return;
    }

    if (!window.confirm("정말 삭제하시겠습니까?")) return;

    try {
      await api.delete(`/api/posts/${id}/`);
      alert("게시글이 삭제되었습니다.");
      navigate(`/board/${league}`);
    } catch (err) {
      console.error(err);
      alert("삭제 실패");
    }
  };

  const handleEdit = () => {
    if (!user.isLoggedIn) {
      alert("로그인이 필요합니다.");
      return;
    }

    if (user.id !== post.user.id) {
      alert("작성자만 수정할 수 있습니다.");
      return;
    }

    navigate(`/posts/${id}/edit`);
  };
  
  const handleReportSubmit = async () => {
    if (!reportReason.trim()) {
      alert('신고 사유를 입력해주세요.');
      return;
    }

    try {
      await api.post('/api/reports/post-reports/', {
        post: post.id,
        reason: reportReason
      });
      alert('신고가 접수되었습니다.');
      setShowReportForm(false);
      setReportReason('');
    } catch (err) {
      if (err.response?.status === 400 && err.response.data?.detail === '이미 신고하셨습니다.') {
        alert('이미 신고한 게시글입니다.');
      } else {
        alert('신고 처리 중 오류가 발생했습니다.');
        console.error(err);
      }
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    getPost();
    getComments();
  }, [id]);

  if (!post) return <div>불러오는 중...</div>;

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>{post.title}</h2>

      <div className={styles.meta}>
        <span>작성자:<Link to={`/profile/${post.user.nickname}`} className={styles.nicknameLink}>{post.user.nickname}</Link></span>
        <span>작성일: {new Date(post.created_at).toLocaleString("ko-KR")}</span>
        <span>조회수: {post.views}</span>
      </div>

      <div className={styles.content}>{post.content}</div>

      {post.media && post.media.length > 0 && (
        <div className={styles.media}>
          {post.media.map((item) => (
            <div key={item.id}>
              {item.file.endsWith('.mp4') ? (
                <video src={item.file} controls />
              ) : (
                <img src={item.file} alt="첨부 이미지" />
              )}
            </div>
          ))}
        </div>
      )}

      <div className={voteStyles.actions}>
          <button
            onClick={handleLike}
            className={`${voteStyles.voteBtn} ${post.is_liked ? voteStyles.active : ''}`}
          >
          <ThumbsUp size={18} />
          {post.like_count}
        </button>

        <button
          onClick={handleDislike}
          className={`${voteStyles.voteBtn} ${post.is_disliked ? voteStyles.active : ''}`}
        >
          <ThumbsDown size={18} />
          {post.dislike_count}
        </button>
        <button onClick={handleDelete} className={voteStyles.utilityBtn}>삭제</button>
        <button onClick={handleEdit} className={voteStyles.utilityBtn}>수정</button>
        <button onClick={() => setShowReportForm(!showReportForm)} className={voteStyles.utilityBtn}>
          신고
        </button>
      </div>

      {showReportForm && (
        <div className={styles.reportForm}>
          <textarea
            value={reportReason}
            onChange={(e) => setReportReason(e.target.value)}
            placeholder="신고 사유를 입력하세요"
            rows={3}
          />
          <button onClick={handleReportSubmit} className={voteStyles.utilityBtn}>
            신고 제출
          </button>
        </div>
      )}


      <div className={styles.commentSection}>
        <h3>댓글</h3>
        <CommentForm postId={id} onCommentAdded={handleNewComment} />
        <div>
          {comments
            .filter((comment) => comment.parent === null)
            .map((comment) => (
              <Comment
                key={comment.id}
                comment={comment}
                refreshComments={getComments}
              />
            ))}
        </div>
      </div>
    </div>
  );
}

export default PostDetail;