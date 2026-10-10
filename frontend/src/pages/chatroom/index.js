import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useRecoilValue } from 'recoil';
import { userState } from '../../recoil/atoms';
import api from '../../api/axios';



const ChatRoom = () => {
  const socketRef = useRef(null);
  const [message, setMessage] = useState('');
  const [chatLog, setChatLog] = useState([]);
  const roomName = 'room1';
  const chatBoxRef = useRef(null);
  const user = useRecoilValue(userState);

  // 기존 채팅 메시지 불러오기 (처음 렌더링될 때만)
  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const res = await api.get(`/api/chat/messages/room/${roomName}/`);
        const messages = res.data.map(msg => ({
          username: msg.username,
          text: msg.message,
          time: new Date(msg.timestamp).toLocaleTimeString()
        }));
        setChatLog(messages);
      } catch (err) {
        console.error('채팅 메시지 불러오기 실패:', err);
      }
    };

    fetchMessages();
  }, [roomName]);

  // WebSocket 연결
  useEffect(() => {
    const ws = new WebSocket(`${process.env.REACT_APP_WS_URL || `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`}/ws/chat/${roomName}/`);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket 연결 성공');
    };

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      const newMsg = {
        username: data.username || '익명',
        text: data.message || '',
        time: new Date().toLocaleTimeString(),
      };

      setChatLog(prev => [...prev, newMsg]);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };

    return () => {
      ws.close();
    };
  }, [user]);

  // 자동 스크롤
  useEffect(() => {
    chatBoxRef.current?.scrollTo(0, chatBoxRef.current.scrollHeight);
  }, [chatLog]);

  // 메시지 전송
  const handleSend = useCallback(() => {
    const socket = socketRef.current;

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        message: message,
        username: user.nickname || '익명'
      }));
      setMessage('');
    } else {
      console.warn('WebSocket이 닫혀 있어서 메시지를 보낼 수 없습니다.');
    }
  }, [message, user]);

  return (
    <div style={{ padding: '20px' }}>
      <h2>채팅</h2>
      <div
        ref={chatBoxRef}
        style={{
          border: '1px solid #ccc',
          padding: '10px',
          height: '200px',
          overflowY: 'scroll',
          marginBottom: '10px',
        }}
      >
        {chatLog.map((msg, idx) => (
          <div key={idx}>
            <strong>{msg.username}</strong> [{msg.time}]: {msg.text}
          </div>
        ))}
      </div>
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleSend();
        }}
        placeholder="메시지를 입력하세요"
        style={{ marginRight: '8px', padding: '6px', width: '60%' }}
      />
      <button onClick={handleSend}>전송</button>
    </div>
  );
};

export default ChatRoom;
