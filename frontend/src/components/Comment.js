import React, { useState } from "react";
import api from "../api/axios";
import { useRecoilValue } from "recoil";
import { userState, blockedUserIdState } from "../recoil/atoms";
import styles from '../styles/Comment.module.scss';
import { Link } from "react-router-dom";


export default function Comment({ comment, refreshComments }) {
  const user = useRecoilValue(userState);
  const blockedUserIds = useRecoilValue(blockedUserIdState);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(comment.content);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState("");
  const [showReportForm, setShowReportForm] = useState(false); // 신고 폼 열기
  const [reportReason, setReportReason] = useState(""); // 사유

  const isAuthor = user?.id === comment.user;
  const isBlocked = blockedUserIds.includes(comment.user);

  const handleEditSubmit = async () => {
    try {
      await api.patch(`/api/posts/${comment.post}/comments/${comment.id}/`, { content: editedContent });
      setIsEditing(false);
      refreshComments();
    } catch (err) {
      console.error(err);
      alert("댓글 수정 실패");
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("정말 삭제하시겠습니까?")) return;
    try {
      await api.delete(`/api/posts/${comment.post}/comments/${comment.id}/`);
      refreshComments();
    } catch (err) {
      console.error(err);
      alert("댓글 삭제 실패");
    }
  };

  const handleReplySubmit = async () => {
    try {
      await api.post(`/api/posts/${comment.post}/comments/`, {
        content: replyContent,
        parent: comment.id,
      });
      setReplyContent("");
      setShowReplyForm(false);
      refreshComments();
    } catch (err) {
      console.error(err);
      alert("답글 작성 실패");
    }
  };

  const handleReportSubmit = async () => {
  if (!reportReason.trim()) {
    alert("신고 사유를 입력해주세요.");
    return;
  }

  try {
    await api.post("/api/reports/comment-reports/", {
      comment: comment.id,
      reason: reportReason,
    });
    alert("댓글이 신고되었습니다.");
    setShowReportForm(false);
    setReportReason("");
  } catch (err) {
    if (
      err.response?.status === 400 &&
      err.response.data?.detail === "이미 신고하셨습니다."
    ) {
      alert("이미 신고한 댓글입니다.");
    } else {
      console.error(err);
      alert("신고 중 오류가 발생했습니다.");
    }
  }
};


return (
  <div className={`${styles.comment} ${comment.parent ? styles.reply : ''}`}>
    {isEditing ? (
      <>
        <div className={styles.textareaWrapper}>
          <textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            rows={3}
          />
          <button onClick={handleEditSubmit}>저장</button>
          <button onClick={() => setIsEditing(false)}>취소</button>
        </div>
      </>
    ) : (
      <>
          {isBlocked ? (
            <>
              <Link to={`/profile/${comment.author_username}`} className={styles.author}>
                {comment.author_username}
              </Link>
            <div className={styles.blocked}>차단한 유저의 댓글입니다</div>
            </>
          ) : (
            <>
          <Link to={`/profile/${comment.author_username}`} className={styles.author}>
            {comment.author_username}
          </Link>
        <div className={styles.content}>
          {comment.is_deleted ? (
            <span className={styles.deleted}>삭제된 댓글입니다.</span>
          ) : (
            comment.content
          )}
        </div>
        <div className={styles.meta}>
          {new Date(comment.created_at).toLocaleString("ko-KR")}
        </div>

        <div className={styles.buttons}>
          {!comment.is_deleted && isAuthor && (
            <>
              <button onClick={() => setIsEditing(true)}>수정</button>
              <button onClick={handleDelete}>삭제</button>
            </>
          )}
          {!comment.is_deleted && (
            <button onClick={() => setShowReplyForm(!showReplyForm)}>답글</button>
          )}
          {!comment.is_deleted && (
            <button onClick={() => setShowReportForm(!showReportForm)}>신고</button>
          )}
        </div>
      </>
    )}
    </>
    )}
        {!isBlocked && showReportForm && (
          <div className={styles.textareaWrapper}>
            <textarea
              rows={2}
              value={reportReason}
              onChange={(e) => setReportReason(e.target.value)}
              placeholder="신고 사유를 입력하세요"
            />
            <button onClick={handleReportSubmit}>신고 제출</button>
          </div>
          )}


        {!isBlocked && showReplyForm && (
          <div className={styles.textareaWrapper}>
            <textarea
              rows={2}
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              placeholder="답글을 입력하세요"
            />
            <button onClick={handleReplySubmit}>등록</button>
          </div>
        )}

        {comment.replies?.map((child) => (
          <Comment key={child.id} comment={child} refreshComments={refreshComments} />
        ))}
      </div>
      );
    }

