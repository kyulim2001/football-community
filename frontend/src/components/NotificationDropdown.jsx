// src/components/NotificationDropdown.jsx
import React, { useEffect, useState, useRef } from 'react';
import styles from '../styles/NotificationDropdown.module.scss';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';
import { HiOutlineBell } from 'react-icons/hi';
import { AiFillHeart} from 'react-icons/ai';
import { BiMessageRoundedDots } from 'react-icons/bi';

function NotificationDropdown({ reloadTrigger }) {
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const dropdownRef = useRef();

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/api/notifications/');
      const data = res.data;
      if (Array.isArray(data.results)) {
        setNotifications(data.results);
      } else {
        console.warn("❗ 알림 응답이 배열이 아님:", data);
        setNotifications([]);
      }
    } catch (err) {
      console.error('🔔 알림 불러오기 실패', err);
      setNotifications([]);
    }
  };

  const unreadCount = Array.isArray(notifications) ? notifications.filter(n => !n.is_read).length : 0;

  const toggleDropdown = () => {
    setIsOpen(prev => !prev);
  };

  const timeAgo = (timestamp) => {
  const now = new Date();
  const created = new Date(timestamp);
  const diffMs = now - created;
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return '방금 전';
  if (diffMins < 60) return `${diffMins}분 전`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}시간 전`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}일 전`;
};

  const handleClickOutside = (e) => {
    if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
      setIsOpen(false);
    }
  };

  const handleClickNotification = async (notification) => {
    try {
      await api.patch(`/api/notifications/${notification.id}/mark-read/`);

      // ✅ 읽음 상태 업데이트 (프론트)
      setNotifications(prev =>
        prev.map(n => n.id === notification.id ? { ...n, is_read: true } : n)
      );

      // ✅ 이동
      let link = '/';
      if (notification.post) {
        link = `/posts/${notification.post}/`;
      } else if (notification.comment) {
        link = `/comments/${notification.comment}/`;
      }
      navigate(link);
    } catch (err) {
      console.error('✅ 알림 읽음 처리 실패', err);
    }
  };

    useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
        fetchNotifications();
    }
    }, [reloadTrigger]);

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
      <div className={styles.wrapper} ref={dropdownRef}>
        <div className={styles.iconWrapper} onClick={toggleDropdown}>
          <HiOutlineBell size={20} />
          {unreadCount > 0 && <span className={styles.badge}>{unreadCount}</span>}
        </div>
        {isOpen && (
          <div className={styles.dropdown}>
            {notifications.length === 0 ? (
              <div className={styles.item}>알림이 없습니다</div>
            ) : (
              notifications.map(n => (
                <div
                  key={n.id}
                  className={`${styles.item} ${!n.is_read ? styles.unread : ''}`}
                  onClick={() => handleClickNotification(n)}
                >
                  <div className={styles.messageRow}>
                    {n.type === 'like' && <AiFillHeart color="red" />}
                    {n.type === 'reply' && <BiMessageRoundedDots />}
                    <span>
                      {n.type === 'like' && `${n.sender}님이 회원님의 게시글을 좋아합니다.`}
                      {n.type === 'comment' && `${n.sender}님이 회원님의 게시글에 댓글을 남겼습니다.`}
                      {n.type === 'reply' && `${n.sender}님이 회원님의 댓글에 답글을 남겼습니다.`}
                    </span>
                  </div>
                  <div className={styles.time}>{timeAgo(n.created_at)}</div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    );
}

export default NotificationDropdown;
