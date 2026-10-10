import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import LoginForm from './components/LoginForm';
import PrivateRoute from './components/PrivateRoute';
import MyPage from './pages/mypage/MyPage';
import MyPosts from './pages/mypage/MyPosts';
import MyComments from './pages/mypage/MyComments';
import MyLikes from './pages/mypage/MyLikes';
import ChangePassword from './pages/mypage/ChangePassword';
import DeleteAccount from './pages/mypage/DeleteAccount';
import PostList from './pages/PostList';
import PostDetail from './pages/PostDetail';
import MyInfo from './pages/mypage/MyInfo';
import FindIDPage from './pages/FindIDPage';
import FindPasswordPage from './pages/FindPasswordPage';
import SignupForm from './components/SignupForm';
import CreatePostPage from './pages/CreatePostPage';
import EditPostPage from './pages/EditPostPage';
import Home from './pages/home'
import ChatRoom from './pages/chatroom';
import { useSetRecoilState } from 'recoil';
import { userState } from './recoil/atoms';
import { useEffect, useState } from 'react';
import UserProfile from './pages/profile/UserProfile';
import { blockedUserIdState } from './recoil/atoms';
import api from './api/axios';
import { useRecoilState } from 'recoil';

// 전체 웹사이트 페이지 구성과 화면 전환 구조 담당
function App() {
  const [user, setUser] = useRecoilState(userState);
  const [loading, setLoading] = useState(true);
  const setBlockedUserIds = useSetRecoilState(blockedUserIdState);

    useEffect(() => {
    const savedUser = localStorage.getItem('userState');
    const accessToken = localStorage.getItem('accessToken');
    if (savedUser && accessToken) {
      setUser(JSON.parse(savedUser)); // recoil에 로그인 상태 복구
    } else {
      setUser ({ isLoggedIn: false, username: '', nickname: '', id: null});
      localStorage.removeItem('userState');
    }
    setLoading(false);
  }, [setUser]);

    useEffect(() => {
    const fetchBlockedUsers = async () => {
      try {
        const res = await api.get('/api/accounts/blocks/');
        const blockedIds = res.data.results.map(block => block.blocked);
        setBlockedUserIds(blockedIds);
      } catch (error) {
        console.error('차단된 유저 목록 불러오기 실패:', error);
        setBlockedUserIds([]); // 실패 시 빈 배열로 초기화
      }
    };
    fetchBlockedUsers();
  }, [setBlockedUserIds]);
  
  if (loading) return null;

  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/find-id" element={<FindIDPage />} />
          <Route
            path="/posts/create"
            element={<PrivateRoute><CreatePostPage /></PrivateRoute>}
          />
          <Route
            path="/board/:league/create"
            element={<PrivateRoute><CreatePostPage /></PrivateRoute>}
          />
          <Route
            path="/posts/:id/edit"
            element={<PrivateRoute><EditPostPage /></PrivateRoute>}
          />
        <Route path="/find-password" element={<FindPasswordPage />} />
        <Route path="/signup" element={<SignupForm />} />
        <Route path="/chat" element={<ChatRoom />} />
        <Route path="/board/:league" element={<PostList  />} />
        <Route path="/posts/:id" element={<PostDetail />} />
        <Route path="/profile/:userId" element={<UserProfile />} />
        <Route path="/" element={<Home />} />
        <Route
            path="/mypage"
            element={
              <PrivateRoute>
                <MyPage />
              </PrivateRoute>
            } // 마이페이지와 그 하위경로들은 로그인한 사용자만 접근 가능하게끔
        > 
        <Route path="posts" element={<MyPosts />} />
        <Route path="comments" element={<MyComments />} />
        <Route path="likes" element={<MyLikes />} />
        <Route path="password" element={<ChangePassword />} />
        <Route path="delete" element={<DeleteAccount />} />
        <Route path="info" element={<MyInfo />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
